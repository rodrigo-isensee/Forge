---
id: R-CONFORMIDADE
titulo: Controles não se contornam; o que está em vigor é do usuário
verificada_por: hook, sandbox, permissões, vigia (ADR 0009)
---
# R-CONFORMIDADE: Controles não se contornam; o que está em vigor é do usuário

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Revisão: 2026-10-13. Decisão: `docs/adr/0009-conformidade-dos-agentes.md`.

- **Nenhum agente desliga, enfraquece ou dribla um controle**, seja ele um hook, uma permissão, o sandbox, um teste, o CI ou uma regra, usando um desvio: shell, script, ferramenta alternativa, outro agente ou outra sessão.
- **Bloqueio que impede trabalho legítimo não se contorna:** o agente para, explica o que foi barrado e leva ao usuário como decisão (`R-DECISAO`), com opções e recomendação.
- **Trocar de ferramenta** depois de uma falha só vale para um caminho que não é protegido; se a mesma ação é barrada por outro meio, vale o bloqueio.
- **Arquivos em vigor** (hooks, permissões, política de conformidade, testes e regras) **só o usuário altera**; o time propõe a mudança por PR.
- Tentativa de contorno é registrada e tratada como incidente, não como detalhe técnico.
