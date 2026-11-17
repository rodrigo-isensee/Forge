# Ritmo diário, corte por arquivo e teto do time

Detalhe da skill `trabalho-em-paralelo` (diretriz 25: o Jarvis traz o resumo e manda ler este arquivo). Vale no Forge e em todo projeto.

## Ritmo diário (diretriz 32 do dono)
- O time desenvolve o máximo em paralelo, dia e noite, e junta cada item na `develop` assim que fica verde, em lotes de até 3 PRs sem arquivo em comum (`docs/fechamento-integrador.md`, diretriz 26).
- Nunca junta sem os testes verdes nem pela exceção do GitHub (bypass do ruleset).
- Uma vez por dia, de manhã, o dono recebe um PR só para a `main`, com tudo o que está verde na `develop`: a versão do dia (diretrizes 21 e 27). O que entra depois da marca vai para a versão seguinte.
- À noite o Jarvis não escreve ao dono, salvo algo grave que mude prazo ou risco. A mensagem da manhã traz a tabela pedido × entregue, o que precisa do dono e o `resumo:` do placar.
- Não é um PR só de desenvolvimento: cada item segue com revisão e testes próprios.

## Corte do trabalho por arquivo (diretriz 33 do dono)
- Cartões que mexem nos mesmos arquivos vão para o mesmo agente, na mesma branch, um depois do outro, nunca para agentes diferentes em paralelo (`forge-check sobreposicao` diz o arquivo em comum).
- Lote de desenvolvimento: de 3 a 5 cartões pequenos (ou um dia de trabalho), com uma revisão só.
- A junção na `develop` continua como na diretriz 26: até 3 PRs que não mexem nos mesmos arquivos.

## Teto do time (decisão do dono, H6)
- Até 20 agentes ao mesmo tempo, dentro do `R-TETO`, e no máximo 12 branches com trabalho aberto.
- Agente livre termina o que está aberto (revisão, conserto, teste vermelho, CI vermelho) antes de abrir item novo; branch nova só quando uma entra na `develop`.
- A regra de tocar o máximo de itens ao mesmo tempo continua: o máximo vale dentro desses tetos.
