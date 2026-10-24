---
id: R-DECISAO
titulo: Uma decisão por vez, com opções e recomendação
verificada_por: conferente (corte de escopo); vigia (lista do dono não gravada no turno, `entrada-sem-registro`) e revisão (transcrições, ADR 0007); retrospectiva (linhas `MELHORIA:`)
---
# R-DECISAO: Uma decisão por vez, com opções e recomendação

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Revisão: 2026-10-21.

- Toda decisão que cabe ao usuário (produto, escopo, prioridade, regra de negócio, custo, acesso, exceção a uma regra, aumento de tokens ou de tempo de entrega) é levada **uma de cada vez**: a próxima só depois que ele responder a anterior.
- Cada decisão vem com: o contexto em uma ou duas linhas; **as opções** (A, B, C…), cada uma com o principal prós e contra, **se afrouxa o processo** (sim ou não) e o **tempo e os tokens a mais ou a menos** por demanda (faixa e média, marcados `medido`, `estimado` ou `não medido`; a fonte do número está em "Como perguntar" da skill `modo-iniciante`); e **a recomendação** do time, com o motivo.
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
- **Decisão só vale gravada.** Pedido, lista ou decisão do dono é gravado por quem o recebe, no mesmo turno, no arquivo do pedido (`docs/pedidos/`) ou no quadro; o scratchpad da sessão é temporário e nunca guarda o que é do dono. Lista de 3 ou mais itens do turno sem gravação o vigia avisa ao dono (aviso, nunca bloqueio). Resumo de compactação não autoriza: depois dela, decisão que não está no disco é perguntada de novo.

## Complemento: "tanto faz" e ordem ampla
- **"Tanto faz" e "decidam vocês" viram item `delegado`.** O Jarvis grava a frase literal do usuário e a recomendação adotada, com a base, no arquivo do pedido, no mesmo turno. Esses nunca são delegáveis assim: **custo** (`R-CUSTO`), **acesso**, **exceção a regra** (`R-CONFORMIDADE`) e **ato irreversível**; continuam indo ao usuário.
- **Ordem ampla não confirma.** "Resolva", "acabe tudo" e "pode fazer" só cobrem itens já marcados `confirmado` ou `delegado` no pedido. Item novo ou ato irreversível dentro dela volta ao usuário como pergunta, uma por vez.
- **Item `técnico` não depende de ordem.** É decisão do time ("Decisões técnicas são do time", acima): executa sem ordem do usuário. `Suposição` e `no-protótipo` seguem fora da ordem ampla: ela não os confirma.

## Complemento: melhoria vista e entrada direta
- **(a) Linha `Melhoria vista:`.** Todo relatório de agente termina com a linha `Melhoria vista:` (menos o do `forge:conferente`): o problema, a evidência (arquivo e linha, saída de ferramenta ou transcrição) e a mudança sugerida, ou `nenhuma`. Sem evidência vale `nenhuma`; não se inventa melhoria para preenchê-la.
- **(b) Retrospectiva.** O Jarvis grava no pedido, no mesmo turno, cada linha diferente de `nenhuma` como `MELHORIA: <agente>: <texto>`. Na retrospectiva o `agile-coach` classifica cada uma em `cartão`, `ao usuário` (com o critério que falhou) ou `descartada` (sem evidência ou duplicada, citando o cartão que a cobre), e o Jarvis abre os cartões.
- **(c) Entrada direta na fila, sem perguntar ao usuário,** só com as quatro condições juntas: não custa dinheiro real, sem exceção (`R-CUSTO`); não afrouxa controle (`R-CONFORMIDADE`), regra nem item de `tests/config.json`; não é decisão de produto; não aumenta tokens nem tempo de entrega dos pedidos seguintes (por exemplo, passo, rodada, agente ou texto lido a cada delegação). O usuário fica sabendo no resumo da etapa.
- **(d) Faltando uma condição, ou na dúvida,** vai ao usuário como decisão, com o aumento estimado; melhoria que custa dinheiro real não entra na fila.
- **(e) Vale igual em todo projeto que usa o Forge:** melhoria técnica do projeto entra no quadro do projeto; melhoria de fábrica vista num projeto só vira proposta por PR no Forge (`R-CONTRIB`).
