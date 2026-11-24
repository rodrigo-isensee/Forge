"""Forge: `forge-check pronto`, o portão de entrega do autor (D2-PORTAO-ENTREGA-AUTOR, v0481 E11.1; estudo determinístico de 24/11).

O autor roda na raiz da cópia antes de entregar; as revisões só começam depois que passa. Reúne num comando as checagens que já
existem soltas, sem regra nova: os registros (`forge-testes --registros`: índice do Forge, fragmento de changelog, specs de mutante,
pesos), a neutralidade com os dois detectores (as classes Neutralidade e NeutralidadeDoNucleo de tests/test_forge.py), os tetos de
texto (`forge-testes --texto`), os testes afetados (`forge-testes --afetados`), o teto H1 (forge_tamanho) e as seções do corpo do PR
(o passo pr-texto da catraca, o mesmo do CI). Saída 0: tudo passou; 1: alguma checagem reprovou. Só biblioteca padrão; não usa nada
do forge-check (quem chama passa a base comum, o tamanho e o corpo).
"""
import os
import subprocess
import sys

import forge_tamanho

LINHAS_DA_SAIDA = 40  # o fim da saída da checagem reprovada, no stderr


def passos(base):
    """[(nome, argv)] das checagens externas, da mais barata à mais cara; rodam na raiz da cópia."""
    py = sys.executable
    return [("registros", [py, "bin/forge-testes", "--registros", "--base", base]),
            ("neutralidade", [py, "-m", "unittest", "-q", "tests.test_forge.Neutralidade", "tests.test_forge.NeutralidadeDoNucleo"]),
            ("texto", [py, "bin/forge-testes", "--texto"]),
            ("testes", [py, "bin/forge-testes", "--afetados", "--base", base])]


def rodar(raiz, argv, env=None):
    """(código, stdout e stderr juntos) do `argv` na `raiz`, sem stdin; o comando que não abre sai com código 2."""
    try:
        r = subprocess.run(argv, cwd=raiz, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env)
    except OSError as erro:
        return 2, f"{type(erro).__name__}: {erro}"
    return r.returncode, r.stdout + r.stderr


def tamanho_e_corpo(raiz, ancora, total, corpo):
    """Falhas do teto H1 e do pr-texto da catraca sobre o `corpo` do PR; `corpo` None (sem --corpo e sem PR aberto) reprova."""
    if corpo is None:
        return ["corpo do PR não conferido: passe --corpo <o arquivo do --body-file> ou abra o PR em rascunho antes"]
    falhas = []
    if not forge_tamanho.tem_motivo(corpo, total) and (aviso := forge_tamanho.aviso_de_linhas(total)):
        falhas.append(aviso)
    rc, saida = rodar(raiz, [sys.executable, "-I", "tests/catraca.py", "--modo", "pr-texto", "--base", ancora],
                      dict(os.environ, PR_BODY=corpo))
    if rc:
        falhas.append(f"pr-texto da catraca reprovou o corpo (saída {rc}; o CI reprova igual):\n{saida.rstrip()}")
    return falhas


def conferir(raiz, base, ancora, total, corpo, lista=None):
    """Roda os `passos` (ou a `lista` dada) e o teto com o corpo; uma linha `pronto:` por checagem. Devolve 0 ou 1."""
    reprovadas = []
    for nome, argv in passos(base) if lista is None else lista:
        rc, saida = rodar(raiz, argv)
        print(f"pronto: {nome}: {'ok' if rc == 0 else f'reprovado (saída {rc})'}")
        if rc:
            print("\n".join(saida.rstrip().splitlines()[-LINHAS_DA_SAIDA:]), file=sys.stderr)
            reprovadas.append(nome)
    falhas = tamanho_e_corpo(raiz, ancora, total, corpo)
    print(f"pronto: tamanho e corpo do PR ({total} linhas de código): {'reprovado' if falhas else 'ok'}")
    for falha in falhas:
        print(f"pronto: {falha}", file=sys.stderr)
    if falhas:
        reprovadas.append("tamanho e corpo do PR")
    print(f"pronto: reprovado em {', '.join(reprovadas)}; corrija antes de pedir as revisões" if reprovadas
          else "pronto: tudo passou; a entrega pode ir às revisões")
    return 1 if reprovadas else 0
