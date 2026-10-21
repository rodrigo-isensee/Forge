### Alterado
- Suíte do Forge em até 4 processos no pre-push e no CI (`scripts/suite-paralela.py`), com guarda de completude contra o `discover`, fila por ordem de chegada (uma suíte por vez, também à mão) e parada só da própria execução (SUITE-PARALELA-D4, SUITE-FILA-JUSTA, PREPUSH-PKILL-ALHEIO).
- O `pre-push` não roda a suíte quando não há ref a enviar (a branch já é igual à remota); o push que só apaga continua rodando (PREPUSH-JA-NO-REMOTO).
