### Corrigido
- A conferência da entrega (`forge-check entrega`) reexecuta a prova `cmd` com o TMPDIR do ambiente, quando é pasta absoluta do próprio usuário, gravável e fora do repositório; no sandbox, o `mktemp` da prova não cai mais no /tmp somente leitura (E2.316).
