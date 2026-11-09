---
id: R-QA
titulo: Portão de QA
verificada_por: `forge-check classe` e `forge-check pr`; hook `parecer` (parecer em docs/qa/ exigido no PR e no merge nas classes N e C); CI obrigatório
---
# R-QA: Portão de QA

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time.

Revisar em: 2027-01-07
Medida: 27 de 52 bloqueantes dos pareceres eram defeito provado; 4 escapes (estudo 0.43.1)

- Classes N e C (`forge-check classe`): nenhum código sai sem aprovação do `qa-engineer`, na mesma passada e no mesmo head do review. Classe T não tem QA: o review e o CI bastam.
- A suíte completa roda no CI do PR, obrigatório para o merge; o QA cita o `run` como prova. Local, só os testes afetados (`bin/forge-testes`) e os cenários do QA.
- O parecer de QA fica em `docs/qa/<pedido>.md`: cenários, resultado real, bugs abertos. O teste que o QA escreve entra pela volta do autor ou num commit de teste; ele não reabre o review (o domínio do review não inclui o teste do QA).
- Documentação não passa por QA, só o código que a verifica.
- Bug bloqueante, crítico ou alto bloqueia a entrega e nunca segue aberto (ou vai ao usuário como decisão). Médio e baixo viram cartão no quadro, sem aceite do usuário caso a caso (BUR-B4).
- No máximo 3 voltas por bug; na 3.ª reprovação, o Jarvis leva a decisão ao usuário.
