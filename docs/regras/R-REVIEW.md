---
id: R-REVIEW
titulo: Code review antes do QA
verificada_por: revisão e hook `parecer` (parecer em docs/reviews/ exigido no PR e no merge na integração)
---
# R-REVIEW: Code review antes do QA

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- **Code review** do `tech-lead` em toda entrega, antes do QA, com o checklist da skill `engineering-practices`.
- Parecer em `docs/reviews/<pedido>-<etapa>.md`: aprovado, ou ajustes necessários (arquivo:linha, problema, sugestão, severidade) devolvidos ao agente autor. Correção de lógica é sempre do autor.
- O review é de uma instância que não implementou o cartão: a instância autora não revisa o próprio cartão, nem reaproveitada do contexto da implementação.
- Todo cartão passa pela coluna Code review antes da coluna QA; nenhuma das duas é pulada, nem para bug, ajuste ou correção de segurança.
- Entrega que toca pipeline, contêiner ou IaC (`.github/`, `Dockerfile*`, `compose*`, pasta de IaC) tem também o parecer do `devops-engineer` em `docs/devops/<pedido>.md` (`tipo: revisao-devops`), em rodada única com este: o `tech-lead` cita o parecer no dele. O hook `parecer` o exige.
- **O que bloqueia:** um parecer só reprova (`bloqueante`) por defeito de comportamento provado (teste, comando ou cenário que falha), por requisito da especificação não atendido ou por segurança com gatilho (`R-SEGURANCA`). O resto (estilo, nome, estrutura, preferência) é recomendação (`recomendado`) e não devolve a entrega. Promover recomendação a bloqueante, numa volta ou numa revalidação, exige a marca `critério mudou:` com o motivo no achado; sem a marca, a promoção não vale.
