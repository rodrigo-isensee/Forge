#!/usr/bin/env python3
"""Catraca anti-piora do Forge (ADR 0008, seção 3): barra, para todos inclusive o dono, a mudança que piora a fábrica.

Só biblioteca padrão. Lê a base com `git show <base>:<arquivo>` (a base efetiva é o merge-base com o HEAD).
Exceção estreita: PR de `dependabot[bot]` que só troca SHA de `uses:` em workflows passa sem rótulo e sem parecer.
Modos (`--modo`): `regras` (padrão), `pr-texto` (corpo do PR em $PR_BODY) e `pareceres`.
Exceção única das regras (menos `R-CUSTO`, que só tem `custo_permitido`): rótulo `afrouxa-regra` aplicado pelo `dono` (de tests/config.json da base) depois do
último push. Eventos vêm da API do GitHub com $GITHUB_TOKEN (somente leitura); sem token, sem $HEAD_SHA ou sem execução
do head no servidor, vale como sem rótulo. Cada violação: `<R-ID>: <o quê>. Por quê: <motivo>. Corrigir: <ação> (<doc>)`.
"""
import argparse
import ast
import hashlib
import importlib.util
import itertools
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from neutralidade import normalizar  # noqa: E402

ROTULO = "afrouxa-regra"
ADR = "docs/adr/0008-governanca-de-contribuicoes.md"
PROTEGIDOS = (".github/workflows/", ".github/rulesets/", ".github/CODEOWNERS", ".github/dependabot.yml", ".githooks/", "tests/catraca.py")
SENSIVEIS = ("hooks/", "bin/", "scripts/", "migrations/", ".github/workflows/", "tests/catraca.py")
PASTAS_CUSTO = ("hooks/", "bin/", "scripts/", ".github/")
CUSTO = {
    "chave-de-api": r"ANTHROPIC_API_KEY",
    "claude-plugin-eval": r"claude\s+plugin\s+eval",
    "claude-print": r"\bclaude\s+(?:-p|--print)\b",
    "url-de-api-paga": r"api\.anthropic\.com|api\.openai\.com",
    "segredo-do-workflow": r"\bsecrets\b(?!\.GITHUB_TOKEN\b)",  # cobre secrets.X, secrets[..], tojson(secrets), secrets: inherit
}


def msg(rid, oque, porque, corrigir, doc):
    return f"{rid}: {oque}. Por quê: {porque}. Corrigir: {corrigir} ({doc})"


def git(raiz, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, env=env, timeout=60)
    return r.returncode, r.stdout


def ler(raiz, ref, caminho):
    cod, saida = git(raiz, "show", f"{ref}:{caminho}")
    return None if cod else saida


def listar(raiz, ref, prefixo):
    cod, saida = git(raiz, "ls-tree", "-r", "--name-only", ref, prefixo)
    return [] if cod else saida.splitlines()


def json_de(raiz, ref, caminho):
    texto = ler(raiz, ref, caminho)
    try:
        return None if texto is None else json.loads(texto)
    except ValueError:
        return {}


def alterados(raiz, base, head):
    """Caminhos tocados entre base e head. `--no-renames`: mover ou apagar conta como mudança do caminho antigo também."""
    cod, saida = git(raiz, "diff", "--no-renames", "--name-only", "-z", base, head)
    return [] if cod else [a for a in saida.split("\0") if a]


def base_efetiva(raiz, base, head):
    cod, saida = git(raiz, "merge-base", base, head)
    return saida.strip() if not cod and saida.strip() else base


# --- Regras de configuração ------------------------------------------------------------------------------
def _prefixo(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:8]


def _chave(e):
    return (e.get("tipo"), json.dumps(e.get("n")), e.get("sha256"))


