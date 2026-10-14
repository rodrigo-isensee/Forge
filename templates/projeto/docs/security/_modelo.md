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

Copie para `docs/security/<pedido>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. Arquivos que começam com `_` ou sem frontmatter (postura, modelo de ameaças) são ignorados. Exigido quando há gatilho (`R-SEGURANCA`). `parecer: riscos-aceitos` exige `aceite_usuario: sim` no frontmatter, dado pelo usuário.

## Gatilhos
Quais gatilhos da `R-SEGURANCA` a entrega toca.

## Achados
Por achado: evidência (`arquivo:linha`; nunca o segredo) · caminho de ataque · severidade (crítica, alta, média, baixa, informativa) · correção mínima · esforço (P/M/G) · dono.

## Riscos aceitos e ferramentas
Riscos aceitos e quem os aceitou; ferramentas usadas e as que faltaram no ambiente.
