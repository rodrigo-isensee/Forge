---
tipo: qa
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <o Revisar-sha do brief (o código testado, sem os commits de parecer)>
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: AAAA-MM-DD
---
# QA: <pedido>

Copie para `docs/qa/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Médio ou baixo abertos não bloqueiam o parecer aprovado nem pedem aceite do usuário: cada um vira cartão no quadro (`R-QA`, BUR-B4). Bugs em `docs/qa/bugs/`.

Formato do bloco `## Achados` (lido por máquina em `forge-check brief gerar --volta` e conferido por `forge-check docs`): uma linha por achado, `- A<n> (bloqueante|recomendado) <arquivo>:<linha> · <texto>`, sem quebra de linha nem caractere de controle, com até 300 caracteres no texto; só essas linhas entram no bloco (a prosa fica nas outras seções), e parecer reprovado traz ao menos um `bloqueante`. Parecer aprovado traz só linhas `(recomendado)` ou o bloco vazio.

Bloqueio (`R-REVIEW`): `bloqueante` é só defeito provado, requisito ou segurança com gatilho; o resto é `recomendado` e não devolve. Promover recomendação a bloqueante exige `critério mudou:` com o motivo no achado.

Evidência: a evidência não muda para caber (`reproduzido` não vira `visto`); se o achado não cabe nos 300 caracteres, encurte o texto, nunca a prova.

Avisos (o pre-push e o `forge-check docs` barram): cite o ID da regra, sem copiar a frase dela; cada achado em até 300 caracteres de texto (conta o que vem depois do ` · `; o prefixo `A<n> (...) <arquivo>:<linha>` não conta).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 | CT-01 | vazio, máximo ou `n/a` | passou |

## Cenários e resultado real
