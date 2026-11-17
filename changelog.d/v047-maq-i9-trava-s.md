### Alterado
- Hook `pesado` (MAQ-I9, fatia 2): com o PID vivo, a trava de outra sessão vale até 20 min (`TRAVA_S` = 1.200 s, antes 600 s), acima da suíte em série (até 693 s), sempre limitada por `expiracao_horas`; ocupada, a vez segue pela fila (`ESPERA_S` sem mudança). Com o PID morto, solta na hora, como antes. O `bin/forge-pesado` e o hook `agentes` leem a mesma constante.
