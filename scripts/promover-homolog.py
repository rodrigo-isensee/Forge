#!/usr/bin/env python3
"""Forge: prepara e confere a promoção develop -> homolog (D5b, PA-5; R-FLUXO, R-CONTRIB). Só biblioteca padrão.

Uso: scripts/promover-homolog.py [--dry-run] [--ref origin/develop] [--base origin/homolog]

Passos, em ordem; para no primeiro erro:
  1. refs: só develop -> homolog (qualquer outro par, a main inclusive, é recusado); há commit a promover.
  2. pareceres: cada parecer de docs/{reviews,qa,security,devops}/ que a promoção traz (lido da ref) é `parecer: aprovado`.
  3. versão e CHANGELOG (lidos da ref): versão nova é maior que a da homolog; `## [<versão>]` existe; `[Não publicado]`
     vazio; sem fragmento em changelog.d/. Sem versão nova a promoção não é release e o CHANGELOG não é conferido
     (a mesma regra do CI, scripts/conferir-release.py --so-se-versao-mudou). Na release, `bin/forge-check pr
     release-<versão> --ref <ref> --base main`: parecer da release desatualizado ou faltando contra a main para (P-N3).
  4. PR develop -> homolog: abre se não houver (reusa o aberto; base que não seja a homolog para).
  5. checks: uma leitura de `gh pr checks --json`; só contam os do evento pull_request (os do push da develop, no
     mesmo sha, não são a bateria do PR); só pass/skipping passam.
  6. rótulo: a Catraca vermelha pede o rótulo `afrouxa-regra` do dono; o script só avisa, nunca o aplica.
  7. imprime o comando que liga o merge automático (--auto); com o merge automático desligado no repositório, o comando recusa e o tech-lead mescla com tudo verde. O script NÃO mescla: o rótulo segue com o dono.
--dry-run: roda só as leituras locais dos passos 1 a 3, o forge-check pr inclusive (nenhum fetch, nenhum gh, nenhum PR, nenhuma escrita) e descreve 4 a 7.
Sem --dry-run, antes do passo 1 roda `git fetch origin` (atualiza as refs remotas; é a única escrita local).
Código de saída: 0 pronta para o merge automático (checks verdes, pendentes ou ainda sem check; ou dry-run sem problema);
1 parou (inclui check vermelho); 3 preparada, mas o rótulo do dono por vir (rode de novo).
Nunca: mescla, aplica rótulo, usa --force ou --no-verify, toca a main. Roda só no repositório do Forge.
Para teste, com FORGE_PROMOVER_TESTE=1: FORGE_GH substitui o `gh` e FORGE_PROMOVER_PAUSA (segundos) a espera entre leituras
repetidas; sem a variável, FORGE_GH é ignorada, com aviso.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PASTAS_DE_PARECER = ("docs/reviews", "docs/qa", "docs/security", "docs/devops")
CATRACA = "catraca"
ROTULO = "afrouxa-regra"
PENDENTES = {"pending", "queued", "in_progress"}
FORGE_CHECK = Path(__file__).resolve().parent.parent / "bin" / "forge-check"
OK = {"pass", "skipping"}


def parar(msg, codigo=1):
    print(f"promover-homolog: {msg}", file=sys.stderr)
    sys.exit(codigo)


def git(*args, ok_vazio=False):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        parar(f"git {' '.join(args)} passou de 120 s")
    if r.returncode and not ok_vazio:
        parar(f"git {' '.join(args)}: {r.stderr.strip() or r.stdout.strip()}")
    return r


def mostrar(ref, caminho):
    """Texto do arquivo na ref; None se não existe lá."""
    r = git("show", f"{ref}:{caminho}", ok_vazio=True)
    return r.stdout if r.returncode == 0 else None


def frontmatter(texto):
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return None
    campos = {}
    for linha in linhas[1:]:
        if linha.strip() == "---":
            return campos
        if ":" in linha:
            chave, _, valor = linha.partition(":")
            campos[chave.strip()] = valor.strip()
    return None


def versao_de(ref, vazio="0.0.0"):
    texto = mostrar(ref, ".claude-plugin/plugin.json")
    try:
        return json.loads(texto)["version"] if texto else vazio
    except (ValueError, KeyError, TypeError):
        return vazio


def tupla(versao):
    try:
        return tuple(int(p) for p in versao.split("."))
    except ValueError:
        parar(f"versão que não é X.Y.Z: {versao}")


def conferir_refs(ref, base):
    if "main" in (ref.split("/")[-1], base.split("/")[-1]):
        parar("a main é só do dono (R-MAIN); este script só promove develop -> homolog (R-FLUXO)")
    if ref not in ("origin/develop", "develop") or base not in ("origin/homolog", "homolog"):
        parar(f"par fora do fluxo ({ref} -> {base}); só origin/develop -> origin/homolog (R-FLUXO)")
    for r in (ref, base):
        if git("rev-parse", "--verify", "-q", f"{r}^{{commit}}", ok_vazio=True).returncode:
            parar(f"não achei a ref {r}; rode git fetch origin (ou tire o --dry-run)")
    n = int(git("rev-list", "--count", f"{base}..{ref}").stdout.strip() or 0)
    if n == 0:
        parar(f"nada a promover: {ref} não tem commit que {base} não tenha")
    print(f"refs: {ref} está {n} commit(s) à frente de {base}")


def conferir_pareceres(ref, base):
    nomes = git("diff", "--name-only", "--no-renames", "--diff-filter=AM", base, ref, "--", *PASTAS_DE_PARECER).stdout.split("\n")
    arquivos = [n for n in nomes if n.endswith(".md") and not Path(n).name.startswith("_")
                and str(Path(n).parent) in PASTAS_DE_PARECER]
    problemas = []
    for arquivo in sorted(arquivos):
        campos = frontmatter(mostrar(ref, arquivo) or "")
        if campos is None:
            problemas.append(f"{arquivo}: sem frontmatter")
        elif campos.get("parecer") != "aprovado":
            problemas.append(f"{arquivo}: parecer '{campos.get('parecer', '')}' (esperado aprovado)")
    if problemas:
        parar("pareceres não aprovados na ref:\n  " + "\n  ".join(problemas))
    print(f"pareceres: {len(arquivos)} arquivo(s) da promoção, todos aprovados")


def conferir_versao(ref, base):
    atual, anterior = versao_de(ref), versao_de(base)
    print(f"versão: homolog {anterior} | develop {atual}")
    if atual == anterior:
        print("versão: sem versão nova, a promoção não é release; CHANGELOG não conferido (como o CI)")
        return atual
    if tupla(atual) < tupla(anterior):
        parar(f"a versão da develop ({atual}) é menor que a da homolog ({anterior})")
    changelog = mostrar(ref, "CHANGELOG.md")
    if changelog is None or not re.search(rf"^## \[{re.escape(atual)}\]", changelog, re.M):
        parar(f"CHANGELOG.md sem a entrada '## [{atual}]' na {ref}")
    m = re.search(r"^## \[Não publicado\][^\n]*\n(.*?)(?=^## |\Z)", changelog, re.M | re.S)
    if m and any(linha.strip() for linha in m.group(1).splitlines()):
        parar(f"'## [Não publicado]' com conteúdo na {ref}; converta em '## [{atual}] - data'")
    ls = git("ls-tree", "--name-only", ref, "changelog.d/", ok_vazio=True).stdout.split("\n")
    pendentes = [n for n in ls if n.endswith(".md") and Path(n).name.lower() != "readme.md"]
    if pendentes:
        parar(f"fragmento(s) pendente(s) na {ref}: {', '.join(pendentes)}; rode bin/forge-changelog release")
    print(f"CHANGELOG: entrada [{atual}] presente, [Não publicado] vazio, changelog.d/ sem fragmentos")
    return atual


def conferir_contra_main(ref, versao):
    """P-N3: o parecer da release vale contra a main antes de a versão entrar na homolog (forge-check pr, lido da ref)."""
    pedido = f"release-{versao}"
    comando = [sys.executable, "-I", str(FORGE_CHECK), "pr", pedido, "--ref", ref, "--base", "main"]
    print(" ".join(["forge-check", *comando[3:]]))
    try:
        r = subprocess.run(comando, capture_output=True, text=True, timeout=300)
    except (subprocess.TimeoutExpired, OSError) as e:
        parar(f"forge-check pr {pedido} contra a main não rodou: {e}")
    if r.returncode:
        citado = (r.stdout + r.stderr).strip().replace("\n", "\n  ")
        parar(f"forge-check pr {pedido} contra a main: parecer desatualizado ou faltando; peça novo parecer antes de promover:\n  {citado}")
    print(f"forge-check pr: pareceres de {pedido} valem contra a main")


def comando_gh():
    if os.environ.get("FORGE_PROMOVER_TESTE") == "1":
        return os.environ.get("FORGE_GH", "gh")
    if os.environ.get("FORGE_GH"):
        print("aviso: FORGE_GH só vale com FORGE_PROMOVER_TESTE=1; usando o gh real.", file=sys.stderr)
    return "gh"


def ler(gh, *args, tentativas=3):
    """Leitura idempotente do gh; repete o erro passageiro (502) até 3 vezes e devolve (código, saída)."""
    pausa = float(os.environ.get("FORGE_PROMOVER_PAUSA", "3")) if os.environ.get("FORGE_PROMOVER_TESTE") == "1" else 3.0
    for i in range(tentativas):
        try:
            r = subprocess.run([gh, *args], capture_output=True, text=True, timeout=120)
            cod, saida = r.returncode, r.stdout + (r.stderr if r.returncode else "")
        except (subprocess.TimeoutExpired, OSError) as e:
            cod, saida = 1, str(e)
        if cod == 0 or i == tentativas - 1:
            return cod, saida
        time.sleep(pausa)


def pr_aberto(gh):
    cod, saida = ler(gh, "pr", "list", "--head", "develop", "--state", "open", "--json", "number,baseRefName",
                     "--jq", '.[] | "\\(.number) \\(.baseRefName)"')
    if cod:
        parar(f"não consegui ler os PRs abertos da develop: {saida.strip()}")
    linhas = [l.split() for l in saida.splitlines() if l.strip()]
    for numero, base in linhas:
        if base != "homolog":
            parar(f"o PR aberto #{numero} da develop tem base {base}, não homolog; a main é só do dono (R-MAIN)")
    return linhas[0][0] if linhas else None


def corpo_do_pr(versao, ref, base):
    return (f"## Projeto de origem\nForge (promoção da fábrica, {ref} para {base}, versão {versao}).\n\n"
            f"## Situação observada\nA develop tem commits que a homolog não tem; pareceres, versão e CHANGELOG conferidos por "
            f"scripts/promover-homolog.py.\n\n## O que muda\nO conjunto de {base}..{ref}; ver o diff.\n\n"
            "## Como medir\nBateria completa do PR e checks verdes; o merge é do tech-lead (merge commit, R-FLUXO).\n\n"
            f"## Checklist\n- [ ] Rótulo `{ROTULO}` pedido ao dono (marque só se a leva afrouxa regra protegida; o dono aplica o rótulo)\n")


def ler_checks(gh, numero):
    """Só os checks do evento pull_request do PR: os do push da develop (mesmo sha) não são a bateria do PR."""
    cod, saida = ler(gh, "pr", "checks", numero, "--json", "name,bucket,event,link", tentativas=1)
    try:
        todos = json.loads(saida)
    except ValueError:
        todos = None
    if not isinstance(todos, list):
        return None, [], saida
    estados, linhas = [], []
    for c in todos:
        if not isinstance(c, dict) or c.get("event") != "pull_request":
            continue
        m = re.search(r"/runs/(\d+)/job/(\d+)", str(c.get("link", "")))
        run, job = m.groups() if m else ("?", "?")
        estados.append((c.get("name"), c.get("bucket")))
        linhas.append(f"check {c.get('name')} {c.get('bucket')} run={run} job={job}")
    return estados, linhas, saida


def promover(args):
    ref, base = args.ref, args.base
    if args.dry_run:
        print("promover-homolog --dry-run: nada será escrito (sem fetch, sem gh, sem PR); passos 1 a 3 leem as refs locais.")
    else:
        git("fetch", "origin")
    conferir_refs(ref, base)
    print("[1] refs conferidas")
    conferir_pareceres(ref, base)
    print("[2] pareceres na ref")
    versao = conferir_versao(ref, base)
    if versao != versao_de(base):
        conferir_contra_main(ref, versao)
    else:
        print("forge-check pr: sem versão nova, sem pedido de release; não roda contra a main")
    print("[3] versão, CHANGELOG e forge-check pr contra a main")
    sha = git("rev-parse", ref).stdout.strip()
    comando_merge = f"gh pr merge develop --auto --merge --match-head-commit {sha}"
    if args.dry_run:
        gh = comando_gh()
        print(f"[4] {gh} pr create --base homolog --head develop (só se não houver PR aberto; PR com base que não seja homolog para)")
        print(f"[5] checks: {gh} pr checks <PR> --json (uma leitura; só os do evento pull_request; só pass/skipping passam; pendente sai com 0)")
        print(f"[6] rótulo: catraca vermelha pede o rótulo {ROTULO} do dono; o script nunca o aplica")
        print(f"[7] imprime o comando do tech-lead que liga o merge automático ({comando_merge}); com ele desligado no repositório, mescla com tudo verde; o script não mescla")
        print("dry-run concluído: nada foi alterado.")
        return 0
    gh = comando_gh()
    numero = pr_aberto(gh)
    if numero:
        print(f"[4] PR #{numero} já aberto; reusado")
    else:
        criado = subprocess.run([gh, "pr", "create", "--base", "homolog", "--head", "develop", "--title",
                                 f"chore(promoção): develop para homolog ({versao})", "--body",
                                 corpo_do_pr(versao, ref, base)], capture_output=True, text=True)
        if criado.returncode:
            parar(f"não consegui abrir o PR: {criado.stderr.strip()}")
        numero = pr_aberto(gh)
        if not numero:
            parar("abri o PR, mas não o achei na leitura seguinte; confira no GitHub")
        print(f"[4] PR #{numero} aberto (develop -> homolog)")
    estados, linhas, saida = ler_checks(gh, numero)
    print("[5] checks")
    print("\n".join(linhas))
    if estados is None and saida.strip() and "no checks reported" not in saida.lower():
        parar(f"não consegui ler os checks: {saida.strip()}")
    if not estados:
        print("nenhum check do evento pull_request apareceu ainda; o merge automático espera os checks.")
        print(f"head: {sha}")
        print(f"[7] liga o merge automático (o tech-lead não espera os checks): {comando_merge}")
        return 0
    vermelhos = [(n, e) for n, e in estados if e not in OK and e not in PENDENTES and not (n == CATRACA and e == "fail")]
    if vermelhos:
        parar("check vermelho ou desconhecido: " + ", ".join(f"{n}={e}" for n, e in vermelhos) + "; corrija e rode de novo")
    pendente = any(e in PENDENTES for _, e in estados)
    if any(n == CATRACA and e == "fail" for n, e in estados):
        cod, rotulos = ler(gh, "pr", "view", numero, "--json", "labels", "--jq", ".labels[].name")
        if cod:
            parar(f"não consegui ler os rótulos do PR: {rotulos.strip()}")
        if ROTULO in rotulos.split():
            print(f"[6] rótulo {ROTULO} aplicado, mas a catraca ainda está vermelha (leitura velha?); rode de novo")
        else:
            print(f"[6] a catraca está vermelha: a leva toca caminho de controle; o dono aplica o rótulo {ROTULO} (o script nunca o aplica)")
        return 3
    print(f"[6] rótulo: a catraca não pede o rótulo {ROTULO}")
    if pendente:
        print("checks ainda pendentes; o merge automático espera os checks.")
        print(f"head: {sha}")
        print(f"[7] liga o merge automático (o tech-lead não espera os checks): {comando_merge}")
        return 0
    print("checks verdes.")
    print(f"head: {sha}")
    print(f"[7] pronta para o merge do tech-lead; este script não mescla. Liga o merge automático: {comando_merge} (com ele desligado no repositório, o comando recusa: mescle com tudo verde)")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="promover-homolog", description="Prepara e confere a promoção develop -> homolog.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ref", default="origin/develop")
    ap.add_argument("--base", default="origin/homolog")
    args = ap.parse_args()
    topo = git("rev-parse", "--show-toplevel", ok_vazio=True)
    if topo.returncode:
        parar("rode dentro do repositório do Forge")
    os.chdir(topo.stdout.strip())
    try:
        nome = json.loads(Path(".claude-plugin/plugin.json").read_text(encoding="utf-8")).get("name")
    except (OSError, ValueError):
        nome = None
    if nome != "forge":
        parar("este não é o repositório do Forge (sem .claude-plugin/plugin.json com name forge); a promoção é do tech-lead no Forge (R-CONTRIB)")
    sys.exit(promover(args))


if __name__ == "__main__":
    main()
