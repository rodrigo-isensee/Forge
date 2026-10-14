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
