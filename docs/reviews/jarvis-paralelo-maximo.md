---
tipo: review
contrato: 1
pedido: jarvis-paralelo-maximo
branch: melhoria/jarvis-paralelo-maximo
commit: 7fd503451ad679f2b9aa93984dc0af132e69f7b2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Code review: JARVIS-PARALELO-MAXIMO (regras do dono no Jarvis)

Diff revisado: `f911dfa...7fd5034` (2 commits, 3 arquivos: `agents/jarvis.md`, `tests/config.json`, `changelog.d/jarvis-paralelo-maximo.md`). Brief: `jarvis-paralelo-maximo-tech-lead-3.md`. Ferramentas: suíte e validação do plugin não refeitas aqui (R-TETO; prova do autor, 1194 OK, e conferência do Jarvis). Segurança: parecer próprio do `security-engineer`, não refeito.

## Contra o pedido
- **E1 (paralelo máximo):** cumprido. A frase na seção "Trabalho em paralelo (padrão)" diz que o Jarvis toca sempre o máximo de itens ao mesmo tempo, revê a fila a cada relatório e mudança de estado, espera só por dependência real ou série por arquivo e prepara o brief seguinte em paralelo, "sempre dentro de `R-TETO` e `R-WIP`". Não contradiz R-TETO (o teto continua por máquina, pesado um por vez) nem R-WIP (um cartão por agente), e preserva a série por arquivo em comum da decisão 31 e o `forge-check sobreposicao` logo antes.
- **E3 (alcance das melhorias):** cumprido. A frase em "Fábrica × projeto" generaliza para todos os projetos, com a exceção explícita do dono; não altera a classificação "fica no projeto" que vem depois (exceções locais seguem valendo).
- **E2 (invariantes e fragmento):** os dois trechos novos em `invariantes` de `agents/jarvis.md` existem literalmente no texto (conferido) e quebram o teste se a frase sumir. Fragmento `changelog.d/jarvis-paralelo-maximo.md` no formato, neutro (R-NEUTRO), sem editar o `CHANGELOG.md`.
- Escopo: nada além do pedido. Commits: 2, Conventional Commits em português, coerentes (test, feat).
- R-CUSTO, R-NEUTRO, invariantes anteriores: preservados; nada afrouxado.

## Achados
(nenhum bloqueante)

## Recomendações (não bloqueiam)
- Critério de reversão não se aplica (texto de instrução, não mecanismo novo); reverter é remover as duas frases e os dois invariantes.
- Um único invariante cobre cada frase por um trecho curto; se alguém reescrever mantendo a regra com outras palavras, o teste vai pedir ajuste consciente, o que é o desejado.
