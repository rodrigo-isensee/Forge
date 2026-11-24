---
id: R-REVIEW
titulo: Code review em toda entrega, numa passada
verificada_por: `forge-check classe`, `forge-check pr` e `forge-check parecer delta`; hook `parecer` (no PR e no merge)
---
# R-REVIEW: Code review em toda entrega, numa passada

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: 477 revalidações, 89% sem achado, com o parecer preso ao sha (estudo 0.43.1)

- **Code review** do `tech-lead` em toda entrega, em paralelo ao QA e à segurança, no mesmo head, com o checklist da skill `engineering-practices`. Rigor por classe (`forge-check classe`): `skills/engineering-practices/rigor-por-classe.md`. Os gatilhos de segurança (`R-SEGURANCA`) e de devops valem em qualquer classe.
- **Uma passada:** os portões rodam uma vez, juntos, no fim da implementação; os bloqueantes e o `recomendado` de segurança voltam ao autor numa volta só (`R-QA`).
- Review por outra instância: a instância autora não revisa o próprio cartão.
- **O que bloqueia:** um parecer só reprova (`bloqueante`) por defeito de comportamento provado, por requisito da especificação não atendido ou por segurança com gatilho (`R-SEGURANCA`). Sempre com evidência: repro, teste que falha ou `arquivo:linha`. Estilo, nome, estrutura e preferência são sugestão (`recomendado`); a de review e QA vira cartão depois do merge; a de segurança é corrigida antes. Promover a bloqueante exige a marca `critério mudou:` com o motivo no achado.
- **Parecer preso ao domínio:** o parecer vale enquanto o conteúdo do seu domínio não muda; commit fora do domínio não o invalida. A revalidação lê só `forge-check parecer delta <parecer>`. Bloqueante novo fora dele vira cartão (G1.2). O `commit:` do parecer é o `Revisar-sha:` do brief, não o HEAD com pareceres (`forge-check parecer novo`, AQ-5).