def entradas_da_regex(regex):
    """Entradas de `termos_proibidos_hash` que cobrem uma regex em claro da base, ou None se a regex não é simples.

    Só entende o que a lista antiga usava: literal, `\\bliteral\\b`, classes `[abc]` e `parte1 ?parte2`. Em memória; nada é impresso.
    """
    forma = normalizar(regex)
    if re.search(r"[().*+|{}^$]", forma.replace("\\b", "")) or "\\" in forma.replace("\\b", ""):
        return None
    sha = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
    if " ?" in forma:
        p1, _, p2 = forma.partition(" ?")
        if any(c in x for x in (p1, p2) for c in "[]? \\") or not p1 or not p2:
            return None
        return [{"tipo": "par", "n": [len(p1), len(p2)], "sha256": sha(p1 + p2)},
                {"tipo": "trecho", "n": len(p1 + p2), "sha256": sha(p1 + p2)}]
    palavra = forma.startswith("\\b") and forma.endswith("\\b") and len(forma) > 4
    corpo = forma[2:-2] if palavra else forma
    if "\\b" in corpo or "?" in corpo or " " in corpo or not corpo:
        return None
    partes = re.split(r"\[([^\]]+)\]", corpo)  # texto, classe, texto, classe, ...
    if any("[" in x or "]" in x for x in partes[::2]):
        return None
    formas = ["".join(c) for c in itertools.product(*[[x] if i % 2 == 0 else list(x) for i, x in enumerate(partes)])]
    return [{"tipo": "palavra" if palavra else "trecho", "n": len(f), "sha256": sha(f)} for f in formas]


def regra_termos_proibidos(b, h):
    """Nada de nome em claro nas mensagens: só índice e prefixo do hash. Transição claro -> hash só se a nova lista cobrir tudo."""
    v, ids = [], {_chave(e) for e in h.get("termos_proibidos_hash", [])}
    por = "a lista impede que dados de projeto vazem para a fábrica"
    for i, e in enumerate(b.get("termos_proibidos_hash", []), 1):
        if _chave(e) not in ids:
            v.append(msg("R-NEUTRO", f"termo nº {i} (sha256 {str(e.get('sha256'))[:8]}…) removido ou alterado em termos_proibidos_hash",
                         por, "restaure a entrada", "docs/regras/R-NEUTRO.md"))
    claros = h.get("termos_proibidos", [])
    for i, p in enumerate(b.get("termos_proibidos", []), 1):
        if p in claros:
            continue
        cobertura = entradas_da_regex(p)
        if cobertura is None or any(_chave(e) not in ids for e in cobertura):
            v.append(msg("R-NEUTRO", f"termo nº {i} (sha256 {_prefixo(p)}…) removido ou alterado sem cobertura em termos_proibidos_hash",
                         por, "restaure o termo ou inclua as entradas de hash que o cobrem", "docs/regras/R-NEUTRO.md"))
    return v


