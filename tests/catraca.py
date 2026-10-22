#!/usr/bin/env python3
"""Catraca anti-piora do Forge (ADR 0008, seção 3): barra, para todos inclusive o dono, a mudança que piora a fábrica.

Só biblioteca padrão. Lê a base com `git show <base>:<arquivo>` (a base efetiva é o merge-base com o HEAD).
Exceção estreita: PR de `dependabot[bot]` que só troca SHA de `uses:` em workflows passa sem rótulo e sem parecer.
Modos (`--modo`): `regras` (padrão), `pr-texto` (corpo do PR em $PR_BODY) e `pareceres`.
Exceção única das regras (menos `R-CUSTO`, que só tem `custo_permitido`): rótulo `afrouxa-regra` aplicado pelo `dono` (de tests/config.json da base) depois do
último push, ou cujo diff efetivo (merge-base, fora dos pareceres dos pedidos desta branch) não mudou desde o rótulo e
cujas violações já existiam no head rotulado. Na promoção (PROMOCOES), também vale o rótulo do dono já posto num PR mesclado
em base..head, só para as violações "mudança em <arquivo>" cujo arquivo tem o mesmo blob e modo do head rotulado (S-16). Com squash
(develop → homolog) o head rotulado vem de `refs/pull/<n>/head`, buscado num namespace próprio (`refs/catraca/pull/<n>`), e vale
o mesmo arquivo no merge e no head rotulado no lugar da ancestralidade (S-16-PROMOCAO-DEVELOP); qualquer falha vale como sem rótulo.
Eventos e execuções vêm da API do GitHub com $GITHUB_TOKEN (somente leitura); sem token, sem $HEAD_SHA ou sem execução
do head no servidor, vale como sem rótulo. Cada violação: `<R-ID>: <o quê>. Por quê: <motivo>. Corrigir: <ação> (<doc>)`.
"""
import argparse
import ast
from collections import Counter
import hashlib
import http.client
import importlib.util
import itertools
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from importlib.machinery import SourceFileLoader
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from neutralidade import normalizar  # noqa: E402

ROTULO = "afrouxa-regra"
ADR = "docs/adr/0008-governanca-de-contribuicoes.md"
PARECERES = ("docs/reviews/", "docs/qa/")  # mudar só o parecer do pedido não muda o conteúdo que o dono viu (o modo `pareceres` o confere)
CURINGA = re.compile(r"[*?\[\]\\]")  # pathspec do git casa curinga: caminho com eles nunca é ignorado
REESCRITA = ("head_ref_force_pushed", "head_ref_deleted", "head_ref_restored")
PROTEGIDOS = (".github/workflows/", ".github/rulesets/", ".github/CODEOWNERS", ".github/dependabot.yml", ".githooks/", "tests/catraca.py",
              "tests/neutralidade.py", "hooks/conformidade.py", "hooks/parecer.py", "hooks/_comum.py", "bin/forge-check",
              "scripts/conferir-release.py")
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
    """Arquivos de `prefixo` em `ref`. Falha fechada: o git que falha levanta `ErroDeGit`, nunca devolve lista vazia."""
    cod, saida = git(raiz, "ls-tree", "-r", "--name-only", ref, prefixo)
    if cod:
        raise ErroDeGit(msg_falha_git(f"o `git ls-tree` de {prefixo} em {ref} falhou"))
    return saida.splitlines()


def existe(raiz, ref, caminho):
    """True se `caminho` existe em `ref`. O `ls-tree` sai 0 sem linha para caminho ausente num commit válido; código diferente
    de 0 é erro do git (levanta `ErroDeGit`), e não "ausente" como no `ler`."""
    cod, saida = git(raiz, "--literal-pathspecs", "ls-tree", "--name-only", ref, "--", caminho)
    if cod:
        raise ErroDeGit(msg_falha_git(f"o `git ls-tree` de {caminho} em {ref} falhou"))
    return bool(saida.strip())


def json_de(raiz, ref, caminho):
    texto = ler(raiz, ref, caminho)
    try:
        return None if texto is None else json.loads(texto)
    except ValueError:
        return {}


class ErroDeGit(Exception):
    """Uma leitura do git de que a decisão depende falhou: erro do git não é "ausente" nem "nada mudou". O texto já é a violação."""


class ErroDeDiff(ErroDeGit):
    """O `git diff` que lista os arquivos alterados falhou: sem a lista, a catraca não pode dizer que nada mudou."""


SEM_LISTA = "não consegui listar os arquivos alterados"
NAO_LIBERAVEL = "o rótulo não libera esta violação"  # marca comum das violações de falha do git (a guarda do rótulo a procura)


