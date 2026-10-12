---
id: R-QA
titulo: Portão de QA
verificada_por: revisão (parecer em docs/qa/ exigido no PR)
---
# R-QA: Portão de QA

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- Nenhum código sai sem aprovação do `qa-engineer`, **por entrega**: a suíte completa (unitários, E2E, acessibilidade) roda uma vez a cada entrega.
- Cartão de correção (bug ou ajuste) também passa pelo QA, sem pular coluna, e o QA roda a suíte completa antes de o cartão pai seguir.
- Documentação não passa por testes nem QA, só o código que a verifica.
- O PR exige o parecer de code review (`R-REVIEW`) e o de QA em `docs/qa/<pedido>.md`: cenários, resultado real, bugs abertos.
- Bug bloqueante, crítico ou alto bloqueia a entrega e nunca segue aberto. Médio e baixo só acompanham a entrega com aprovação explícita do usuário, listados no PR como pendências.
- No máximo 3 voltas por bug (rodadas de review ou de QA que o reabrem); na 3ª reprovação, o Jarvis leva a decisão ao usuário.
