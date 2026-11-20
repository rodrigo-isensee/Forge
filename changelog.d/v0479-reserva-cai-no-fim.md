### Corrigido
- A reserva de escrita do R-TETO cai no fim do agente que a gravou: o disparo guarda o tool_use_id e o início e o fim do agente casam com o toolUseId do meta, em vez de casar pelo tipo e pela ordem (agentes do mesmo tipo disparados juntos trocavam o id e o fim de um soltava a branch do outro e prendia a própria até a expiração; RESERVA-NAO-CAI-NO-FIM). O prazo de expiração não muda.
