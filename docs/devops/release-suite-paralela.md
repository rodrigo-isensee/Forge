---
tipo: revisao-devops
contrato: 1
pedido: versao-033
branch: melhoria/release-suite-paralela
commit: 6652f6b1898c91866a18e128ddbd1927c76b0277
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: release-suite-paralela

## Parecer
Aprovado, sem achado. Diff de `.github/workflows/release.yml` conferido linha a linha contra a base:

- Suíte: o passo roda `python3 scripts/suite-paralela.py`, o mesmo comando dos jobs `rapida` e `bateria` do `ci.yml`. O script só lê `GITHUB_ACTIONS` e `CI` do ambiente, e ambos existem no runner do Release; não há variável própria do CI a copiar.
- Python: entra `actions/setup-python` com o mesmo SHA fixado (`6d4fd22b...`, v7.1.0) e a mesma `python-version` "3.12" do `ci.yml`.
- Teto: 25 min, igual ao do job `bateria`. Medido no CI (run 41816030187, `gh run view`): o passo da suíte levou cerca de 18,5 min no Python 3.12 e cerca de 12 min no 3.14; a folga é de cerca de 6 min sobre o pior caso. Suficiente e sem custo extra, porque o job só roda a suíte e a publicação.
- Inalterados: gatilho (`push` na `main`), `permissions: contents: write`, checkout (SHA, `fetch-depth: 0`, `persist-credentials: false`) e o passo "Tag e release".
- Teste `test_rapida_e_bateria_rodam_a_suite_pelo_script_dividido` passa a exigir o script e proibir `unittest discover` no Release; a contraprova antiga foi invertida de propósito. Fragmento `changelog.d/release-suite-paralela.md` presente.
- Ferramentas: `actionlint` e `shellcheck` não estão no PATH deste ambiente (lacuna registrada; o CI as roda no PR). Suíte inteira não rodada aqui (D-5).

## Achados

## Custo e rollback
Sem custo novo: runner padrão gratuito, menos minutos que a execução em série. Rollback: reverter o commit restaura o passo em série e o teto de 20 min.