def regras_de_config(b, h):
    if b is None:
        return []
    v = []
    inv_h = h.get("invariantes", {})
    for arq, pads in b.get("invariantes", {}).items():
        for p in sorted(set(pads) - set(inv_h.get(arq, []))):
            v.append(msg("R-CONFORMIDADE", f"invariante removido de {arq}: {p}",
                         "os trechos de `invariantes` protegem as regras da fábrica",
                         f"restaure o padrão ou peça o rótulo `{ROTULO}` ao dono", "docs/regras/R-CONFORMIDADE.md"))
    v += regra_termos_proibidos(b, h)
    nb, nh = b.get("neutralidade_nucleo", {}), h.get("neutralidade_nucleo", {})
    for p in sorted(set(nb.get("termos", [])) - set(nh.get("termos", []))):
        v.append(msg("R-NEUTRO", f"termo de neutralidade removido ou alterado: {p}", "o núcleo não pode citar stack ou projeto",
                     "restaure o termo", "docs/regras/R-NEUTRO.md"))
    for p in sorted(set(nb.get("pastas", [])) - set(nh.get("pastas", []))):
        v.append(msg("R-NEUTRO", f"pasta saiu da checagem de neutralidade: {p}", "pasta fora da lista não é verificada",
                     "restaure a pasta", "docs/regras/R-NEUTRO.md"))
    for p in sorted(set(nh.get("ignorar", [])) - set(nb.get("ignorar", []))):
        v.append(msg("R-NEUTRO", f"nova pasta ignorada pela neutralidade: {p}", "ignorar uma pasta afrouxa a regra",
                     "remova o item", "docs/regras/R-NEUTRO.md"))
    exc_b = {(a, p) for a, ps in nb.get("excecoes", {}).items() for p in ps}
    for a, p in sorted({(a, p) for a, ps in nh.get("excecoes", {}).items() for p in ps} - exc_b):
        v.append(msg("R-NEUTRO", f"exceção nova de neutralidade em {a}: {p}", "exceção afrouxa a regra",
                     "remova a exceção ou peça o rótulo ao dono", "docs/regras/R-NEUTRO.md"))
    ab, ah = b.get("anti_duplicacao", {}), h.get("anti_duplicacao", {})
    for e in sorted(set(map(str, ah.get("excecoes", []))) - set(map(str, ab.get("excecoes", [])))):
        v.append(msg("R-CONFORMIDADE", f"exceção nova de anti-duplicação: {e[:60]}", "exceção permite regra repetida fora do texto único",
                     "remova a exceção ou peça o rótulo ao dono", "docs/regras/R-CONFORMIDADE.md"))
    if "palavras" in ab and "palavras" not in ah:
        v.append(msg("R-CONFORMIDADE", "anti_duplicacao.palavras removido", "sem a chave a detecção deixa de valer",
                     "restaure a chave", "docs/regras/R-CONFORMIDADE.md"))
    elif ah.get("palavras", 0) > ab.get("palavras", 0):
        v.append(msg("R-CONFORMIDADE", "anti-duplicação exige mais palavras iguais", "trecho menor passa a não ser detectado",
                     "volte ao valor anterior", "docs/regras/R-CONFORMIDADE.md"))
    for p in sorted(set(ab.get("pastas", [])) - set(ah.get("pastas", []))):
        v.append(msg("R-CONFORMIDADE", f"pasta saiu da anti-duplicação: {p}", "pasta fora da lista não é verificada",
                     "restaure a pasta", "docs/regras/R-CONFORMIDADE.md"))
    lh = h.get("limite_linhas", {})
    for k, n in b.get("limite_linhas", {}).items():
        if k not in lh:
            v.append(msg("R-CONFORMIDADE", f"limite_linhas.{k} removido", "sem a chave o limite deixa de valer",
                         "restaure a chave", "docs/engineering/praticas.md"))
        elif lh[k] > n:
            v.append(msg("R-CONFORMIDADE", f"limite_linhas.{k} subiu de {n} para {lh[k]}", "o limite mantém agentes e skills curtos",
                         "reduza o arquivo em vez de subir o limite", "docs/engineering/praticas.md"))
    if "dono" in b and b["dono"] != h.get("dono"):
        v.append(msg("R-CONTRIB", "a chave `dono` mudou", "o dono é quem libera exceções e mescla na main",
                     f"restaure `dono` ou peça o rótulo `{ROTULO}` ao dono", ADR))
    perm_b = {(a, p) for a, ps in b.get("custo_permitido", {}).items() for p in ps}
    for a, p in sorted({(a, p) for a, ps in h.get("custo_permitido", {}).items() for p in ps} - perm_b):
        v.append(msg("R-CUSTO", f"permissão nova de custo em {a}: {p}", "a lista de permissão abre brecha para gasto",
                     "remova o item ou peça o rótulo ao dono", "docs/regras/R-CUSTO.md"))
    return v


def chaves_de_hooks(texto):
    try:
        dados = json.loads(texto) if texto else {}
    except ValueError:
        return set()
    chaves = set()
    for evento, grupos in (dados.get("hooks") or {}).items():
        for g in grupos:
            for hk in g.get("hooks", []):
                chaves.add((evento, g.get("matcher", ""), hk.get("command", ""), " ".join(hk.get("args", []))))
    return chaves


