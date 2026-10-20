### Alterado
- Catraca: quando o `git diff` que lista os arquivos alterados falha, a catraca fica vermelha com a mensagem "não consegui listar os arquivos alterados" (falha fechada; o rótulo `afrouxa-regra` não libera esta violação), em vez de tratar como "nada mudou"; `scripts/conferir-release.py` passa a ser arquivo protegido e pede o rótulo do dono (CATRACA-ENDURECER).
