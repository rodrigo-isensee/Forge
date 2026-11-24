---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp9-desenho
commit: 35d78247fb8141a9932bb1ad32f3b342c347f593
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E153.2, desenho BP9)

Classe T, só documento: `docs/propostas/bp9-identidade-agentes.md` (74 linhas, novo) e `changelog.d/v0480-bp9-desenho.md`. Base develop e15c8566; diff de 76 linhas, nenhum hook, script, teste, workflow nem modelo.

## Conferência

- Linhas citadas, lidas na develop e15c8566: `docs/adr/0008-governanca-de-contribuicoes.md:17` (conta de máquina, dono só aprova, rotula e mescla na `main`), `docs/adr/0009-conformidade-dos-agentes.md:63` (`GH_TOKEN` no `env` do dono, `GIT_CONFIG_*` no `env` do projeto, `denyRead`, autor do `~/.gitconfig`, squash da `main`) e `:89` (classic `repo`, fine-grained não alcança conta pessoal), `agents/devops-engineer.md:30`, `agents/security-engineer.md:32`, `docs/adr/0010-agentes-devops-e-seguranca.md:16` (sem escopo `workflow`) e `docs/token-dos-agentes.md` passo 3 (classic, 90 dias, só `repo`): todas batem com o que o desenho afirma.
- `R-CUSTO`: nada pago; conta e App gratuitos, App privado fora do Marketplace, sem runner nem serviço novo, testes do gerador sem rede (seção 7).
- Decisões do dono: D0, D1, D2 e D4 trazem opções, recomendação e motivo; D3 é a troca de trava pedida pela regra do dono de 21/11 (item 3), com a trava que sai nomeada, mas sem a linha de recomendação (A2). Coerente com a decisão do dono de 20/11 (BP2 D1 c: reabre quando o Forge for para organização, pela BP9), que o desenho reflete na opção B.
- Cada fatia diz se é trava e qual sai (C1 não é trava; C2 tira a renovação manual; C3 formaliza a atual); critérios de pronto testáveis; casos de abuso por fatia.
- Ferramentas: `bin/forge-check docs` saída 0; `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.NeutralidadeDoNucleo tests.test_changelog`: 97 testes, OK. Suíte inteira fica no CI do PR.

## Achados
- A1 (recomendado) docs/propostas/bp9-identidade-agentes.md:3 · a origem `docs/propostas/boas-praticas-1911.md` não existe na develop e15c8566 (só na pasta de contribuição); quem lê o repositório não acha a linha BP9. Citar o pedido v0478 como origem ou versionar a revisão.
- A2 (recomendado) docs/propostas/bp9-identidade-agentes.md:65 · D3 não traz `Recomendação`, contra o formato fixo da linha 60; sugerir "sim, trocar", que segue de D1 (c).

## Parecer
Aprovado. O desenho confere com a develop, não custa dinheiro, declara a troca de trava e deixa as decisões ao dono com recomendação; os dois achados são de texto e viram cartão depois do merge.