def regra_hooks(raiz, b, h):
    antes = ler(raiz, b, "hooks/hooks.json")
    if antes is None:
        return []
    depois = ler(raiz, h, "hooks/hooks.json") or ""
    return [msg("R-CONFORMIDADE", f"hook removido de hooks/hooks.json: {ev} {mt or '*'} {ar or cm}",
                "hook é o que faz a regra valer sem depender de memória", "restaure o hook ou peça o rótulo ao dono",
                "docs/regras/R-CONFORMIDADE.md")
            for ev, mt, cm, ar in sorted(chaves_de_hooks(antes) - chaves_de_hooks(depois))]


def contar_testes(raiz, ref):
    testes = fixtures = 0
    for arq in listar(raiz, ref, "tests"):
        if arq.startswith("tests/hooks/"):
            fixtures += 1
        if arq.endswith(".py"):
            try:
                arvore = ast.parse(ler(raiz, ref, arq) or "")
            except SyntaxError:
                continue
            testes += sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")
                          for n in ast.walk(arvore))
    return testes, fixtures


def regra_testes(raiz, b, h):
    (tb, fb), (th, fh) = contar_testes(raiz, b), contar_testes(raiz, h)
    v = []
    if th < tb:
        v.append(msg("R-CONFORMIDADE", f"testes `test_*` caíram de {tb} para {th}", "teste que some deixa a regra sem proteção",
                     "restaure os testes ou peça o rótulo ao dono", "docs/regras/R-CONFORMIDADE.md"))
    if fh < fb:
        v.append(msg("R-CONFORMIDADE", f"fixtures de tests/hooks caíram de {fb} para {fh}", "fixture que some deixa o hook sem caso de teste",
                     "restaure as fixtures ou peça o rótulo ao dono", "docs/regras/R-CONFORMIDADE.md"))
    return v


PULOS = {"skip", "skipIf", "skipUnless", "expectedFailure", "skipTest"}


def _nome(no):
    return no.attr if isinstance(no, ast.Attribute) else getattr(no, "id", "")


def forca_dos_testes(raiz, ref):
    """(asserções, pulos, testes vazios) somados em tests/**/*.py, exceto a própria catraca (AST, sem executar nada)."""
    asserts = pulos = vazios = 0
    for arq in listar(raiz, ref, "tests"):
        if not arq.endswith(".py") or arq == "tests/catraca.py":
            continue
        try:
            arvore = ast.parse(ler(raiz, ref, arq) or "")
        except SyntaxError:
            continue
        for n in ast.walk(arvore):
            if isinstance(n, ast.Assert):
                asserts += 1
            elif isinstance(n, ast.Call):
                nome = _nome(n.func)
                asserts += nome.startswith("assert") and nome != "assert"
                pulos += nome in PULOS
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                pulos += sum(_nome(d.func if isinstance(d, ast.Call) else d) in PULOS for d in n.decorator_list)
                corpo = [c for c in n.body if not (isinstance(c, ast.Expr) and isinstance(c.value, ast.Constant))]
                vazios += n.name.startswith("test_") and all(isinstance(c, ast.Pass) for c in corpo)
    return asserts, pulos, vazios


def regra_testes_enfraquecidos(raiz, b, h):
    """Teste existente que perde asserção, ganha skip/expectedFailure ou vira `pass` continua contando em `def test_*`."""
    (ab, pb, vb), (ah, ph, vh) = forca_dos_testes(raiz, b), forca_dos_testes(raiz, h)
    v = []
    for cond, oque in ((ah < ab, f"asserções em tests/ caíram de {ab} para {ah}"),
                       (ph > pb, f"skip/skipIf/skipUnless/expectedFailure em tests/ subiram de {pb} para {ph}"),
                       (vh > vb, f"testes vazios (só `pass`) em tests/ subiram de {vb} para {vh}")):
        if cond:
            v.append(msg("R-CONFORMIDADE", oque, "teste esvaziado ou pulado deixa a regra sem proteção mantendo a contagem de testes",
                         f"restaure as asserções ou peça o rótulo `{ROTULO}` ao dono", "docs/regras/R-CONFORMIDADE.md"))
    return v


