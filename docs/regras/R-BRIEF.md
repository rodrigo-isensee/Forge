---
id: R-BRIEF
titulo: Brief conferido antes da delegação
verificada_por: conferente (modo brief) e revisão (transcrições, ADR 0007); o hook `brief` (selo pelo hash) ainda não existe
---
# R-BRIEF: Brief conferido antes da delegação

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: o Jarvis e quem mantém o Forge. Revisão: 2026-10-14.

- Todo prompt de delegação do Jarvis passa pelo `forge:conferente` no modo `brief` **antes** de chegar ao agente de destino. Isentos: o próprio conferente e os agentes só de leitura, sem escrita nem Bash.
- O brief vai ao conferente literal, exatamente como será enviado. O conferente lê do disco o pedido (`docs/pedidos/<id>.md`) e as decisões registradas, sem depender da paráfrase do Jarvis.
- Ele confere: fidelidade (cada item do "Entregar" vem do pedido ou de uma decisão registrada); decisões do dono e ADRs citadas presentes, sem contradição; corte de escopo marcado (`R-DECISAO`); forma ("Pronto quando" com `PQ-n` e tipo de prova, `R-PROVA`); e a etapa do fluxo, quando o brief manda abrir PR ou mesclar.
- Veredito reprovado: o Jarvis corrige o brief e confere de novo. O agente só recebe o texto aprovado, sem edição depois da conferência.
