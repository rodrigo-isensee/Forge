---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-varredura-divida
commit: 7bfd64e7d4e2d43daa0cb412ee647684ae70c76c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-varredura-divida

Code review da VARREDURA-SEMANAL-DIVIDA (v0478 E95.2) no head 7bfd64e7, base develop 9d5dcb6e: `scripts/varredura-divida.py` (134 linhas, dentro do H1), 12 testes, 22 mutantes em 3 specs e o M19 de `v0475-ci-custo-2` realinhado.

## Achados
- A1 (recomendado) scripts/varredura-divida.py:70 · a guarda olha tests/mutantes/*.json na árvore, mas o forge-mutante --todas lê o HEAD: spec ainda não commitada vira "corrigir a spec que o forge-mutante recusa" (sonda num projeto do forge-init). Ler a lista do HEAD (git ls-tree) ou dizer "spec fora do HEAD".

## Parecer
Aprovado (`R-REVIEW`).

- Projeto do forge-init: `git init` + `bin/forge-init --nome Demo` em pasta de `mktemp -d`, commit, e `python3 -I scripts/varredura-divida.py --mb -1` deu `varredura: 0 achado(s)`, saída 0; o teste `ProjetoDoForgeInit` cobre o mesmo caminho e o MAPA do `bin/forge-testes` liga o `forge-init` a ele.
- Só leitura e sem rede: o script chama só `git rev-parse`, `git for-each-ref`, `du` e `forge-mutante --conferir --todas`; este último vai por `conferir()` (bin/forge-mutante:777), que não passa por `anotar()` nem grava o `.forge/run/testes.log`, e lê o rev com `ls-tree`/`show`. Nenhum `fetch`. Na sonda, `git status --porcelain` vazio depois da varredura; `test_so_le` fotografa a pasta, as refs e o status.
- Realinhamento do M19 (`v0475-ci-custo-2`): a linha 201 do `forge-testes` ganhou `test_varredura_divida`; o `de`/`para` só acompanha o fim da linha e continua tirando o `test_modelo_ci`, a mesma guarda. `forge-mutante ... --ids M19`: `M19 · morreu · bin/forge-testes:201`. O M22 novo tira o `test_varredura_divida` da mesma linha e também morre. Nada enfraqueceu.
- Mutantes: os 22 das três specs `varredura-divida*.json` rodados aqui, todos `morreu`. `tests.test_varredura_divida`: 12 testes, OK. Os testes limpam o git herdado (`sem_git_herdado`) e chamam o script com `python3 -I` (AR-4).
- Suíte inteira não rerrodada (fica no CI). O `test_forge ... test_raiz_depois_do_subcomando_e_git_isolado` falha também na base por ambiente, segundo o brief; fora deste diff.
- A1 é recomendado: o achado sai (não some), só com o texto errado, e o docstring avisa "no HEAD".