def regra_custo(raiz, ref, permitido):
    v = []
    for arq in sorted(a for p in PASTAS_CUSTO for a in listar(raiz, ref, p)):
        texto = ler(raiz, ref, arq)
        if texto is None:
            continue
        for nome, padrao in CUSTO.items():
            if nome == "segredo-do-workflow" and not arq.startswith(".github/workflows/"):
                continue
            if nome in permitido.get(arq, []):
                continue
            m = re.search(padrao, texto, re.I)
            if m:
                linha = texto.count("\n", 0, m.start()) + 1
                v.append(msg("R-CUSTO", f"{nome} em {arq}:{linha}", "nada no Forge pode consumir API paga ou segredo",
                             f"remova o uso, ou inclua `{nome}` para o arquivo em `custo_permitido` com autorização do usuário",
                             "docs/regras/R-CUSTO.md"))
    return v


def regra_protegidos(raiz, b, h):
    if ler(raiz, b, "tests/catraca.py") is None:  # introdução da própria catraca
        return []
    return [msg("R-CONFORMIDADE", f"mudança em {a}", "workflows, rulesets, CODEOWNERS, hooks do git, dependabot e a catraca são os próprios controles",
                f"só passa com o rótulo `{ROTULO}` do dono, aplicado depois do último push", ADR)
            for a in alterados(raiz, b, h) if a.startswith(PROTEGIDOS)]


def regra_arquivos_de_regras(raiz, b, h, cfg_base):
    """Apagar ou mover arquivo com `invariantes` ou de `docs/regras/` tira a regra do alcance dos testes."""
    v = []
    for a in alterados(raiz, b, h):
        if ler(raiz, h, a) is None and ler(raiz, b, a) is not None and (a in cfg_base.get("invariantes", {}) or a.startswith("docs/regras/")):
            v.append(msg("R-CONFORMIDADE", f"arquivo de regra apagado ou movido: {a}", "as regras da fábrica vivem nestes arquivos e os testes os procuram pelo caminho",
                         f"restaure o arquivo ou peça o rótulo `{ROTULO}` ao dono", "docs/regras/R-CONFORMIDADE.md"))
    return v


def violacoes_das_regras(raiz, base, head="HEAD"):
    b = base_efetiva(raiz, base, head)
    cb, ch = json_de(raiz, b, "tests/config.json"), json_de(raiz, head, "tests/config.json")
    permitido = (ch or {}).get("custo_permitido", {})
    return (regras_de_config(cb, ch or {}) + regra_arquivos_de_regras(raiz, b, head, cb or {}) + regra_hooks(raiz, b, head) + regra_testes(raiz, b, head)
            + regra_testes_enfraquecidos(raiz, b, head)
            + regra_custo(raiz, head, permitido) + regra_protegidos(raiz, b, head))


# --- Rótulo do dono ----------------------------------------------------------------------------------------
def instante(texto):
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def rotulo_liberado(eventos, dono, ultimo_push):
    """True se o último evento do rótulo é `labeled` pelo dono e posterior ao último push."""
    ultimo = None
    for e in sorted((e for e in eventos if (e.get("label") or {}).get("name") == ROTULO
                     and e.get("event") in ("labeled", "unlabeled")), key=lambda e: e["created_at"]):
        ultimo = e
    if not ultimo or ultimo["event"] != "labeled" or not dono:
        return False
    return (ultimo.get("actor") or {}).get("login") == dono and instante(ultimo["created_at"]) > instante(ultimo_push)


