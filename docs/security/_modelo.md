---
tipo: revisao-seguranca
contrato: 1
pedido: <id-do-pedido>
branch: <branch>
commit: <hash do HEAD revisado>
parecer: aprovado
revisor: forge:security-engineer
data: AAAA-MM-DD
---
# Review de segurança: <pedido>

Copie para `docs/security/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Arquivos que começam com `_` ou sem frontmatter (postura, modelo de ameaças) são ignorados. Exigido quando há gatilho (`R-SEGURANCA`). `parecer: riscos-aceitos` só vale se o usuário escrever, à mão, `docs/security/aceites/<pedido>.md` com `pedido: <pedido>`, `commit: <o `commit` deste parecer>` e `aceite: sim` (parecer novo, outro commit, pede aceite novo) (nenhum agente grava essa pasta; `R-SEGURANCA`).

Formato do bloco `## Achados` (lido por máquina em `forge-check brief gerar --volta` e conferido por `forge-check docs`): uma linha por achado, `- A<n> (bloqueante|recomendado) <arquivo>:<linha> · <texto>`, sem quebra de linha nem caractere de controle, com até 300 caracteres no texto; só essas linhas entram no bloco (a prosa fica nas outras seções), e parecer reprovado traz ao menos um `bloqueante`. Parecer aprovado deixa o bloco vazio.

## Gatilhos
Quais gatilhos da `R-SEGURANCA` a entrega toca.

## Achados

## Detalhe dos achados
Por achado, em prosa (fora do bloco `## Achados`): evidência (`arquivo:linha`; nunca o segredo) · caminho de ataque · severidade (crítica, alta, média, baixa, informativa) · correção mínima · esforço (P/M/G) · dono.

## Riscos aceitos e ferramentas
Riscos aceitos e quem os aceitou; ferramentas usadas e as que faltaram no ambiente.
