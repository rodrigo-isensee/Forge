---
id: R-SEMPARADA
titulo: O Jarvis não espera com a máquina livre
verificada_por: revisão (retrospectiva do agile-coach) e invariante em `tests/config.json`
---
# R-SEMPARADA: O Jarvis não espera com a máquina livre

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: o Jarvis e quem o conduz. Revisão: 2026-11-05.

- **Com folga no teto de recursos (`R-TETO`), o Jarvis não espera.** Quando as frentes em curso esperam fila, envio, CI, conferência ou o dono, ele puxa na hora o próximo trabalho que não depende das frentes paradas: a etapa seguinte de outro cartão, a próxima versão em dual-track, voltas recomendadas, cartões que destravam o fluxo e retrospectivas.
- **Só para em dois casos:** a máquina no teto de `R-TETO`, ou nada desbloqueado no quadro. Ao parar, diz ao dono qual dos dois é.
- **Não afrouxa portão:** review, QA e conferência seguem valendo, em paralelo ao trabalho puxado; o limite de `R-WIP` também segue.
- Motivo (decisão do dono, 2026-11-05): o Jarvis ficou parado esperando um envio com a máquina livre.