def msg_falha_git(detalhe):
    return msg("R-CONFORMIDADE", f"falha do git ao ler o repositório ({detalhe})",
               "sem a leitura a catraca não sabe o que mudou, e tratar o erro como arquivo ausente ou lista vazia deixaria passar a mudança",
               f"confira se a base e o head existem no clone (`git fetch`) e rode de novo; {NAO_LIBERAVEL}", ADR)


def msg_diff(base, head):
    return msg("R-CONFORMIDADE", f"{SEM_LISTA} entre {base} e {head} (o `git diff` falhou)",
               "sem a lista a catraca não sabe o que mudou, e lista vazia deixaria passar mudança em arquivo protegido",
               f"confira se a base e o head existem no clone (`git fetch`) e rode de novo; {NAO_LIBERAVEL}", ADR)


def violacao_de_git(e):
    """A violação de uma falha do git: o texto de `ErroDeGit`, ou o estouro de prazo ou a falta do próprio `git`."""
    if isinstance(e, ErroDeGit):
        return str(e)
    return msg_falha_git(f"o git não terminou: {type(e).__name__}")


FALHAS_DO_GIT = (ErroDeGit, subprocess.TimeoutExpired, OSError)


def alterados(raiz, base, head):
    """Caminhos tocados entre base e head. `--no-renames`: mover ou apagar conta como mudança do caminho antigo também.
    Falha fechada: se o `git diff` falha, levanta `ErroDeDiff` em vez de devolver lista vazia."""
    cod, saida = git(raiz, "diff", "--no-renames", "--name-only", "-z", base, head)
    if cod:
        raise ErroDeDiff(msg_diff(base, head))
    return [a for a in saida.split("\0") if a]


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


POLITICA = "hooks/conformidade.json"


def _chave(entrada):
    return json.dumps(entrada, sort_keys=True)


def _rotulo(entrada):
    return entrada.get("caminho") if isinstance(entrada, dict) else repr(entrada)


def _entrada_nova_invalida(entrada, base, papeis):
    """Por que uma entrada acrescentada em `caminhos` não é aceita sem o rótulo; `None` se é aceitável."""
    if not isinstance(entrada, dict) or not isinstance(entrada.get("caminho"), str) or not entrada["caminho"]:
        return "entrada sem `caminho` textual"
    quem = entrada.get("quem")
    if not isinstance(quem, list) or not all(isinstance(q, str) for q in quem):
        return "`quem` ausente ou fora da forma (lista de papéis)"
    if not isinstance(entrada.get("motivo"), str) or not entrada["motivo"]:
        return "`motivo` ausente ou fora da forma (texto não vazio)"
    if not isinstance(entrada.get("so_forge", False), bool):
        return "`so_forge` fora da forma (booleano)"
    if "branch" in entrada and (not isinstance(entrada["branch"], str) or not entrada["branch"]):
        return "`branch` fora da forma (texto não vazio)"
    fora = sorted(set(entrada) - {"caminho", "quem", "motivo", "so_forge", "branch"})
    if fora:
        return f"chave desconhecida: {', '.join(fora)}"
    if "dev" in quem:
        return "`quem` contém `dev`"
    if [q for q in quem if q not in papeis]:
        return f"`quem` com papel inexistente: {', '.join(q for q in quem if q not in papeis)}"
    if any(isinstance(c, dict) and str(c.get("caminho", "")).startswith(entrada["caminho"]) for c in base):
        return "caminho igual ou prefixo de um caminho já protegido (muda o casamento com o que existe)"
    return None


def mudancas_da_politica(b, h):
    """Lista branca: a única mudança aceita em `hooks/conformidade.json` é acrescentar entradas válidas em `caminhos`.
    Devolve o motivo de cada diferença fora disso (lista vazia se a política é a mesma ou só ganhou entradas aceitáveis)."""
    if not isinstance(h, dict):
        return ["o arquivo deixou de ser um objeto JSON ou foi removido"]
    motivos = [f"`{k}` mudou ou foi removido" for k in sorted(b) if k != "caminhos" and b[k] != h.get(k)]
    motivos += [f"chave nova `{k}`" for k in sorted(h) if k != "caminhos" and k not in b]
    base, atual = b.get("caminhos"), h.get("caminhos")
    if not isinstance(base, list) or not isinstance(atual, list):
        return motivos + ["`caminhos` ausente ou fora da forma (lista)"]
    ck_base, ck_atual = Counter(_chave(c) for c in base), Counter(_chave(c) for c in atual)
    novas = [json.loads(k) for k in (ck_atual - ck_base).elements()]
    for k in (ck_base - ck_atual).elements():
        motivos.append(f"entrada de `caminhos` removida ou alterada: {_rotulo(json.loads(k))}")
    papeis = set(h.get("papeis") or {}) if isinstance(h.get("papeis"), dict) else set()
    for c in novas:
        porque = _entrada_nova_invalida(c, base, papeis)
        if porque:
            motivos.append(f"entrada nova {_rotulo(c)}: {porque}")
    return motivos


