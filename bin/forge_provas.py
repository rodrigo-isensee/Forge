"""Forge: o arquivo de provas da branch, gerado do brief pela lista do script que o CI roda (M15 E5a1; FILA-31 F6, 0.45.5).
Só biblioteca padrão.

Importado pelo `bin/forge-check` só quando `provas gerar --brief B` roda. `ctx` traz do forge-check os nomes que ele
divide com a conferência das provas (`secoes_por`, `CABECALHO_BRIEF`, `PQ`, `argv_do_comando`, `espera_da_pq`,
`carregar_reexecutar_provas`, `caminho_de_brief`, `nome_seguro`, `sem_controle`): uma fonte só para o brief e para o script do CI (C-1).
"""
import re
import sys
from pathlib import Path

TITULO_DAS_PROVAS = "# Provas reexecutáveis da branch"  # fixo e sem o slug: o MARCA_DE_PROVA do script reprova título com cara de prova


def provas_reexecutaveis(texto, script, ctx):
    """(linhas de prova, linhas `fora:`) das PQ `cmd` do `Pronto quando`. Quem decide é só o script (`comando_permitido` e `ler_espera`,
    C-1); o comando vai byte a byte e a espera também, salvo o prefixo `rc=0 e ` (C-4); o motivo do `fora:` é o texto fixo do script (C-9)."""
    secoes_por, CABECALHO_BRIEF, PQ = ctx["secoes_por"], ctx["CABECALHO_BRIEF"], ctx["PQ"]
    argv_do_comando, espera_da_pq = ctx["argv_do_comando"], ctx["espera_da_pq"]
    provas, fora = [], []
    for linha in secoes_por(texto, CABECALHO_BRIEF).get("Pronto quando", []):
        m = PQ.search(linha)
        if not m or (m.group(2) or "").split(",")[0].strip().lower() != "cmd":
            continue
        resto = linha[m.end():]
        comando = re.search(r"`([^`]+)`", resto)
        try:
            argv = argv_do_comando(comando)
        except ValueError:
            argv = []
        motivo = script.comando_permitido(argv)
        espera = espera_da_pq(script, motivo, resto, comando)
        if motivo or espera is None:
            fora.append(f"fora: PQ-{m.group(1)} ({motivo or 'espera recusada pelo ler_espera do script'})")
        else:
            provas.append(f"- PQ-{m.group(1)} (cmd): `{comando.group(1)}` · espera: {espera}")
    return provas, fora


def cmd_provas_gerar(raiz, brief, ctx):
    """Imprime o arquivo de provas da branch (M15 E5a1; não escreve): as PQ do brief no stdout, as `fora:` no stderr. rc 0 com ou sem
    PQ elegível; rc 2 com o brief fora de docs/briefs/, o script do CI que não carrega (C-6) ou o texto gerado que o `ler_provas` recusa (C-1)."""
    carregar_reexecutar_provas, caminho_de_brief = ctx["carregar_reexecutar_provas"], ctx["caminho_de_brief"]
    nome_seguro, sem_controle = ctx["nome_seguro"], ctx["sem_controle"]
    script = carregar_reexecutar_provas()
    if script is None:
        print("provas: não verificável (scripts/reexecutar-provas.py ausente)")
        return 2
    arquivo, _ = caminho_de_brief(raiz, brief)
    try:
        texto = arquivo.read_text(encoding="utf-8")
    except (AttributeError, OSError, UnicodeDecodeError):  # AttributeError: `arquivo` None, fora de docs/briefs/
        print(f"provas: --brief {nome_seguro(sem_controle(brief))}: fora de docs/briefs/, inexistente ou ilegível")
        return 2
    provas, fora = provas_reexecutaveis(texto, script, ctx)
    for linha in fora:
        print(linha, file=sys.stderr)
    if not provas:
        print("provas: nenhuma PQ cmd reexecutável")
        return 0
    gerado = "\n".join((TITULO_DAS_PROVAS, "", "## Provas", "", *provas)) + "\n"
    try:
        script.ler_provas("docs/provas/gerado.md", gerado, Path(raiz))
    except script.Falha as erro:
        print(f"provas: o script do CI recusa o texto gerado; nada impresso ({sem_controle(erro)})")
        return 2
    print(gerado, end="")
    return 0
