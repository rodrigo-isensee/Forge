---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp15-desenho
commit: f367d8d5bb62657fd24847c92003248a037bff89
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E158.2, desenho da BP15)

Item só de texto (`docs/propostas/bp15-entrega-de-produto.md`, 69 linhas, e `changelog.d/v0480-bp15-desenho.md`, 2 linhas; Base-sha 789fc141), classe T. Nenhum hook, script, teste, modelo ou CI mudou; teto H1 não se aplica (só documentação). PR em rascunho #843.

## Ferramentas citadas
- `python3 -m unittest tests.test_forge.Neutralidade` no head f367d8d5: `Ran 3 tests`, `OK`.
- `python3 -m unittest tests.test_forge.NeutralidadeDoNucleo tests.test_forge.AntiDuplicacao tests.test_changelog` no head f367d8d5: `Ran 96 tests`, `OK`.
- A suíte inteira fica no CI do PR #843.

## Conferência
- Evidência da seção 1 conferida na base: `templates/projeto/.github/workflows/ci.yml` (jobs `mudanca`, `suite`, `ci`; nenhum de preview nem de deploy), seções citadas de `skills/ci-cd` e `skills/observabilidade-incidentes`, `templates/projeto/scripts/pos-release` e `templates/projeto/docs/devops/pos-release.{md,passos}`, `bin/forge-cota-ci`; nenhuma ocorrência de "feature flag" em `skills/`, `agents/`, `docs/regras/`, `stacks/`, `templates/`.
- Fontes da seção 2 relidas hoje em docs.github.com: franquia do Free em dinheiro (USD 12 de computação, 500 MB de artefato, 10 GB de cache) e a regra de `environments` em privado (Pro, Team ou Enterprise; `wait timer` e `required reviewers` só em público nos planos Free, Pro e Team) batem com o texto.
- `R-CUSTO`: o que é pago (Pages em privado, `environments` com aprovação em privado) fica fora do modelo e parado em D1 e D2; o C4a usa a franquia com `retention-days: 3` e tem medida de custo (pronto d).
- `R-NEUTRO`: nenhum nome de projeto, biblioteca, linguagem ou nuvem; escolha de biblioteca e provedor remetida a `stacks/<stack>/` e ADR do projeto.
- Decisões do dono: D1 a D4 trazem opções e recomendação. Regra do dono de 21/11 (item 3): nenhuma fatia é trava, e o texto diz isso em cada uma.

## Achados
- A1 (recomendado) docs/propostas/bp15-entrega-de-produto.md:41 · o pronto (c) do C3 manda reproduzir "a lista de campos proibidos da skill de LGPD", mas skills/cyber-security/SKILL.md:28 só traz o princípio (minimização, base legal), sem lista; o critério não tem fonte. Escrever a lista no modelo uso.md e citar a skill como princípio.
- A2 (recomendado) docs/propostas/bp15-entrega-de-produto.md:63 · "required reviewers pode pedir Enterprise": a fonte (:24) diz que em privado, nos planos Free, Pro e Team, ele não existe, ou seja, exige Enterprise. Trocar "pode pedir" por "exige" e ajustar :49 ("só funciona em repositório privado com plano pago" lê-se como exigência de privado).
- A3 (recomendado) docs/propostas/bp15-entrega-de-produto.md:58 · o caso de abuso do C4a conta com a varredura do BP10 C2, que ainda é pergunta ao dono e pode virar só aviso (bp10-higiene-segredo.md:39). Dizer o que pega o segredo no artefato se o BP10 C2 não entrar (por exemplo, a varredura do CI antes do upload).

## Parecer
Aprovado. O desenho cumpre o cartão BP15: quatro frentes com evidência conferível, fontes atuais relidas e corretas no essencial, corte em fatias independentes com pronto testável e casos de abuso, custo zero com o que é pago isolado em decisão do dono com recomendação, e texto neutro (testes verdes). Os três achados são `recomendado`: ajuste de texto que o autor faz ao abrir a fatia, ou cartão depois do merge; nenhum é defeito com gatilho neste PR, que só tem texto.