def regra_politica(raiz, b, h):
    antes = json_de(raiz, b, POLITICA)
    if antes is None:
        return []
    motivos = mudancas_da_politica(antes, json_de(raiz, h, POLITICA))
    if not motivos:
        return []
    return [msg("R-CONFORMIDADE", f"{POLITICA} mudou além de acrescentar caminhos protegidos: {'; '.join(motivos)}",
                "a política só cresce por entrada nova válida; o resto pode dar mais poder ou desligar um bloqueio",
                f"restaure o trecho ou peça o rótulo `{ROTULO}` ao dono", "docs/regras/R-CONFORMIDADE.md")]


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


def msg_protegido(a):
    return msg("R-CONFORMIDADE", f"mudança em {a}", "workflows, rulesets, CODEOWNERS, hooks do git, dependabot, a catraca, os hooks que decidem o bloqueio e o forge-check são os próprios controles",
               f"só passa com o rótulo `{ROTULO}` do dono, aplicado depois do último push", ADR)


def arquivo_da_violacao(v):
    """O caminho de uma violação "mudança em <arquivo>" de `regra_protegidos`; None para qualquer outra violação."""
    prefixo, sufixo = msg_protegido("\0").split("\0")
    if not (v.startswith(prefixo) and v.endswith(sufixo)) or len(v) <= len(prefixo) + len(sufixo):
        return None
    a = v[len(prefixo):-len(sufixo)]
    return a if msg_protegido(a) == v else None


def regra_protegidos(raiz, b, h):
    if not existe(raiz, b, "tests/catraca.py"):  # introdução da própria catraca; erro do git levanta (não é "ausente")
        return []
    return [msg_protegido(a) for a in alterados(raiz, b, h) if a.startswith(PROTEGIDOS)]


def regra_arquivos_de_regras(raiz, b, h, cfg_base):
    """Apagar ou mover arquivo com `invariantes` ou de `docs/regras/` tira a regra do alcance dos testes."""
    v = []
    for a in alterados(raiz, b, h):
        if ler(raiz, h, a) is None and ler(raiz, b, a) is not None and (a in cfg_base.get("invariantes", {}) or a.startswith("docs/regras/")):
            v.append(msg("R-CONFORMIDADE", f"arquivo de regra apagado ou movido: {a}", "as regras da fábrica vivem nestes arquivos e os testes os procuram pelo caminho",
                         f"restaure o arquivo ou peça o rótulo `{ROTULO}` ao dono", "docs/regras/R-CONFORMIDADE.md"))
    return v


def violacoes_das_regras(raiz, base, head="HEAD"):
    try:
        return _violacoes_das_regras(raiz, base, head)
    except FALHAS_DO_GIT as e:
        return [violacao_de_git(e)]


def _violacoes_das_regras(raiz, base, head):
    b = base_efetiva(raiz, base, head)
    cb, ch = json_de(raiz, b, "tests/config.json"), json_de(raiz, head, "tests/config.json")
    permitido = (ch or {}).get("custo_permitido", {})
    return (regras_de_config(cb, ch or {}) + regra_arquivos_de_regras(raiz, b, head, cb or {}) + regra_hooks(raiz, b, head) + regra_testes(raiz, b, head)
            + regra_testes_enfraquecidos(raiz, b, head) + regra_politica(raiz, b, head)
            + regra_custo(raiz, head, permitido) + regra_protegidos(raiz, b, head))


# --- Rótulo do dono ----------------------------------------------------------------------------------------
def instante(texto):
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def rotulo_do_dono(eventos, dono):
    """O último evento do rótulo, se for `labeled` pelo dono; senão None."""
    ultimo = None
    for e in sorted((e for e in eventos if (e.get("label") or {}).get("name") == ROTULO
                     and e.get("event") in ("labeled", "unlabeled")), key=lambda e: e["created_at"]):
        ultimo = e
    if not ultimo or ultimo["event"] != "labeled" or not dono or (ultimo.get("actor") or {}).get("login") != dono:
        return None
    return ultimo


