# Toda mensagem do dono tem resposta e ação

Parte da skill `falar-com-o-dono`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres da
`SKILL.md` (diretriz 25 do dono: regra existente não se apaga nem se resume; o que não cabe muda de arquivo, com
ponteiro). Vale como a skill (`R-DECISAO`).

**Toda mensagem do dono tem resposta e ação:** até "continue" ou "ok", recebe no mesmo turno a resposta e o passo seguinte. Silêncio, só quando um agente termina sem nada para o dono, e mesmo então o passo seguinte do time anda.

**Idioma do dono (SIEG-G4), regra única:** toda mensagem ao dono sai no idioma dele, inclusive as notas entre chamadas de
ferramenta e as mensagens depois de uma compactação da conversa. O idioma vem de `idioma_do_dono` no `.forge/config.json` do
projeto; sem a chave, português. Comando, caminho e citação ficam como estão. Medida: o hook `meta` grava `outro_idioma` em
`.forge/run/mensagens.jsonl`; alvo 0 por dia.
