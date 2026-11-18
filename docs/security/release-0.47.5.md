---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.5
branch: melhoria/v0475-release-0475
commit: 74d6ccd9a74a1b7742ad4b89a289c1539c4a2797
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: release-0.47.5

Escopo: o que entra desde a 0.47.4 (`v0.47.4` = `origin/main` = `3544d4ed`, merge do #643) até `74d6ccd9`: 14 commits, os itens #642, #644 a #654 e #656 mais a marca da versão `74d6ccd9` (só `plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md` e a remoção dos 13 fragmentos de `changelog.d/`, sem código).

Gatilhos: hooks (`conformidade`, `meta`, `agentes`, `doutor`, `_comum`), execução de comando e controle novo (`bin/forge-check` de merge e Revisar-sha, `bin/forge-copia`, `bin/forge_sempre_atual.py`, `bin/forge-cota-ci`, `bin/forge-fechar`, `bin/forge-upgrade`, `scripts/jarvis`, `scripts/instalar-atalho.sh`, `scripts/preparar-estacao.sh`) e modelo de CI de projeto (`templates/projeto/.github/workflows/ci.yml`).

## Achados

## Sondas

## Detalhe dos achados
Sem achados novos. Conferido:
- Cada item com gatilho tem parecer próprio `parecer: aprovado`: `v0475-mp1-mp7` (#642), `v0475-h3-h8` (#644), `v0476-revisar-sha-delta` (#646), `v0476-brief-gerar` (#647), `v0475-copia-pasta` (#648), `v0475-ci-sem-reenvio` (#649), `v047-forge-sempre-atual` (#650), `v0475-ci-custo` (#651), `v0476-conformidade-formas` (#652), `v0475-merge-checks` (#653), `v0475-ci-cota` (#654), `v0475-mp5` (#656). O #645 só toca `tests/` (mutantes das guardas do CI), sem gatilho.
- O que foi mesclado é o que foi revisado: para os 12 itens, o `commit:` do parecer é ancestral do head do PR, o patch do squash na `develop` tem o mesmo `git patch-id --stable` do diff do head do PR (arquivos fora de `docs/{reviews,qa,security,devops,pedidos}/` e `changelog.d/`), e o código que mudou depois do parecer veio só de merges da `develop` (itens já revisados). Os merges com resolução própria (`--remerge-diff`) tocam só `tests/test_testes_tocados.py` (`57737d10`, `d8f33e1b`) e `docs/hooks-fixtures.md` (`f564377f`, `49e720e8`).
- Recomendações abertas dos pareceres de item, que seguem valendo aqui sem recópia (não bloqueiam; sem caminho de ataque fora da própria sessão autorizada): `v047-forge-sempre-atual` A4 a A7 (corrida de tag entre conferência e busca, cobertura do bloqueio de tag, trava por `v*` fora da main, texto da ADR 0017); `v0475-merge-checks` A2 a A5 (falha fechada ou dependente de proteção do destino); `v0475-copia-pasta` A2 (`allowWrite` largo, patch proposto ao dono em `docs/propostas/copia-pasta-settings.patch`); `v0475-mp1-mp7` A3 (Telegram com um bot só, levado ao dono por `R-DECISAO`); `v0476-brief-gerar` A1; `v0476-revisar-sha-delta` A1 e A2; `v0475-ci-custo` A4; `v0475-ci-sem-reenvio` A1.
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.5; topo do `CHANGELOG.md` `[0.47.5] - 2026-11-18`; `changelog.d/` só com o `README.md`.

## Riscos aceitos e ferramentas
Sem riscos aceitos e nenhum pendente de aceite (nenhum parecer da leva em `riscos-aceitos`; não há `docs/security/aceites/`). O `v0475-mp1-mp7` A3 aguarda decisão do dono; se ele não fechar o item, vira risco a aceitar pelo Jarvis (`R-SEGURANCA`, `R-DECISAO`). Os afrouxamentos da leva (#644, #646, marcados `afrouxa-regra`) são decisões do dono, não risco aceito. Testes rodados: `python3 -m unittest tests.test_changelog` (89, OK). A suíte inteira é do CI: a `develop` no `95a01e54` (base desta branch) tem o CI verde (14 checks `success`, 12 `skipped`); o `74d6ccd9` ainda não tem CI (sem PR), e a promoção exige o CI do PR verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; o modelo de CI de projeto foi conferido no parecer `v0475-ci-custo`.
