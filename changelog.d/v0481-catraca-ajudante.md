### Corrigido
- catraca: a asserção feita num ajudante do teste (método da classe, da base no mesmo módulo ou função do módulo, até 8 níveis) conta no teste que o chama, e o nome e os argumentos constantes da chamada viram valor esperado; teste sem asserção não pareia mais como renomeado. Tirar a chamada `self.fica()` ou renomear um teste de 0 asserções agora pede o rótulo do dono (v0481 E14.14)
