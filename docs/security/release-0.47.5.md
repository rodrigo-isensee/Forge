---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.5
branch: melhoria/v0475-pareceres-release
commit: fc3f2ed87165a80bb10aef78bd525abd7f53e629
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: release-0.47.5 (versão inteira, com o MP2/MP4)

Escopo: a 0.47.5 inteira na `develop` em `fc3f2ed8` (topo de `origin/develop`), desde a 0.47.4 (`v0.47.4` = `3544d4ed`): os itens #642, #644 a #654 e #656 (rodada anterior deste parecer, `commit: 74d6ccd9`, no git), o #655 (MP2/MP4, squash `31b29052`), a marca da versão #657 (`561ec804`) e o #658 (`fc3f2ed8`, junção do MP2/MP4 à 0.47.5). Esta volta só troca o commit revisado para o da `develop` que vai à homolog (E4.31).

Gatilhos: hooks (`conformidade`, `meta`, `agentes`, `doutor`, `_comum`, `_maquina`, `pesado`, `hooks.json`), estado em `~/.forge/maquina/` lido por hooks de todos os projetos, execução de comando e controle novo (`bin/forge-check`, `bin/forge-copia`, `bin/forge_sempre_atual.py`, `bin/forge-cota-ci`, `bin/forge-fechar`, `bin/forge-upgrade`, `bin/forge-status`, `bin/forge-pesado`, `bin/forge-testes`, `scripts/jarvis`, `scripts/instalar-atalho.sh`, `scripts/preparar-estacao.sh`), modelo de CI de projeto e a release usada por todos os projetos.

## Achados

## Sondas

## Detalhe dos achados
Sem achados novos. Delta lido nesta volta:
- `git diff --stat 561ec804 fc3f2ed8`: só `CHANGELOG.md` (+1 linha do MP2/MP4 na [0.47.5]), remoção de `changelog.d/v0476-mp2-mp4.md` e pareceres em `docs/{qa,reviews,security}/`; sem código, hook nem workflow. É o conteúdo que o parecer `release-0.47.5-b` (aprovado, `bc538cd3`) revisou; o `bc538cd3` não existe neste clone (squash no #658), então a igualdade foi conferida pelo delta acima, não pelo tree.
- Até `561ec804`: coberto pelo parecer `release-0.47.5-b` (o #655 mesclou o que o `v0476-mp2-mp4` aprovou, junção `4bb3b48e` só no índice de fixtures) e, antes dele, pela rodada anterior deste parecer (12 itens com parecer próprio aprovado e mesmo patch mesclado).
- Recomendações abertas que seguem valendo sem recópia (não bloqueiam): as listadas na rodada anterior deste parecer e `v0476-mp2-mp4` A5 e A7. `v0475-mp1-mp7` A3 segue com o dono (`R-DECISAO`).
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.5; topo do `CHANGELOG.md` `[0.47.5] - 2026-11-18` com `[Não publicado]` vazio; `changelog.d/` só com o `README.md`.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. Rodado em `fc3f2ed8`: `python3 -m unittest tests.test_changelog` (89, OK) e `scripts/indice-fixtures.py --conferir` (em dia, rc 0). A suíte inteira é do CI: em `fc3f2ed8`, na hora deste parecer, 12 checks `skipped` e 10 `in_progress`; a promoção exige o CI verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; o delta desta volta não toca workflow nem código.
