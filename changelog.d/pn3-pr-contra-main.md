### Alterado
- O `scripts/promover-homolog.py`, na release, roda o `forge-check pr release-<versão> --ref <ref> --base main` antes de abrir o PR `develop` → `homolog` e para, citando a saída, se o parecer de review ou de QA da release estiver desatualizado ou faltando contra a `main`: o parecer velho aparece antes de a versão entrar na `homolog` (pedido PN3-PR-CONTRA-MAIN, P-N3).
