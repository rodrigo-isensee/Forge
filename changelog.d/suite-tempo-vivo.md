### Alterado
- scripts/suite-paralela.py imprime no stderr, com flush, o tempo de cada unidade de teste ao terminar e, no SIGTERM, as que ainda rodavam e há quanto tempo; job cortado por timeout deixa o tempo por módulo no log (veredito, ordem e saída final iguais)
