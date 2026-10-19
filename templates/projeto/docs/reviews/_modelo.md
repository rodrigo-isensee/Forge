---
tipo: review
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <hash do HEAD revisado>
parecer: aprovado
revisor: forge:tech-lead
data: AAAA-MM-DD
---
# Review: <pedido>

Copie para `docs/reviews/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Arquivos que começam com `_` são ignorados.

Formato do bloco `## Achados` (lido por máquina em `forge-check brief gerar --volta` e conferido por `forge-check docs`): uma linha por achado, `- A<n> (bloqueante|recomendado) <arquivo>:<linha> · <texto>`, sem quebra de linha nem caractere de controle, com até 300 caracteres no texto; só essas linhas entram no bloco (a prosa fica nas outras seções), e parecer reprovado traz ao menos um `bloqueante`. Parecer aprovado deixa o bloco vazio.

## Achados

## Parecer
Aprovado ou reprovado, com a síntese. Cada ajuste vai em `## Achados` (`bloqueante` = bloqueia), com a explicação aqui: arquivo:linha · problema · sugestão · severidade.
