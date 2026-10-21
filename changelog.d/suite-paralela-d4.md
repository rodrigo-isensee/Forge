### Alterado
- Suíte do Forge em até 4 processos no pre-push e no CI (`scripts/suite-paralela.py`), com guarda de completude contra o `discover`, fila por ordem de chegada (uma suíte por vez, também à mão) e parada só da própria execução (SUITE-PARALELA-D4, SUITE-FILA-JUSTA, PREPUSH-PKILL-ALHEIO).
