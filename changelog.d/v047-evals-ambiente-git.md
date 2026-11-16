### Corrigido
- Os evals de regressão de forma rodam o forge-check e o git sem as variáveis GIT_* herdadas e com Python -I (sem_git_herdado em tests/ambiente_git.py); antes, sob um GIT_DIR exportado por hook, a classe FragmentoDoChangelog dava erro (AR-4).
