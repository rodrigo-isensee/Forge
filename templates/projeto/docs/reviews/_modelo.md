---
tipo: review
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <o Revisar-sha do brief (o código revisado, sem os commits de parecer)>
parecer: aprovado
revisor: forge:tech-lead
data: AAAA-MM-DD
---
# Review: <pedido>

Copie para `docs/reviews/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Arquivos que começam com `_` são ignorados.

Formato do bloco `## Achados` (lido por máquina em `forge-check brief gerar --volta` e conferido por `forge-check docs`): uma linha por achado, `- A<n> (bloqueante|recomendado) <arquivo>:<linha> · <texto>`, sem quebra de linha nem caractere de controle, com até 300 caracteres no texto; só essas linhas entram no bloco (a prosa fica nas outras seções), e parecer reprovado traz ao menos um `bloqueante`. Parecer aprovado traz só linhas `(recomendado)` ou o bloco vazio.

Formato do bloco `## Sondas` (PAR-P1, conferido por `forge-check docs`): em entrega de analisador ou hook, uma linha por sonda executada que prova um bloqueante, `- S<n> · <comando ou entrada literal> · espera: <resultado esperado> · obtido: <resultado obtido>`, numa linha só, sem caractere de controle, com ` · espera: ` e ` · obtido: ` uma vez cada e até 300 caracteres depois do id; só essas linhas entram no bloco, e sem sonda o bloco fica vazio.

Bloqueio (`R-REVIEW`): `bloqueante` é só defeito provado, requisito ou segurança com gatilho; o resto é `recomendado` e não devolve. Promover recomendação a bloqueante exige `critério mudou:` com o motivo no achado.

Evidência: a evidência não muda para caber (`reproduzido` não vira `visto`); se o achado não cabe nos 300 caracteres, encurte o texto, nunca a prova.

Avisos (o pre-push e o `forge-check docs` barram): cite o ID da regra, sem copiar a frase dela; cada achado em até 300 caracteres de texto (conta o que vem depois do ` · `; o prefixo `A<n> (...) <arquivo>:<linha>` não conta).

## Achados

## Sondas

## Parecer
Aprovado ou reprovado, com a síntese. Cada ajuste vai em `## Achados` (`bloqueante` = bloqueia), com a explicação aqui: arquivo:linha · problema · sugestão · severidade.
