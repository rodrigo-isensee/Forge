---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-k167-ato-do-dono
commit: b9974f7561240393a660c841699a65fee99064e4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E74.3, K167)

Escopo: diff `8caa7f3d..b9974f75` (3 arquivos, só texto): `skills/modo-iniciante/SKILL.md`, `skills/ci-cd/SKILL.md`, `changelog.d/v0479-k167-ato-do-dono.md`.

## Gatilhos
Gatilhos: controle da fábrica (R-MAIN, R-CONFORMIDADE citadas em skill), configuração do GitHub (leitura de proteção e rulesets).

## Achados

## Sondas

## Detalhe dos achados
- `skills/modo-iniciante/SKILL.md:35`: endurece. A opção de pergunta sobre ato do dono (merge na `main`, rótulo de PR da `main`, arquivo travado, configuração do GitHub) passa a dizer que quem aplica é o dono e proíbe opção que ponha o agente para aplicá-lo, citando `R-MAIN` e `R-CONFORMIDADE`. As linhas 22 e 29 (não orientar contorno; a `main` é do usuário) seguem intactas.
- `skills/ci-cd/SKILL.md:8`: o encurtamento da abertura tirou só a frase descritiva ("Princípios genéricos e o padrão da fábrica") e o fecho "aqui só o que é da mecânica da entrega"; nenhum dos dois carregava regra de controle. A remissão à skill `cyber-security` continua.
- `skills/ci-cd/SKILL.md:29` (item 9, `R-MAIN`), `:32` (proteção, rulesets, segredos e `environments` são do dono, `R-CONFORMIDADE`, "proponha, não altere por `gh api`"; token sem escopo `workflow`) e `:45` (nunca afrouxar check, `R-CONFORMIDADE`): intactos. O acréscimo em `:32` só amplia a leitura (rulesets e `rules/branches/<b>` além de `branches/<b>/protection`), fechando o ponto cego de quem conferia só a proteção clássica; as chamadas citadas são de leitura e a frase anterior mantém a proibição de alterar.
- `tests/config.json`: nenhum invariante cobre o texto removido (a única entrada de `modo-iniciante` é a remissão a `numeros.md`, preservada).
- Nenhum caminho de ataque novo: mudança só de texto de skill, sem código, workflow nem configuração.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do diff e de `tests/config.json`. Faltaram no PATH: `gitleaks` e `actionlint` (lacuna; o diff é só prosa de skill, sem credencial nem workflow). Suíte inteira não rodada (só no CI, conforme o brief).