def api(caminho, token, chave=None):
    """GET paginado; `chave` extrai a lista de uma resposta em objeto (ex.: `workflow_runs`)."""
    itens, pagina = [], 1
    while True:
        req = urllib.request.Request(f"https://api.github.com{caminho}{'&' if '?' in caminho else '?'}per_page=100&page={pagina}",
                                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            lote = json.load(r)
        lote = lote[chave] if chave else lote
        itens += lote
        if len(lote) < 100:
            return itens
        pagina += 1


def eventos_do_github():
    """(eventos, ultimo_push) via API; (None, None) sem token, repositório, número do PR ou HEAD_SHA.

    O "último push" é o instante do servidor em que o head atual apareceu: o `created_at` mais antigo das execuções
    do Actions com `head_sha` igual ao do PR. A data do commit nunca vale (vem do cliente e pode ser forjada).
    Sem execução registrada, `ultimo_push` é None e o rótulo não vale.
    """
    token, repo, numero, head = (os.environ.get(k) for k in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER", "HEAD_SHA"))
    if not (token and repo and numero and head):
        return None, None
    try:
        eventos = api(f"/repos/{repo}/issues/{numero}/events", token)
        execucoes = api(f"/repos/{repo}/actions/runs?head_sha={head}", token, "workflow_runs")
    except (OSError, ValueError, KeyError, TypeError):
        return None, None
    datas = [e["created_at"] for e in execucoes if e.get("head_sha", head) == head and e.get("created_at")]
    return eventos, (min(datas, key=instante) if datas else None)


# --- Outros modos -----------------------------------------------------------------------------------------
def secao(corpo, titulo):
    corpo = re.sub(r"<!--.*?-->", "", corpo or "", flags=re.S)
    m = re.search(rf"^##\s+{re.escape(titulo)}\s*$(.*?)(?=^##\s|\Z)", corpo, re.M | re.S)
    return (m.group(1) if m else "").strip()


MINIMO_SECAO = 20  # caracteres, sem contar comentários HTML (QA BUG-03: "ok" não descreve origem nem medida)


def violacoes_do_texto(corpo):
    return [msg("R-CONTRIB", f"PR sem a seção '{t}' preenchida (mínimo de {MINIMO_SECAO} caracteres fora de comentários)",
                "a origem e a medida da melhoria decidem se ela entra",
                f"preencha '## {t}' no corpo do PR (modelo em .github/pull_request_template.md)", "docs/melhoria-continua.md")
            for t in ("Projeto de origem", "Como medir") if len(secao(corpo, t)) < MINIMO_SECAO]


def forge_check():
    """O `bin/forge-check` ao lado deste script (uma fonte só, ADR 0002): no CI, a versão da base."""
    caminho = Path(__file__).resolve().parent.parent / "bin" / "forge-check"
    loader = SourceFileLoader("forge_check", str(caminho))
    modulo = importlib.util.module_from_spec(importlib.util.spec_from_loader("forge_check", loader))
    loader.exec_module(modulo)
    return modulo


PROMOCOES = {("develop", "homolog"), ("homolog", "main")}  # o parecer é exigido na entrada de cada PR na develop
DEPENDABOT = "dependabot[bot]"
USO_DE_ACAO = re.compile(r"^(\s*(?:-\s*)?uses:\s*[\w./-]+@)[0-9a-f]{40}(\s+#.*)?$")


def so_troca_sha_de_acoes(raiz, b, h):
    """True se o diff só troca o SHA (e o comentário de versão) de linhas `uses:` em workflows."""
    arquivos = alterados(raiz, b, h)
    if not arquivos:
        return False
    for a in arquivos:
        antes, depois = ler(raiz, b, a), ler(raiz, h, a)
        if not a.startswith(".github/workflows/") or antes is None or depois is None or len(antes.splitlines()) != len(depois.splitlines()):
            return False
        for x, y in zip(antes.splitlines(), depois.splitlines()):
            if x != y:
                mx, my = USO_DE_ACAO.match(x), USO_DE_ACAO.match(y)
                if not (mx and my and mx.group(1) == my.group(1)):
                    return False
    return True


def violacoes_de_pareceres(raiz, base, head, ramo, base_ref):
    if (ramo, base_ref) in PROMOCOES:
        return []
    b = base_efetiva(raiz, base, head)
    tocados = [a for a in alterados(raiz, b, head) if a.startswith(SENSIVEIS)]
    if not tocados:
        return []
    fc, achados = forge_check(), []
    for ped in fc.pedidos_da_branch(Path(raiz), ramo, head):
        linhas = [l for l in fc.cmd_pr(Path(raiz), ped, head) if l.strip()]
        if base_ref != "homolog":  # o QA só é exigido na entrada da homolog
            linhas = [l for l in linhas if not l.startswith("docs/qa") and "(R-QA)" not in l]
        if not linhas:
            return []
        achados += linhas
    exige = "review e QA" if base_ref == "homolog" else "review"
    detalhe = f" ({'; '.join(achados[:2])})" if achados else ""
    return [msg("R-REVIEW", f"PR toca {tocados[0]} (e outros {len(tocados) - 1}) sem parecer aprovado de {exige}{detalhe}",
                "código que muda o comportamento dos agentes precisa de revisão antes de entrar",
                f"peça o parecer e confira com `bin/forge-check pr <pedido>` (parecer com `branch: {ramo}`)",
                "docs/regras/R-REVIEW.md")]


def resumo(titulo, linhas):
    saida = os.environ.get("GITHUB_STEP_SUMMARY")
    texto = f"### {titulo}\n" + ("\n".join(f"- {l}" for l in linhas) if linhas else "Sem violações.") + "\n"
    if saida:
        with open(saida, "a", encoding="utf-8") as f:
            f.write(texto)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modo", choices=("regras", "pr-texto", "pareceres"), default="regras")
    ap.add_argument("--base", default=os.environ.get("BASE", "origin/develop"))
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--ramo", default=os.environ.get("HEAD_REF", ""), help="branch do PR (modo pareceres)")
    ap.add_argument("--base-ref", default=os.environ.get("BASE_REF", ""), help="branch de destino (modo pareceres)")
    ap.add_argument("--autor", default=os.environ.get("PR_AUTOR", ""), help="login do autor do PR")
    ap.add_argument("--eventos", help="JSON com os eventos da issue (testes); ignora a API")
    ap.add_argument("--ultimo-push", help="instante ISO do último push (com --eventos)")
    a = ap.parse_args(argv)
    raiz = Path(a.raiz).resolve()
    if a.modo in ("regras", "pareceres") and a.autor == DEPENDABOT and so_troca_sha_de_acoes(raiz, base_efetiva(raiz, a.base, a.head), a.head):
        resumo(a.modo, ["PR do dependabot que só troca SHA de ações em workflows: passa sem rótulo e sem parecer (ADR 0008)"])
        return 0
    if a.modo == "pr-texto":
        viol, titulo = violacoes_do_texto(os.environ.get("PR_BODY", "")), "pr-texto"
    elif a.modo == "pareceres":
        viol, titulo = violacoes_de_pareceres(raiz, a.base, a.head, a.ramo, a.base_ref), "pareceres"
    else:
        viol, titulo = violacoes_das_regras(raiz, a.base, a.head), "catraca"
        if viol:
            if a.eventos:
                eventos, push = json.loads(Path(a.eventos).read_text(encoding="utf-8")), a.ultimo_push
            else:
                eventos, push = eventos_do_github()
            cfg = json_de(raiz, base_efetiva(raiz, a.base, a.head), "tests/config.json") or json_de(raiz, a.head, "tests/config.json") or {}
            custo = [x for x in viol if x.startswith("R-CUSTO:")]  # só `custo_permitido` abre exceção de custo, nunca o rótulo
            if not custo and eventos is not None and push and rotulo_liberado(eventos, cfg.get("dono"), push):
                resumo(titulo, [f"liberado pelo rótulo `{ROTULO}` do dono: {len(viol)} violação(ões) aceita(s)"] + viol)
                print(f"catraca: {len(viol)} violação(ões) liberada(s) pelo rótulo `{ROTULO}` do dono.")
                return 0
    for v in viol:
        print(v)
    resumo(titulo, viol)
    return 1 if viol else 0


if __name__ == "__main__":
    sys.exit(main())
