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

## Complemento: o que é bloqueante e de onde vem a recomendação
- **Teste de bloqueante.** Uma dúvida só vai ao usuário se as três condições valem **juntas**: (1) existem leituras razoáveis que levam a resultados bem distintos em negócio, dados, interface, escopo, segurança, compatibilidade ou ato irreversível; (2) nem a conversa nem o projeto resolvem; (3) errar custa caro de desfazer. Faltando uma, o time decide e a dúvida vira uma linha "Suposições" no relatório, com a base.
- **Escada da recomendação**, nesta ordem: fato do projeto, depois regra ou ADR, depois prática da fábrica, depois preferência do time.
- **Recomendar sempre, com a base declarada:** toda recomendação diz o degrau da escada que a decidiu. Em escopo, prioridade ou custo, leva a marca "preferência do time", separada dos fatos.
- **Decisão só vale gravada.** Quem recebe a resposta do usuário a grava, no mesmo turno, no arquivo do pedido ou no diário de retomada. Resumo de compactação não autoriza: depois dela, decisão que não está no disco é perguntada de novo.
