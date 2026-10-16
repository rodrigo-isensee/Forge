---
id: R-DECISAO
titulo: Uma decisão por vez, com opções e recomendação
verificada_por: conferente (corte de escopo) e revisão (transcrições, ADR 0007)
---
# R-DECISAO: Uma decisão por vez, com opções e recomendação

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Revisão: 2026-10-14.

- Toda decisão que cabe ao usuário (produto, escopo, prioridade, regra de negócio, custo, acesso, exceção a uma regra) é levada **uma de cada vez**: a próxima só depois que ele responder a anterior.
- Cada decisão vem com: o contexto em uma ou duas linhas; **as opções** (A, B, C…), cada uma com o principal prós e contra; e **a recomendação** do time, com o motivo.
- Pendências que dependem do usuário e não são decisões (ex.: mesclar um PR, criar uma conta) vão numa lista curta de ações, separada da decisão.
- Havendo várias decisões na fila, o Jarvis escolhe a que destrava mais trabalho, leva só ela e diz quantas restam.
- **Uma pergunta por vez** em tudo, também no entendimento inicial do pedido: as outras ficam na fila, e a resposta diz quantas restam.
- **Corte de escopo é explícito.** Toda decisão, brief ou entrega que retira algo do escopo original traz a marca literal **"Retira do escopo original"**, o trecho do pedido citado, a justificativa, a consequência e a referência à decisão do usuário que o autoriza. O arquivo do pedido ganha a lista "Fora do escopo". Item pedido que some sem a marca é corte silencioso: o `forge:conferente` o reprova (no brief, `corte: sem marca`; na entrega, `pendente:`).
- Decisões técnicas são do time: decidem, registram (ADR ou relatório) e não viram pergunta ao usuário.
- Vale para o Jarvis e para qualquer agente que fale com o usuário, em todo projeto que usa o Forge.

## Complemento: o que é bloqueante e de onde vem a recomendação
- **Teste de bloqueante.** Uma dúvida só vai ao usuário se as três condições valem **juntas**: (1) existem leituras razoáveis que levam a resultados bem distintos em negócio, dados, interface, escopo, segurança, compatibilidade ou ato irreversível; (2) nem a conversa nem o projeto resolvem; (3) errar custa caro de desfazer. Faltando uma, o time decide e a dúvida vira uma linha "Suposições" no relatório, com a base.
- **O teste não se aplica** a custo (`R-CUSTO`), a acesso e credenciais, a exceção a uma regra (`R-CONFORMIDADE`) nem a fato de negócio que o usuário já declarou: esses casos vão sempre ao usuário, como o primeiro item desta regra manda.
- **Escada da recomendação**, nesta ordem: o que o usuário disse, depois o fato do projeto, depois regra ou ADR, depois prática da fábrica, depois preferência do time.
- **Recomendar sempre, com a base declarada:** toda recomendação diz o degrau da escada que a decidiu. Em escopo, prioridade ou custo, leva a marca "preferência do time", separada dos fatos.
- **Decisão só vale gravada.** Quem recebe a resposta do usuário a grava, no mesmo turno, no arquivo do pedido ou no diário de retomada. Resumo de compactação não autoriza: depois dela, decisão que não está no disco é perguntada de novo.

## Complemento: "tanto faz" e ordem ampla
- **"Tanto faz" e "decidam vocês" viram item `delegado`.** O Jarvis grava a frase literal do usuário e a recomendação adotada, com a base, no arquivo do pedido, no mesmo turno. Esses nunca são delegáveis assim: **custo** (`R-CUSTO`), **acesso**, **exceção a regra** (`R-CONFORMIDADE`) e **ato irreversível**; continuam indo ao usuário.
- **Ordem ampla não confirma.** "Resolva", "acabe tudo" e "pode fazer" só cobrem itens já marcados `confirmado` ou `delegado` no pedido. Item novo ou ato irreversível dentro dela volta ao usuário como pergunta, uma por vez.
