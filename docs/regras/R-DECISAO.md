---
id: R-DECISAO
titulo: Uma decisão por vez, com opções e recomendação
verificada_por: revisão (transcrições, ADR 0007)
---
# R-DECISAO: Uma decisão por vez, com opções e recomendação

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Revisão: 2026-10-13.

- Toda decisão que cabe ao usuário (produto, escopo, prioridade, regra de negócio, custo, acesso, exceção a uma regra) é levada **uma de cada vez**: a próxima só depois que ele responder a anterior.
- Cada decisão vem com: o contexto em uma ou duas linhas; **as opções** (A, B, C…), cada uma com o principal prós e contra; e **a recomendação** do time, com o motivo.
- Pendências que dependem do usuário e não são decisões (ex.: mesclar um PR, criar uma conta) vão numa lista curta de ações, separada da decisão.
- Havendo várias decisões na fila, o Jarvis escolhe a que destrava mais trabalho, leva só ela e diz quantas restam.
- Decisões técnicas são do time: decidem, registram (ADR ou relatório) e não viram pergunta ao usuário.
- Vale para o Jarvis e para qualquer agente que fale com o usuário, em todo projeto que usa o Forge.
