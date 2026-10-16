### Alterado
- Os 882 fixtures de hook de tests/test_hooks.py rodam em paralelo (ThreadPoolExecutor, até 4 trabalhadores); os 18 que dependem de PID ou da trava do hook pesado seguem em série. test_hooks caiu de 84-114 s (série) para 32-39 s (duas das três execuções; a terceira, 74 s, com a máquina ocupada).
