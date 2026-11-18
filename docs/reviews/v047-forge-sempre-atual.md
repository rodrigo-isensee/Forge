---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-forge-sempre-atual
commit: 008d66c31e331e3bd150cbb487bec5cdcf521c49
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Code review: FORGE-SEMPRE-ATUAL (diretriz 30, ADR 0017), E3.89

Revalidação por delta (E3.89) do parecer aprovado no b89aa7ed (E1.58). Delta lido: `forge-check parecer delta docs/reviews/v047-forge-sempre-atual.md`, intervalo b89aa7ed..008d66c3, escopo sem o que veio da develop. Commits do autor (E1.62): 83928ecf, 3d6f1eb3, b5ac9125 (testes de ramo em tests/test_sempre_atual.py e tests/test_atualizar.py), dcfd49c8 (specs v047-sempre-atual-11 a 35, 200 mutantes, um por condição mudada), c3091397 (isenção da condição apagada do `devolver_original`, motivo E6.5 do ADR 0017) e cdfcf7b7 (seis mutantes trocam o teste genérico pelo que mata o ramo). Merges da develop 28e50dbf e 008d66c3, lidos pelo `--remerge-diff`: bin/forge-testes guarda as entradas da branch e o `test_estado_ilegivel` da develop no `RODAM_OS_HOOKS`; docs/adr/README.md fica com a 0017 e a 0018; docs/hooks-fixtures.md foi regenerado (2913 fixtures). Sem código de produção no delta do autor; nenhum achado novo.

## Histórico
E1.58, no b89aa7ed:

Revalidação por delta (E1.58) do parecer reprovado no 2bcad385 (E1.51). Delta lido: `forge-check parecer delta docs/reviews/v047-forge-sempre-atual.md`, intervalo 2bcad385..b89aa7ed, 40 arquivos no domínio (+1307 −52): `bin/forge-upgrade`, `bin/forge_sempre_atual.py`, `bin/forge-testes`, `hooks/conformidade.py` com 21 fixtures `tagv-*`, ADR 0017, specs de mutante (v047-sempre-atual-7 a 10, v0432-integracao-2 e 3) e os testes. A segurança (pre-push da cópia instalada, origem da tag na main, `git tag` e envio de tags no hook) é do `security-engineer` (E1.59); aqui ficam a correção e a forma.

### Achados no b89aa7ed
- A6 (recomendado) bin/forge-upgrade:173 · a recusa da main tira só o prefixo `origin/`: `--base upstream/main`, `refs/remotes/origin/main` ou o SHA da main passam; hoje só a ferramenta passa a base, e fixa
- A7 (recomendado) hooks/conformidade.py:2575 · o PR leva a atualização na abertura e uma classe de hook (tag no Forge); vale uma classe por PR em `hooks/` (M14) com corpus próprio, que ela tem: o corpo do PR a nomeia no teto

### Parecer no b89aa7ed
Aprovado. O A1 (bloqueante no 2bcad385) está resolvido como sugerido, em bin/forge_sempre_atual.py:816 e bin/forge-upgrade:164; o `ModeloComUpgradeDeVerdade` roda o forge-upgrade real nos casos S1 e S2. Os recomendados A2 a A5 seguem como no parecer anterior, sem mudança no delta. A correção: base explícita no `forge-upgrade` (`switch --no-track -c`, mesclagem e squash conferidos contra a mesma `ref_base`, sugestão de PR com a base sem o prefixo do remoto) e a ferramenta passando a `origin/develop`, com o forge-upgrade de verdade nos testes. Os `git` da ferramenta passam a rodar com `core.hooksPath` em `/dev/null` (`SEM_HOOKS`), somado ao ambiente de lista positiva. A `tag_na_main` falha fechada (init, busca e ancestral). O `bin/forge-testes` mapeia o `forge-upgrade` para o `test_sempre_atual`.

Verificações: `python3 -m unittest tests.test_sempre_atual tests.test_forge_mutante.ConferirTodas tests.test_ambiente_git` no b89aa7ed: `Ran 105 tests in 85.461s`, `OK`. Mutante do A1 (tirar `"--base", "origin/develop"` de bin/forge_sempre_atual.py:816): `tests.test_sempre_atual.ModeloComUpgradeDeVerdade` `Ran 3 tests`, `FAILED (failures=3)`; restaurado. A suíte inteira fica para o CI do PR. Teto (M14): o motivo segue no corpo do PR, com `teto: excedido`, somando o delta.

## Achados
- A6 (recomendado) bin/forge-upgrade:173 · segue como no b89aa7ed; o delta não toca a recusa da main
- A7 (recomendado) hooks/conformidade.py:2575 · segue como no b89aa7ed: o corpo do PR nomeia a classe de hook (tag no Forge) no teto (M14)

## Parecer
Aprovado no 008d66c3. Os 25 specs novos cobrem as condições mudadas da forge-sempre-atual com um mutante por linha; a isenção do `devolver_original` tem motivo e referência ao ADR 0017. Os testes novos que rodam subprocesso usam `sys.executable -I` e ambiente limpo. Recomendado ao autor, sem bloquear: 60 dos 200 mutantes apontam o mesmo `Alvo.test_fixacao_automatica_solta_com_versao_maior_que_a_quebrada`; morrem (amostra abaixo), mas um teste mais perto de cada ramo localiza melhor a falha, como o cdfcf7b7 fez com seis.

Verificações no 008d66c3: `python3 -I scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`. `python3 -m unittest test_indice_fixtures test_sempre_atual test_atualizar test_testes_tocados`: `Ran 419 tests in 545.187s`, `OK (skipped=4)` (pulos do sandbox por /proc de outro namespace). `bin/forge-mutante tests/mutantes/v047-sempre-atual-22.json --rev 008d66c3 --processos 1`: S89 a S96 `morreu` (seis apontam o teste genérico), rc 0. A suíte inteira e a catraca dos mutantes ficam para o CI do PR.