def rotulo_liberado(eventos, dono, ultimo_push):
    """True se o último evento do rótulo é `labeled` pelo dono e posterior ao último push."""
    ultimo = rotulo_do_dono(eventos, dono)
    return bool(ultimo) and instante(ultimo["created_at"]) > instante(ultimo_push)


def commit_do_rotulo(eventos, execucoes, numero, dono):
    """SHA do head do PR no instante em que o dono aplicou o rótulo; None se não der para saber com segurança.

    Instantes só do servidor: o head vigente é o da última execução `pull_request` deste PR criada antes do rótulo.
    Falha fechada se o mesmo head não tem execução depois do rótulo (a do próprio `labeled`; sem ela, o head do
    instante do rótulo pode não ter execução, como com `[skip ci]`) ou se a branch foi reescrita depois dele.
    """
    rotulo = rotulo_do_dono(eventos, dono)
    if not rotulo:
        return None
    t = instante(rotulo["created_at"])
    do_pr = [e for e in execucoes if e.get("event") == "pull_request" and e.get("head_sha") and e.get("created_at")
             and any(str(p.get("number")) == str(numero) for p in e.get("pull_requests") or [])]
    antes = [e for e in do_pr if instante(e["created_at"]) < t]
    if not antes:
        return None
    vigente = max(antes, key=lambda e: instante(e["created_at"]))
    sha, desde = vigente["head_sha"], instante(vigente["created_at"])
    if not any(e["head_sha"] == sha and instante(e["created_at"]) >= t for e in do_pr):
        return None
    if any(e.get("event") in REESCRITA and instante(e["created_at"]) > desde for e in eventos):
        return None
    return sha


def pareceres_do_pedido(raiz, base, rotulado, head, ramo):
    """Pareceres que podem mudar depois do rótulo: os que o PR já tocava no head rotulado e os de nome igual ao último
    segmento da branch (`melhoria/x` -> `docs/reviews/x.md`, `docs/qa/x.md`). Caminho com curinga fica de fora (falha fechada)."""
    def tocados(ref):
        return {a for a in alterados(raiz, base_efetiva(raiz, base, ref), ref) if a.startswith(PARECERES)}
    nome = ramo.rsplit("/", 1)[-1]
    antes = tocados(rotulado)
    livres = antes | {a for a in tocados(head) if nome and Path(a).stem == nome and Path(a).parent.as_posix() + "/" in PARECERES}
    return sorted(a for a in livres if not CURINGA.search(a))


def chave_da_violacao(v):
    """Regra e o que foi violado (com o caminho), sem os números: contagens e linhas mudam com a base, a violação não."""
    return re.sub(r"\b\d+\b", "N", v.split(". Por quê:", 1)[0])


def violacoes_novas(atuais, rotuladas):
    """Violações atuais que não estavam no head rotulado (multiconjunto pela chave normalizada)."""
    sobra = Counter(map(chave_da_violacao, atuais)) - Counter(map(chave_da_violacao, rotuladas))
    return [v for v in atuais if sobra.get(chave_da_violacao(v))]


def rotulo_vale_pelo_conteudo(raiz, base, head, eventos, execucoes, numero, dono, ramo="", atuais=None):
    """True se o diff efetivo do head (merge-base com a base, fora dos pareceres do pedido) é o do head no instante do
    rótulo e nenhuma violação atual é nova em relação às do head rotulado sobre o merge-base dele (ex.: vinda da base)."""
    sha = commit_do_rotulo(eventos, execucoes, numero, dono)
    if not sha or not forge_check().mesmo_diff(raiz, base, sha, head, pareceres_do_pedido(raiz, base, sha, head, ramo)):
        return False
    atuais = violacoes_das_regras(raiz, base, head) if atuais is None else atuais
    return not violacoes_novas(atuais, violacoes_das_regras(raiz, base, sha))


