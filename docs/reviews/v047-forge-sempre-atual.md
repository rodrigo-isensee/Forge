---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-forge-sempre-atual
commit: b89aa7ed43a1c96daf2250a0d312e6359717f935
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Code review: FORGE-SEMPRE-ATUAL (diretriz 30, ADR 0017), E1.58

Revalidação por delta (E1.58) do parecer reprovado no 2bcad385 (E1.51). Delta lido: `forge-check parecer delta docs/reviews/v047-forge-sempre-atual.md`, intervalo 2bcad385..b89aa7ed, 40 arquivos no domínio (+1307 −52): `bin/forge-upgrade`, `bin/forge_sempre_atual.py`, `bin/forge-testes`, `hooks/conformidade.py` com 21 fixtures `tagv-*`, ADR 0017, specs de mutante (v047-sempre-atual-7 a 10, v0432-integracao-2 e 3) e os testes. A segurança (pre-push da cópia instalada, origem da tag na main, `git tag` e envio de tags no hook) é do `security-engineer` (E1.59); aqui ficam a correção e a forma.

## Achados
- A6 (recomendado) bin/forge-upgrade:173 · a recusa da main tira só o prefixo `origin/`: `--base upstream/main`, `refs/remotes/origin/main` ou o SHA da main passam; hoje só a ferramenta passa a base, e fixa
- A7 (recomendado) hooks/conformidade.py:2575 · o PR leva a atualização na abertura e uma classe de hook (tag no Forge); vale uma classe por PR em `hooks/` (M14) com corpus próprio, que ela tem: o corpo do PR a nomeia no teto

## Parecer
Aprovado. O A1 (bloqueante no 2bcad385) está resolvido como sugerido, em bin/forge_sempre_atual.py:816 e bin/forge-upgrade:164; o `ModeloComUpgradeDeVerdade` roda o forge-upgrade real nos casos S1 e S2. Os recomendados A2 a A5 seguem como no parecer anterior, sem mudança no delta. A correção: base explícita no `forge-upgrade` (`switch --no-track -c`, mesclagem e squash conferidos contra a mesma `ref_base`, sugestão de PR com a base sem o prefixo do remoto) e a ferramenta passando a `origin/develop`, com o forge-upgrade de verdade nos testes. Os `git` da ferramenta passam a rodar com `core.hooksPath` em `/dev/null` (`SEM_HOOKS`), somado ao ambiente de lista positiva. A `tag_na_main` falha fechada (init, busca e ancestral). O `bin/forge-testes` mapeia o `forge-upgrade` para o `test_sempre_atual`.

Verificações: `python3 -m unittest tests.test_sempre_atual tests.test_forge_mutante.ConferirTodas tests.test_ambiente_git` no b89aa7ed: `Ran 105 tests in 85.461s`, `OK`. Mutante do A1 (tirar `"--base", "origin/develop"` de bin/forge_sempre_atual.py:816): `tests.test_sempre_atual.ModeloComUpgradeDeVerdade` `Ran 3 tests`, `FAILED (failures=3)`; restaurado. A suíte inteira fica para o CI do PR. Teto (M14): o motivo segue no corpo do PR, com `teto: excedido`, somando o delta.
