---
tipo: revisao-devops
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <hash do HEAD revisado>
parecer: aprovado
revisor: forge:devops-engineer
data: AAAA-MM-DD
---
# Review de devops: <pedido>

Copie para `docs/devops/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Arquivos que começam com `_` são ignorados. Exigido quando a entrega toca `.github/`, `Dockerfile*`, `compose*` ou IaC (`R-REVIEW`).

Formato do bloco `## Achados` (lido por máquina em `forge-check brief gerar --volta` e conferido por `forge-check docs`): uma linha por achado, `- A<n> (bloqueante|recomendado) <arquivo>:<linha> · <texto>`, sem quebra de linha nem caractere de controle, com até 300 caracteres no texto; só essas linhas entram no bloco (a prosa fica nas outras seções, inclusive as ferramentas usadas), e parecer reprovado traz ao menos um `bloqueante`. Parecer aprovado traz só linhas `(recomendado)` ou o bloco vazio.

Bloqueio (`R-REVIEW`): `bloqueante` é só defeito provado, requisito ou segurança com gatilho; o resto é `recomendado` e não devolve. Promover recomendação a bloqueante exige `critério mudou:` com o motivo no achado.

Evidência: a evidência não muda para caber (`reproduzido` não vira `visto`); se o achado não cabe nos 300 caracteres, encurte o texto, nunca a prova.

## Achados

## Detalhes
Aprovado ou reprovado, com a síntese; por achado, em prosa: arquivo:linha · problema · sugestão. Registre aqui, fora do bloco `## Achados`, as ferramentas usadas (`actionlint`, `shellcheck`, `docker build`) e as que faltaram no ambiente.

## Custo e rollback
Minutos de CI e recursos novos (`R-CUSTO`); procedimento de volta da mudança.
