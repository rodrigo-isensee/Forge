---
id: R-QA
titulo: Portão de QA
verificada_por: `forge-check classe` e `forge-check pr`; hook `parecer` (parecer em docs/qa/ exigido no PR e no merge nas classes N e C); CI obrigatório
---
# R-QA: Portão de QA

Revisar em: 2027-01-07
Medida: 27 de 52 bloqueantes dos pareceres eram defeito provado; 4 escapes (estudo 0.43.1)

- Classes N e C (`forge-check classe`): nenhum código sai sem aprovação do `qa-engineer`, na mesma passada e no mesmo head do review. Classe T dispensa QA (review e CI bastam).
- A suíte completa roda no CI do PR, obrigatório para o merge; o QA cita o `run` como prova. Local, os cenários do QA, sem rerrodar o SHA.
- O parecer de QA fica em `docs/qa/<pedido>.md`: cenários, resultado real, bugs abertos. O teste que o QA escreve entra pela volta do autor ou num commit de teste; ele não reabre o review.
- Documentação não passa por QA, só o código que a verifica.
- Guarda mudada em código de controle (classe C) pede mutante em `tests/mutantes/` no próprio diff (catraca do CI).
- Bug bloqueante, crítico ou alto bloqueia a entrega e nunca segue aberto (ou vai ao usuário como decisão). Médio e baixo viram cartão no quadro, sem aceite do usuário caso a caso (BUR-B4).
- No máximo 3 voltas por bug; na 3.ª reprovação, o Jarvis leva a decisão ao usuário.
