### Corrigido
- Os testes de tests/test_oraculo_sempre_atual.py e ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado passam no sandbox do Bash: o oráculo lê os processos vivos de uma árvore montada pelo teste (lançador tests/sem_claude_ancestral.py, opção --proc) e o teste do forge-check usa o gh falso de sem PR; nada de produção mudou (v0481 E27.1).
