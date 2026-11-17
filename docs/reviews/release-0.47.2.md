---
tipo: review
contrato: 1
pedido: release-0.47.2
branch: melhoria/v047-release-0472
commit: b57bb55861115f7b9b5236d4349b4807fe842aa8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: release-0.47.2

Marca da 0.47.2 no head b57bb558 (v047 E2.518), sobre a develop 86ac0fcb. Parecer completo: não havia parecer anterior deste arquivo.

## Achados
- A1 (recomendado) CHANGELOG.md:53 · O #576 (CI-RAPIDO, .github/workflows/ci.yml) entrou na develop só com parecer de devops, sem review, QA nem segurança no squash (R-REVIEW, R-QA). Saiu pelo revert do #604, com pareceres; efeito nulo na 0.47.2, mas o merge sem portão fica registrado.

## Sondas

## Parecer
Aprovado. O commit b57bb558 só toca `CHANGELOG.md` (48 linhas na entrada `[0.47.2] - 2026-11-16`), sobe `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` de 0.47.1 para 0.47.2 e apaga os 37 fragmentos de `changelog.d/`. Cada fragmento apagado tem o texto na entrada (conferido um a um contra o 86ac0fcb); `[Não publicado]` fica vazio e `changelog.d/` só traz o README (`forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes`). Sem código nem teste no diff; sem guarda, sem mutante a declarar.

Leva da develop desde a v0.47.1 (38 commits de primeiro pai, `v0.47.1..86ac0fcb`, todos squash): 37 trazem parecer de review aprovado próprio no commit; os de código trazem também QA e segurança. Os que trazem só review são de docs ou só de teste (#596, #591, #589, #578, #570, #568), e o #600 (proposta em docs) traz review e segurança. Sem portão: só o #576 (A1), revertido por inteiro no #604 (o diff `22f1eaa8^..86ac0fcb` nos 28 arquivos dele só difere em `docs/engineering/achados-recorrentes.md`, por commits posteriores, como diz `docs/security/v047-reverte-576.md`).

Medidas (não portão): `scripts/placar-mutacao.py --desde v0.47.1 --versao 0.47.2`: `placar: 0.47.2 mortos=62 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 specs=9` (51 specs fora da amostra). `forge-check decisoes --sem-cartao`: `sem-cartao=765 sem-id=1741 com-cartao=387 encerradas=25`. Bench não rodado aqui.

Testes só dos arquivos tocados (ordem do dono de 16/11): `python3 -m unittest tests.test_changelog tests.test_conferir_release` (104 testes, OK) e `tests.test_forge.Manifestos`, `ManifestoDoPlugin`, `PluginDeDesenvolvimento` (12 testes, OK). `forge-check docs`: rc=0. A suíte completa fica no CI do PR. A1 não entra em `achados-recorrentes.md`: primeira ocorrência da classe.
