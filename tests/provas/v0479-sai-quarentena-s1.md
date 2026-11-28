# Prova: sonda S1 sem quarentena, 10 rodadas sob carga (v0478 E37.41)

Comando de cada rodada (12 laços de CPU `while :; do :; done` ativos em 12 CPUs):
`python3 -m unittest tests.test_hooks.Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1 tests.test_hooks.SondaS1ComRelogioFalso`
(a prova real da recusa e as duas da S1 pequena com relógio falso, 3 testes por rodada).

```
nproc=12 load average: 29.96, 21.76, 13.44
rodada 1 rc=0 13s Ran 3 tests in 12.172s  OK 
rodada 2 rc=0 16s Ran 3 tests in 13.805s  OK 
rodada 3 rc=0 13s Ran 3 tests in 11.607s  OK 
rodada 4 rc=0 13s Ran 3 tests in 11.877s  OK 
rodada 5 rc=0 12s Ran 3 tests in 11.422s  OK 
rodada 6 rc=0 16s Ran 3 tests in 13.283s  OK 
rodada 7 rc=0 14s Ran 3 tests in 11.936s  OK 
rodada 8 rc=0 14s Ran 3 tests in 12.318s  OK 
rodada 9 rc=0 14s Ran 3 tests in 11.882s  OK 
rodada 10 rc=0 13s Ran 3 tests in 12.084s  OK 
verdes=10/10
rc=0
```
