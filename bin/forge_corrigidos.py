"""Forge: `forge-check corrigidos` e `forge-check afrouxamentos` (M14b; FILA-31 F6, 0.45.7 E5.3): os PRs `fix` que corrigem PR já
mesclado e, dos PRs rotulados `afrouxa-regra`, quantos afrouxavam regra de verdade, lidos do histórico do git. Só leitura, sem rede,
só biblioteca padrão.

Importado pelo `bin/forge-check` só quando um desses dois roda. `ctx` traz do forge-check os nomes que ele divide com outros
subcomandos (`git`, `sha_do_commit`, `nome_seguro`, `sem_controle` e `carregar_catraca`, que o `classe` também usa); a janela padrão
do `--dias` (`DIAS_DO_CORRIGIDO`) fica no forge-check, no parser.
"""
import json
import re
from pathlib import Path

# ---- M14b: PR `fix` que corrige PR já mesclado, lido do histórico do git (só leitura, sem rede) ----
PR_NO_ASSUNTO = re.compile(r"\(#(\d+)\)\s*$|^Merge pull request #(\d+)\b")
TIPO_FIX = re.compile(r"^fix(\([^)]*\))?!?:")
PR_CITADO = re.compile(r"(?<![0-9A-Za-z&])#(\d{1,6})(?!\d)")
REFS_PADRAO = ("origin/develop", "develop", "HEAD")


def resolver_ref(raiz, ref, ctx):
    """(sha40, nome) da `ref` pedida ou, sem ela, da primeira de `REFS_PADRAO` que existe; (None, nome) se não existe."""
    sha_do_commit = ctx["sha_do_commit"]
    for nome in ([ref] if ref else REFS_PADRAO):
        sha = sha_do_commit(raiz, nome)
        if sha:
            return sha, nome
    return None, ref or REFS_PADRAO[0]


def commits_da_ref(raiz, sha, ctx):
    """Os commits da linha principal (`--first-parent`; o merge comum conta pelo diff contra o primeiro pai) até `sha`, do mais antigo
    ao mais novo: dicts com `sha`, `hora` (epoch), `titulo` (o assunto; no merge comum, a 1.ª linha do corpo), `texto` (assunto e corpo),
    `arquivos` e `pr` (número do PR, ou None se o commit não é de PR); None se o git falha."""
    git = ctx["git"]
    cod, bruto = git(raiz, "log", "--first-parent", "-m", "--reverse", "--name-only", "-z", "--format=%x1e%H%x1f%ct%x1f%s%x1f%b%x1f",
                     "--end-of-options", sha, bruto=True)
    if cod:
        return None
    commits = []
    for pedaco in bruto.decode("utf-8", "replace").split("\x1e")[1:]:
        campos = pedaco.split("\x1f", 4)
        if len(campos) < 5 or not campos[1].isdigit():
            continue
        assunto, corpo = campos[2], campos[3]
        achou = PR_NO_ASSUNTO.search(assunto)
        titulo = assunto
        if assunto.startswith("Merge pull request"):
            titulo = next((l.strip() for l in corpo.splitlines() if l.strip()), assunto)
        commits.append({"sha": campos[0], "hora": int(campos[1]), "titulo": titulo, "texto": f"{assunto}\n{corpo}",
                        "arquivos": [a for a in campos[4].lstrip("\0\n").split("\0") if a],
                        "pr": int(achou.group(1) or achou.group(2)) if achou else None})
    return commits


def corrigidos_da_linha(commits, dias):
    """[(commit, evidência, citados, tocados)] dos PRs `fix` da linha: `cita` se o texto do PR cita (#N) um PR mesclado antes dele (prova
    escrita); `arquivo` se não cita, mas mexe num arquivo que outro PR mesclou até `dias` antes (indício: pode ser outro assunto no mesmo
    arquivo); `nenhuma` nos demais. A ordem é a do histórico."""
    vistos, ultimo, saida = set(), {}, []
    for c in commits:
        if c["pr"] is not None and TIPO_FIX.match(c["titulo"]):
            citados = sorted(({int(n) for n in PR_CITADO.findall(c["texto"])} & vistos) - {c["pr"]})
            antes = (ultimo.get(a, (None, 0)) for a in c["arquivos"])
            tocados = sorted({pr for pr, h in antes if pr is not None and pr != c["pr"] and c["hora"] - h <= dias * 86400})
            saida.append((c, "cita" if citados else "arquivo" if tocados else "nenhuma", citados, tocados))
        if c["pr"] is not None:
            vistos.add(c["pr"])
        for a in c["arquivos"]:
            ultimo[a] = (c["pr"], c["hora"])
    return saida


def cmd_corrigidos(raiz, ref, dias, ctx):
    """Lista os PRs `fix` que corrigem PR já mesclado (`corrigidos: #N sha evidencia=... cita=... toca=... titulo`) e o resumo; só leitura.
    rc 1 se a ref não existe ou o git falha."""
    nome_seguro, sem_controle = ctx["nome_seguro"], ctx["sem_controle"]
    sha, nome = resolver_ref(raiz, ref, ctx)
    commits = commits_da_ref(raiz, sha, ctx) if sha else None
    if commits is None:
        print(f"corrigidos: ref {nome_seguro(sem_controle(nome))} não existe ou o git falhou")
        return 1
    contagem = {"cita": 0, "indicio": 0, "nenhuma": 0}
    fixes = corrigidos_da_linha(commits, dias)
    for c, evidencia, citados, tocados in fixes:
        contagem["indicio" if evidencia == "arquivo" else evidencia] += 1
        if evidencia != "nenhuma":
            print(f"corrigidos: #{c['pr']} {c['sha'][:7]} evidencia={evidencia} cita={_lista_de_prs(citados)} toca={_lista_de_prs(tocados)} "
                  f"{sem_controle(c['titulo'])[:100]}")
    print(f"corrigidos: total: prs={sum(1 for c in commits if c['pr'] is not None)} fix={len(fixes)} cita={contagem['cita']} "
          f"arquivo={contagem['indicio']} nenhuma={contagem['nenhuma']} dias={dias} ref={sha[:7]}")
    return 0


