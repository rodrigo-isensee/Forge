---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 9b075525eaa2a3cadf408e77bafbe5e1817884ab
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E3.21 (melhoria/v0478-guardas-parecer), volta 3 do E3.12

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo b989773a..9b075525 (E3.19: 26262d6d, 652f4bd3, c98f3534, 9dd330f2, 65f4031d, 9b075525, e o merge 014f3e53). No domínio: `hooks/parecer.py` (`mexidas_na_linha`, `nome_incerto`, `mexe_no_config_do_git`, `linha_mantem_os_remotos`, `remotos_incertos`, `pasta_do_gh`, `conferir`), a matriz D1 a D7 em `docs/hooks.md`, o gerador `tests/test_hooks_parecer_matriz.py`, as specs `v0478-guardas-parecer-{5,8,9}.json`, `bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/pesos-d4.json` e o fragmento `changelog.d/`. Nada fora do delta relido.

## Achados
- A5 (bloqueante) hooks/parecer.py:646 · `${N:=v}` e `${N=v}` não contam como mexida: `set -a; : ${GH_REPO:=dono/forge}; gh pr ready feature/x` dá 0 na cópia alheia sem parecer (S28), e o bash exporta o GH_REPO; XDG_CONFIG_HOME e GIT_* idem (S29); a matriz não tem a forma (R-REVIEW).

## Sondas
- S18 · cópia alheia da montagem do gerador (`incidente-r-copia-alheia-source-gh-repo-ready-bloqueia`), `command -p . ./env.sh; gh pr ready feature/x` · espera: código 2 · obtido: código 2 (GH_REPO mexido)
- S26 · mesma montagem, `command -- . ./env.sh; gh pr ready feature/x` · espera: código 2 · obtido: código 2 (GH_REPO mexido)
- S25 · mesma montagem, `gh pr ready feature/x` (controle) · espera: código 0 · obtido: código 0
- S28 · mesma montagem, `set -a; : ${GH_REPO:=dono/forge}; gh pr ready feature/x`, com aspas e com `echo` no lugar de `:` · espera: código 2 · obtido: código 0 nas três (o bash exporta `GH_REPO=dono/forge`)
- S29 · mesma montagem, `set -a; : ${XDG_CONFIG_HOME:=$PWD/x}; gh pr merge feature/x` e `set -a; : ${GIT_CONFIG_GLOBAL:=g.cfg}; gh pr ready feature/x` · espera: código 2 · obtido: código 0 nas duas
- S30 · mesma montagem, `for HOME in $PWD/h; do :; done; gh pr ready feature/x` e `set -a; for GH_REPO in dono/forge; do :; done; gh pr ready feature/x` · espera: código 2 · obtido: código 2 nas duas
- S31 · mesma montagem, `export PATH=bin:$PATH; gh pr ready feature/x` (D7) · espera: código 0 (dimensão aberta) · obtido: código 0

## Conferências
- A3 (meu, E3.16) fechado: S18 e S26 dão 2; o laço de :640 tira as opções depois de `builtin` e `command`.
- A5 já existia no head b989773a (S28 e S29 com o `hooks/parecer.py` da base dão 0): não é regressão do delta, mas é a classe que a E3.19 declara fechada na matriz. Sugestão: em `mexidas_na_linha`, o nome N de toda expansão `${N:=…}` ou `${N=…}` entra em `nomes` (vale a regra de `SENSIVEIS` e `GIT_*` de :646), e a indireta `${!n:=…}` mexe em todos; forma nova na D4 da matriz e no gerador.
- D7 descrita certo: `PATH` fora de `SENSIVEIS` e de `CONFIG_DO_GIT`, a linha `export PATH=bin:$PATH; gh` dá 0 (S31), e `export PATH="$HOME/bin:$PATH"; {gh}` está nos `LEGITIMOS` do gerador; a decisão fica com o dono.
- Mutação dirigida (`bin/forge-mutante`, 1 processo): specs `-8.json` M42 a M49 e `-9.json` M50 a M57 `morreu`, rc=0 nas duas.
- Cobertura (`bin/forge-mutante --cobertura --base b989773a`): as 14 guardas novas `coberta`; `tests/pesos-d4.json` não coberto (dado, sem guarda).
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_matriz`: 5 testes, OK (237 casos gerados, mínimo 190).
- Leitura (checklist 1 a 4, 7, 9, 11): D5 é lista positiva e falha fechada (programa fora da lista, redireção que grava, `leitura.duvida`); a recusa a mais está dita na matriz (`git -c … status`); o gerador afirma mínimo de itens; commits coerentes.
- Tamanho (H1): cerca de 60 linhas de código no delta, um comportamento.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Parecer
Reprovado por A5: forma de dar valor ao GH_REPO e ao config do git na linha que nenhuma dimensão da matriz cobre, com bypass provado (S28, S29). A3 fechado; a matriz D1 a D7 descreve certo o que o código faz, salvo a ausência da forma `${N:=v}`.
