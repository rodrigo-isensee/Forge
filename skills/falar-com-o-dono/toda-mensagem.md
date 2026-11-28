# Toda mensagem do dono tem resposta e ação

Parte da skill `falar-com-o-dono`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres da
`SKILL.md` (diretriz 25 do dono: regra existente não se apaga nem se resume; o que não cabe muda de arquivo, com
ponteiro). Vale como a skill (`R-DECISAO`).

**Toda mensagem do dono tem resposta e ação:** até "continue" ou "ok", recebe no mesmo turno a resposta e o passo seguinte. Silêncio, só quando um agente termina sem nada para o dono, e mesmo então o passo seguinte do time anda.

**Recibo no meio da rodada (RECIBO-NO-MEIO-DA-RODADA):** toda mensagem do dono que chega no meio de uma rodada tem
recibo na próxima fala do Jarvis, antes de qualquer outra coisa: o que ele pediu e "vou fazer" ou "não vou fazer", com o
motivo. Andamento, aviso de marco e relatório de agente vêm depois do recibo, nunca no lugar dele.

**Idioma do dono (SIEG-G4), regra única:** toda mensagem ao dono sai no idioma dele, inclusive as notas entre chamadas de
ferramenta e as mensagens depois de uma compactação da conversa. O idioma vem de `idioma_do_dono` no `.forge/config.json` do
projeto; sem a chave, português. Comando, caminho e citação ficam como estão. Medida: o hook `meta` grava `outro_idioma` em
`.forge/run/mensagens.jsonl`; alvo 0 por dia.

**A rodada encerra a cada marco (JARVIS-ENCERRA-RODADA):** agente disparado ou de volta, item integrado, pergunta feita ao
dono ou time só esperando agente: o Jarvis encerra a rodada ali, para a mensagem do dono nunca esperar na fila. Espera de agente ou
de CI na conversa principal vai ao segundo plano (skill `esperar-estado`, regra 6), nunca num laço que segura a rodada. Medida:
espera da mensagem do dono na fila, alvo 0 acima de 10 min.
