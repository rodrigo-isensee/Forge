---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.5
branch: melhoria/v0475-release-0475b
commit: bc538cd3e72db368f73681ed9031c9ce4d5c7063
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: release 0.47.5 sobre o topo da develop, com o MP2/MP4 (E4.27)

branch: melhoria/v0475-release-0475b · head revisado: bc538cd3e72db368f73681ed9031c9ce4d5c7063

Escopo: delta desde o código revisado da release (`74d6ccd9`, parecer `release-0.47.5` aprovado, squash na `develop`), lido como `git diff 95a01e54..bc538cd3`: o PR #655 (MP2/MP4, squash `31b29052`), a marca da versão (#657, `561ec804`) e o `bc538cd3` desta branch.

Gatilhos: hooks (`hooks/_maquina.py`, `hooks/pesado.py`, `hooks/hooks.json`, `hooks/conformidade.json`), estado fora do repositório lido por hooks de todos os projetos (`~/.forge/maquina/`), `bin/forge-status`, `bin/forge-pesado`, `bin/forge-testes`; a release publica a versão usada por todos os projetos.

## Achados

## Sondas

## Detalhe dos achados
Sem achados novos. Conferido:
- `bc538cd3`: só `CHANGELOG.md` (+1 linha na [0.47.5], texto igual ao do fragmento) e a remoção de `changelog.d/v0476-mp2-mp4.md`. Sem código, hook nem workflow. `changelog.d/` fica só com o `README.md`; `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.5.
- `561ec804` (#657): só versão, `CHANGELOG.md`, remoção de fragmentos e pareceres em `docs/`; sem código.
- #655 (MP2/MP4) mesclou o que foi revisado: o parecer `v0476-mp2-mp4` (aprovado, `commit: d7ad2a42`) é ancestral do head mesclado `6889c028`; o tree de `6889c028` é igual ao do squash `31b29052`; o diff próprio da branch fora de `docs/` e `changelog.d/` (`merge-base..d7ad2a42`) é o mesmo do squash (`95a01e54..31b29052`): 26 arquivos, +1183/-45, iguais linha a linha salvo linhas de contexto vindas da `develop` (`tests/test_forge.py`, `bin/forge-testes`). Nenhum commit sem merge da branch depois de `d7ad2a42` toca código.
- Junção `4bb3b48e` (revalidação E3.266 não concluída antes do merge): `git show --remerge-diff` dá só `docs/hooks-fixtures.md` (contagem do índice gerado); `scripts/indice-fixtures.py --conferir` no head: "em dia". As outras junções depois do parecer resolveram só `tests/test_testes_tocados.py` (`7f4cc378`, `f564b0c6`) e `docs/hooks-fixtures.md` (`e6399206`). O resto do código que mudou desde `d7ad2a42` veio da `develop`, já coberto pelo parecer `release-0.47.5`.
- Recomendações abertas que seguem valendo sem recópia (não bloqueiam): `v0476-mp2-mp4` A5 e A7, além das listadas no parecer `release-0.47.5`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados no head: `python3 -m unittest tests.test_changelog` (89, OK) e `scripts/indice-fixtures.py --conferir` (rc 0). A suíte inteira é do CI: a `develop` em `561ec804` (base desta branch) tem 14 checks `success` e 12 `skipped`; o `bc538cd3` ainda não tem CI (sem PR) e a promoção exige o CI do PR verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; o delta desta branch não toca workflow nem código.
