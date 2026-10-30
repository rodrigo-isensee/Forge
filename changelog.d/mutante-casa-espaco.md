### Corrigido
- forge-mutante --cobertura: o mutante cujo de e para dividem o espaço junto da condição (prefixo e sufixo comuns sobrepostos, como ' and False' inserido depois da condição de um ternário) conta como coberta quando alguma posição do trecho trocado cai no nó; antes saía 'sem mutante' por um byte depois do fim do nó (MUTANTE-CASA-ESPACO, MUTANTE-COBERTURA-TERNARIO, FM1).
