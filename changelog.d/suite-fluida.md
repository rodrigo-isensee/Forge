### Alterado
- A suíte do Forge (`scripts/suite-paralela.py`) fica fluida: um processo por módulo, e o número em paralelo sobe e desce durante a execução conforme a CPU ocupada por outros processos e a memória (de min(2, nproc) a nproc, sem o teto fixo de 4); `FORGE_SUITE_PROCS` fixa de 1 a nproc (SUITE-FLUIDA, afrouxa R-TETO).
