### Corrigido
- O teste do Ctrl-C na troca do plugin deixa de depender de como a suíte foi lançada: o pre-push roda a suíte em segundo plano e o SIGINT chegava ignorado ao forge atualizar; o terminal simulado volta o SIGINT ao padrão (FLAKY-CTRLC-TROCA).