def requisicao(caminho, token):
    req = urllib.request.Request(f"https://api.github.com{caminho}",
                                 headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def api_objeto(caminho, token):
    """GET de um recurso único (ex.: o PR)."""
    return requisicao(caminho, token)


def api(caminho, token, chave=None):
    """GET paginado; `chave` extrai a lista de uma resposta em objeto (ex.: `workflow_runs`)."""
    itens, pagina = [], 1
    while True:
        lote = requisicao(f"{caminho}{'&' if '?' in caminho else '?'}per_page=100&page={pagina}", token)
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


def ramo_do_pr():
    """Branch do PR (`head.ref`) via API; "" sem token, repositório ou número, ou se a API falhar (só os pareceres que
    o PR já tocava ficam fora da comparação: mais estrito)."""
    token, repo, numero = (os.environ.get(k) for k in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER"))
    if not (token and repo and numero):
        return ""
    try:
        ramo = api_objeto(f"/repos/{repo}/pulls/{numero}", token)["head"]["ref"]
    except (OSError, ValueError, KeyError, TypeError):
        return ""
    return ramo if isinstance(ramo, str) else ""


def execucoes_do_pr():
    """Execuções `pull_request` da branch do PR via API; None sem token, repositório, número ou branch, ou se a API falhar."""
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    ramo = ramo_do_pr()
    if not ramo:
        return None
    try:
        return api(f"/repos/{repo}/actions/runs?event=pull_request&branch={urllib.parse.quote(ramo, safe='')}", token, "workflow_runs")
    except (OSError, ValueError, KeyError, TypeError):
        return None


# --- Rótulo já posto num PR mesclado (S-16) ----------------------------------------------------------------
LIMITE_CANDIDATOS = 20  # PRs consultados por execução: tempo dentro do timeout de 10 min da catraca
TETO_PAGINAS = 3  # páginas de 100 por consulta; além disso, falha fechada
MODOS_COMUNS = ("100644", "100755")  # arquivo comum; link simbólico (120000) e submódulo (160000) nunca contam como o mesmo conteúdo
NUMERO_DE_PR = re.compile(r"#(\d+)\b")


def api_com_teto(caminho, token, chave=None, teto=TETO_PAGINAS):
    """GET paginado como `api`, mas None se a resposta passa de `teto` páginas (lista incompleta não decide nada)."""
    itens = []
    for pagina in range(1, teto + 1):
        lote = requisicao(f"{caminho}{'&' if '?' in caminho else '?'}per_page=100&page={pagina}", token)
        lote = lote[chave] if chave else lote
        if not isinstance(lote, list):
            return None
        itens += lote
        if len(lote) < 100:
            return itens
    return None


class FonteGithub:
    """PR atual e PRs mesclados pela API do GitHub com o $GITHUB_TOKEN de leitura; cada falha vira None (falha fechada)."""

    def __init__(self, token, repo, numero):
        self.token, self.repo, self.numero = token, repo, numero

    def _ou_none(self, f):
        try:
            return f()
        except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException):
            return None

    def pr_atual(self):
        return self.pull(self.numero)

    def pull(self, n):
        return self._ou_none(lambda: api_objeto(f"/repos/{self.repo}/pulls/{n}", self.token))

    def eventos(self, n):
        return self._ou_none(lambda: api_com_teto(f"/repos/{self.repo}/issues/{n}/events", self.token))

    def execucoes(self, n, pull):
        """Execuções `pull_request` da branch do PR criadas entre a abertura e o merge (filtro do servidor; reconferido)."""
        janela = urllib.parse.quote(f"{pull['created_at']}..{pull['merged_at']}", safe="")
        ramo = urllib.parse.quote(pull["head"]["ref"], safe="")
        return self._ou_none(lambda: api_com_teto(f"/repos/{self.repo}/actions/runs?event=pull_request&branch={ramo}&created={janela}",
                                                  self.token, "workflow_runs"))


class FonteJson:
    """O mesmo que `FonteGithub`, lido de um JSON (testes, `--mesclados`): {"repo", "pr", "pulls": {n}, "eventos": {n}, "execucoes": {n}}."""

    def __init__(self, dados):
        self.dados = dados if isinstance(dados, dict) else {}
        self.repo = self.dados.get("repo")

    def _de(self, chave, n):
        return (self.dados.get(chave) or {}).get(str(n))

    def pr_atual(self):
        return self.dados.get("pr")

    def pull(self, n):
        return self._de("pulls", n)

    def eventos(self, n):
        return self._de("eventos", n)

    def execucoes(self, n, pull):
        return self._de("execucoes", n)


def fonte_do_github():
    """`FonteGithub` do PR atual; None sem token, repositório ou número do PR (falha fechada)."""
    token, repo, numero = (os.environ.get(k) for k in ("GITHUB_TOKEN", "GITHUB_REPOSITORY", "PR_NUMBER"))
    return FonteGithub(token, repo, numero) if token and repo and numero else None


def _repo_de(lado):
    return ((lado or {}).get("repo") or {}).get("full_name")


def eh_promocao(pr, repo):
    """PR de promoção (PROMOCOES) com as duas pontas no próprio repositório (branch `develop` de um fork não conta)."""
    if not isinstance(pr, dict) or not repo:
        return False
    head, base = pr.get("head") or {}, pr.get("base") or {}
    return (head.get("ref"), base.get("ref")) in PROMOCOES and _repo_de(head) == repo and _repo_de(base) == repo


def entrada_da_arvore(raiz, ref, caminho):
    """(modo, objeto) do arquivo comum em `ref`; None se ausente, pasta, link simbólico, submódulo ou erro do git."""
    cod, saida = git(raiz, "--literal-pathspecs", "ls-tree", "-z", "--full-tree", ref, "--", caminho)
    entradas = [e for e in saida.split("\0") if e] if not cod else []
    if len(entradas) != 1:
        return None
    meta, _, nome = entradas[0].partition("\t")
    modo, tipo, objeto = (meta.split(" ") + ["", "", ""])[:3]
    return (modo, objeto) if nome == caminho and tipo == "blob" and modo in MODOS_COMUNS else None


def mesmo_arquivo(raiz, a, b, caminho):
    """True se o caminho tem o mesmo blob e o mesmo modo (arquivo comum) nos dois commits."""
    x = entrada_da_arvore(raiz, a, caminho)
    return x is not None and x == entrada_da_arvore(raiz, b, caminho)


def candidatos_mesclados(raiz, base, head, arquivos):
    """(commits de base..head, números de PR candidatos): os citados (`#n`) no assunto dos commits do intervalo que tocam um
    dos arquivos, do mais novo ao mais antigo, até LIMITE_CANDIDATOS. O assunto só sugere: a API confirma o merge."""
    cod, saida = git(raiz, "-c", "core.quotePath=false", "log", "--no-renames", "--diff-merges=first-parent", "--name-only",
                     "--format=%x1e%H%x1f%s", f"{base}..{head}")
    if cod:
        return set(), []
    intervalo, numeros = set(), []
    for bloco in saida.split("\x1e")[1:]:
        cabeca, _, nomes = bloco.partition("\n")
        sha, _, assunto = cabeca.partition("\x1f")
        intervalo.add(sha)
        if set(nomes.splitlines()) & arquivos:
            numeros += [n for n in NUMERO_DE_PR.findall(assunto) if n not in numeros]
    return intervalo, numeros[:LIMITE_CANDIDATOS]


REF_BUSCADA = "refs/catraca/pull/{}"  # namespace só da catraca: o fetch nunca escreve em branch, remoto ou tag (M1)
SHA_COMPLETO = re.compile(r"[0-9a-f]{40}")


def aviso(texto):
    print(f"catraca: {texto}; vale como sem rótulo.")


def buscar_cabeca_do_pr(raiz, n):
    """Traz `refs/pull/<n>/head` do `origin` para `refs/catraca/pull/<n>` (só objetos, sem checkout, sem FETCH_HEAD, sem tags).
    True se o git terminou bem; `TimeoutExpired` sobe para quem chama (falha fechada em `liberado_por_pr_mesclado_ou_none`)."""
    n = int(n)
    cod, _ = git(raiz, "-c", "maintenance.auto=false", "-c", "gc.auto=0", "fetch", "--no-tags", "--no-recurse-submodules", "--no-write-fetch-head", "origin",
                 f"refs/pull/{n}/head:{REF_BUSCADA.format(n)}")
    if cod:
        aviso(f"não consegui buscar refs/pull/{n}/head")
    return not cod


def tem_commit(raiz, sha):
    return not git(raiz, "cat-file", "-e", f"{sha}^{{commit}}")[0]


def prova_do_squash(raiz, pull, n, s, m, base, head):
    """Substituto da ancestralidade quando o merge M é squash (S nunca é ancestral dele): M tem um pai só e está na cadeia de
    primeiro pai de base..head; S, o head rotulado, é ancestral do `head.sha` da API, que é o que `refs/pull/<n>/head` traz."""
    cod, pais = git(raiz, "rev-list", "--parents", "-n", "1", m)
    if cod or len(pais.split()) != 2 or m not in git(raiz, "rev-list", "--first-parent", f"{base}..{head}")[1].split():
        return False
    final = (pull.get("head") or {}).get("sha")
    if not isinstance(final, str) or not SHA_COMPLETO.fullmatch(final):
        return False
    if not (tem_commit(raiz, s) and tem_commit(raiz, final)):
        if not buscar_cabeca_do_pr(raiz, n):
            return False
        cod, trazido = git(raiz, "rev-parse", "--verify", "-q", f"{REF_BUSCADA.format(int(n))}^{{commit}}")
        if cod or trazido.strip() != final or not tem_commit(raiz, s):
            return False
    return not git(raiz, "merge-base", "--is-ancestor", s, final)[0]


def sha_rotulado_do_mesclado(raiz, fonte, n, ramo, dono, intervalo, base=None, head=None):
    """(S, M, squash) do PR `n`: mesclado no `ramo` do próprio repositório (base e head), com `merge_commit_sha` M em base..head,
    último evento do rótulo `labeled` pelo dono (sem app) e S, o head no instante do rótulo (`commit_do_rotulo`), presente
    no git local e ancestral de M. Sem isso, e só se M for squash (`prova_do_squash`), S pode vir de `refs/pull/<n>/head`.
    Qualquer dúvida devolve None (sem rótulo)."""
    try:
        pull = fonte.pull(n)
        if not isinstance(pull, dict) or not pull.get("merged_at") or pull.get("merge_commit_sha") not in intervalo:
            return None
        if (pull.get("base") or {}).get("ref") != ramo or _repo_de(pull.get("base")) != fonte.repo or _repo_de(pull.get("head")) != fonte.repo:
            return None
        eventos = fonte.eventos(n)
        ultimo = rotulo_do_dono(eventos, dono) if isinstance(eventos, list) else None
        if not ultimo or ultimo.get("performed_via_github_app"):
            return None
        execucoes = fonte.execucoes(n, pull)
        if not isinstance(execucoes, list):
            return None
        inicio, fim, ramo_pr = instante(pull["created_at"]), instante(pull["merged_at"]), pull["head"]["ref"]
        # O `pull_requests` das execuções de PR fechado vem vazio: valem as da branch dele, do próprio repositório, na vida do PR.
        do_pr = [{**e, "pull_requests": [{"number": n}]} for e in execucoes
                 if e.get("event") == "pull_request" and e.get("head_branch") == ramo_pr and e.get("created_at")
                 and ((e.get("head_repository") or {}).get("full_name")) == fonte.repo and inicio <= instante(e["created_at"]) <= fim]
        # Apagar ou restaurar a branch depois do merge não muda o que foi mesclado; antes dele, reescrita segue falhando fechado.
        antes_do_merge = [e for e in eventos if not (e.get("event") in REESCRITA and instante(e["created_at"]) > fim)]
        s, m = commit_do_rotulo(antes_do_merge, do_pr, n, dono), pull["merge_commit_sha"]
    except (KeyError, TypeError, ValueError, AttributeError):
        return None
    if not s:
        return None
    if tem_commit(raiz, s) and not git(raiz, "merge-base", "--is-ancestor", s, m)[0]:
        return s, m, False
    if base is None or head is None or not prova_do_squash(raiz, pull, n, s, m, base, head):
        return None
    return s, m, True


def liberado_por_pr_mesclado(raiz, base, head, viol, fonte, dono):
    """Números dos PRs mesclados que cobrem todas as violações, ou None. Só em promoção e só violações "mudança em <arquivo>":
    cada uma fica coberta se o arquivo tem em `head` o mesmo blob e modo que no head rotulado S de um PR candidato e a mesma
    violação existia em S sobre o merge-base dele com o primeiro pai do merge (o rótulo cobriu aquele arquivo). Sem
    transitividade: o PR candidato precisa do próprio rótulo do dono."""
    if fonte is None or not dono:
        return None
    arquivos = [arquivo_da_violacao(v) for v in viol]
    if not arquivos or None in arquivos:
        return None
    pr = fonte.pr_atual()
    if not eh_promocao(pr, fonte.repo):
        return None
    intervalo, numeros = candidatos_mesclados(raiz, base, head, set(arquivos))
    pendentes, usados = set(arquivos), []
    for n in numeros:
        sm = sha_rotulado_do_mesclado(raiz, fonte, n, pr["head"]["ref"], dono, intervalo, base, head)
        if not sm:
            continue
        s, m, squash = sm
        de_s = set(regra_protegidos(raiz, base_efetiva(raiz, f"{m}^1", s), s))  # a mesma violação, texto exato (sem normalizar números)
        # No squash o que vale é o arquivo que o merge gravou: igual ao rotulado, byte a byte e no modo (M3)
        cobertos = {a for a in pendentes if msg_protegido(a) in de_s and mesmo_arquivo(raiz, head, s, a)
                    and (not squash or mesmo_arquivo(raiz, m, s, a))}
        if cobertos:
            pendentes -= cobertos
            usados.append(n)
        if not pendentes:
            return usados
    return None


def liberado_por_pr_mesclado_ou_none(raiz, base, head, viol, fonte, dono):
    """`liberado_por_pr_mesclado`, mas git que estoura o prazo ou não executa vale como sem rótulo (M5), com mensagem."""
    try:
        return liberado_por_pr_mesclado(raiz, base, head, viol, fonte, dono)
    except FALHAS_DO_GIT as e:
        aviso(f"o git não terminou ({type(e).__name__})")
        return None


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
    try:
        return _violacoes_de_pareceres(raiz, base, head, ramo, base_ref)
    except FALHAS_DO_GIT as e:
        return [violacao_de_git(e)]


def _violacoes_de_pareceres(raiz, base, head, ramo, base_ref):
    if (ramo, base_ref) in PROMOCOES:
        return []
    b = base_efetiva(raiz, base, head)
    tocados = [a for a in alterados(raiz, b, head) if a.startswith(SENSIVEIS)]
    if not tocados:
        return []
    fc, achados = forge_check(), []
    pedidos = fc.pedidos_da_branch(Path(raiz), ramo, head)
    for ped in pedidos:  # todos os pedidos da branch passam: um aprovado não cobre o reprovado de outro
        linhas = [l for l in fc.cmd_pr(Path(raiz), ped, head, base) if l.strip()]
        if base_ref != "homolog":  # o QA só é exigido na entrada da homolog
            linhas = [l for l in linhas if not l.startswith("docs/qa") and "(R-QA)" not in l]
        achados += linhas
    if pedidos and not achados:
        return []
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
    try:
        return _main(argv)
    except ErroDeGit as e:  # um diff que falha fora das regras (ex.: conferir o rótulo) também deixa a catraca vermelha
        print(e)
        resumo("catraca", [str(e)])
        return 1


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modo", choices=("regras", "pr-texto", "pareceres"), default="regras")
    ap.add_argument("--base", default=os.environ.get("BASE", "origin/develop"))
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--raiz", default=".")
    ap.add_argument("--ramo", default=os.environ.get("HEAD_REF", ""), help="branch do PR (modo pareceres; no modo regras, pareceres do pedido, e sem ela vem da API)")
    ap.add_argument("--base-ref", default=os.environ.get("BASE_REF", ""), help="branch de destino (modo pareceres)")
    ap.add_argument("--autor", default=os.environ.get("PR_AUTOR", ""), help="login do autor do PR")
    ap.add_argument("--eventos", help="JSON com os eventos da issue (testes); ignora a API")
    ap.add_argument("--ultimo-push", help="instante ISO do último push (com --eventos)")
    ap.add_argument("--execucoes", help="JSON com as execuções do Actions do PR (testes, com --eventos); ignora a API")
    ap.add_argument("--pr", default=os.environ.get("PR_NUMBER", ""), help="número do PR")
    ap.add_argument("--mesclados", help="JSON com o PR atual e os PRs mesclados (testes; formato em FonteJson); ignora a API")
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
            cfg = json_de(raiz, base_efetiva(raiz, a.base, a.head), "tests/config.json")  # só a base: o head é do autor
            cfg = cfg if isinstance(cfg, dict) else {}
            custo = [x for x in viol if x.startswith("R-CUSTO:") or NAO_LIBERAVEL in x]  # só `custo_permitido` abre exceção de custo; o rótulo não vale nem com o git falho
            dono, liberado = cfg.get("dono"), None
            if not custo and eventos is not None:
                if push and rotulo_liberado(eventos, dono, push):
                    liberado = "aplicado depois do último push"
                else:
                    execucoes = json.loads(Path(a.execucoes).read_text(encoding="utf-8")) if a.execucoes else ([] if a.eventos else execucoes_do_pr())
                    ramo = a.ramo or ("" if a.eventos else ramo_do_pr())
                    if execucoes is not None and rotulo_vale_pelo_conteudo(raiz, a.base, a.head, eventos, execucoes, a.pr, dono, ramo, viol):
                        liberado = "diff efetivo igual ao do instante do rótulo"
            if not custo and not liberado:
                fonte = FonteJson(json.loads(Path(a.mesclados).read_text(encoding="utf-8"))) if a.mesclados else (
                    None if a.eventos else fonte_do_github())
                prs = liberado_por_pr_mesclado_ou_none(raiz, a.base, a.head, viol, fonte, dono)
                if prs:
                    liberado = f"mesmo conteúdo já rotulado no PR mesclado {', '.join('#' + n for n in prs)}"
            if liberado:
                resumo(titulo, [f"liberado pelo rótulo `{ROTULO}` do dono ({liberado}): {len(viol)} violação(ões) aceita(s)"] + viol)
                print(f"catraca: {len(viol)} violação(ões) liberada(s) pelo rótulo `{ROTULO}` do dono ({liberado}).")
                return 0
    for v in viol:
        print(v)
    resumo(titulo, viol)
    return 1 if viol else 0


if __name__ == "__main__":
    sys.exit(main())