def _lista_de_prs(numeros):
    return ",".join(f"#{n}" for n in numeros) or "-"


# ---- M14b: dos PRs com o rótulo `afrouxa-regra`, quantos afrouxavam regra de verdade (a catraca sobre o diff de cada PR) ----
TETO_DOS_ROTULADOS = 1024 * 1024


def numeros_dos_rotulados(prs, arquivo):
    """Números de PR de `--prs 1,2,3` e/ou de um JSON de `gh pr list --label afrouxa-regra --state all --json number` (lista de objetos com
    `number`); levanta ValueError com o campo (nunca o valor) se algo não é número ou o arquivo não lê."""
    numeros = []
    if prs:
        pedacos = [x.strip().lstrip("#") for x in prs.split(",")]
        if not all(re.fullmatch(r"\d{1,6}", x) for x in pedacos):
            raise ValueError("--prs deve ser uma lista de números de PR separados por vírgula")
        numeros += [int(x) for x in pedacos]
    if arquivo:
        try:
            with open(arquivo, "rb") as f:
                dados = f.read(TETO_DOS_ROTULADOS + 1)
            if len(dados) > TETO_DOS_ROTULADOS:
                raise ValueError(f"--rotulados passa de {TETO_DOS_ROTULADOS} bytes")
            itens = json.loads(dados.decode("utf-8"))
            numeros += [i["number"] for i in itens]
        except (OSError, UnicodeDecodeError, KeyError, TypeError):
            raise ValueError("--rotulados deve ser um arquivo JSON legível com uma lista de objetos com `number`") from None
        except json.JSONDecodeError:
            raise ValueError("--rotulados não é JSON") from None
        if not all(isinstance(n, int) and not isinstance(n, bool) and n > 0 for n in numeros):
            raise ValueError("--rotulados: `number` deve ser inteiro positivo")
    if not numeros:
        raise ValueError("informe --prs ou --rotulados")
    return list(dict.fromkeys(numeros))


def cmd_afrouxamentos(raiz, ref, prs, arquivo, ctx):
    """Classifica cada PR rotulado, pela catraca sobre o diff do commit dele contra o primeiro pai: `real` (alguma violação de conteúdo: regra
    piorada, invariante removido, limite subido...), `so-protegido` (só "mudança em <arquivo protegido>": o rótulo era exigido para editar um
    controle, sem afrouxá-lo), `sem-violacao` (o rótulo não era exigido), `sem-commit` (o PR não está na linha da ref) ou `erro-git`. Só leitura."""
    git, nome_seguro, sem_controle = ctx["git"], ctx["nome_seguro"], ctx["sem_controle"]
    try:
        numeros = numeros_dos_rotulados(prs, arquivo)
    except ValueError as erro:
        print(f"afrouxamentos: {erro}")
        return 2
    sha, nome = resolver_ref(raiz, ref, ctx)
    commits = commits_da_ref(raiz, sha, ctx) if sha else None
    catraca = ctx["carregar_catraca"]()
    if commits is None or catraca is None:
        print(f"afrouxamentos: {'ref ' + nome_seguro(sem_controle(nome)) + ' não existe ou o git falhou' if commits is None else 'não carreguei tests/catraca.py'}")
        return 1
    por_pr = {c["pr"]: c for c in commits if c["pr"] is not None}
    contagem = {"afrouxa": 0, "so-protegido": 0, "sem-violacao": 0, "sem-commit": 0, "erro-git": 0}
    for n in numeros:
        c = por_pr.get(n)
        if c is None or git(raiz, "rev-parse", "--verify", "--quiet", f"{c['sha']}^")[0]:
            veredito, regras = "sem-commit", []
        else:
            violacoes = catraca.violacoes_das_regras(Path(raiz), f"{c['sha']}^", c["sha"])
            de_conteudo = [v for v in violacoes if catraca.arquivo_da_violacao(v) is None]
            if any(catraca.NAO_LIBERAVEL in v for v in violacoes):
                veredito = "erro-git"
            else:
                veredito = "real" if de_conteudo else "so-protegido" if violacoes else "sem-violacao"
            regras = sorted({v.split(":", 1)[0] for v in de_conteudo if re.fullmatch(r"R-[A-Z]+", v.split(":", 1)[0])})
        contagem["afrouxa" if veredito == "real" else veredito] += 1
        print(f"afrouxamentos: #{n} {veredito}" + (f" regras={','.join(regras)}" if regras else ""))
    print(f"afrouxamentos: total: rotulados={len(numeros)} real={contagem['afrouxa']} so-protegido={contagem['so-protegido']} "
          f"sem-violacao={contagem['sem-violacao']} sem-commit={contagem['sem-commit']} erro-git={contagem['erro-git']} ref={sha[:7]}")
    return 0


def executar(a, raiz, ctx):
    """O despacho do forge-check para `corrigidos` e `afrouxamentos`; devolve o código de saída."""
    if a.cmd == "afrouxamentos":
        return cmd_afrouxamentos(raiz, a.ref, a.prs, a.rotulados, ctx)
    return cmd_corrigidos(raiz, a.ref, a.dias, ctx)
