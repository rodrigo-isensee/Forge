---
tipo: plano-tecnico
contrato: 1
pedido: <id-do-pedido>
estado: proposta
ux: docs/ux/<feature>.md
adrs: [0001]
agentes: [<agente-da-stack>, <agente-da-stack>]
gatilhos_seguranca: []
---
# Plano técnico: <feature>

Copie para `docs/architecture/features/<feature>.md`. Formato: ADR 0004 do Forge; `forge-check docs` valida. `gatilhos_seguranca` lista os gatilhos da `R-SEGURANCA` que o diff não mostra (autenticação, dados pessoais, webhook...); vazio = sem gatilho de segurança. Seção "CI/CD" opcional, com o `devops-engineer`, quando o pedido toca pipeline ou infra.

## Módulos afetados, contratos, riscos e tarefas por agente

## Critério de parada
Em analisador, hook ou segurança, declare antes da implementação (PAR-P2): a frase do que bloqueia, uma linha por classe de achado (`[a-z][a-z0-9-]{1,30}`; `nova` é reservada) e o oráculo do gatilho. O parecer cita este arquivo em `criterio:` e abre `## Parecer` com `Critério de parada: "<frase>"`; mudança leva `critério mudou: <motivo>` na linha seguinte.
- bloqueia: <frase>
- <classe-id> · <o que a define> · oráculo: <teste ou comando>
- gatilho · oráculo: <teste ou comando>
