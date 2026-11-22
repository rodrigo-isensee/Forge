### Alterado
- O container recriado se prepara sozinho também com o Claude Code atual: o preparo do Forge e o do modelo de projeto rodam o instalador oficial (baixado para arquivo, em ~/.local/bin, idempotente, sem custo), põem ~/.local/bin na frente do PATH do bash e o --verificar diz a falta (E119.1)
- O download do instalador do Claude Code só por https e com limite de tempo, a falta dá o comando em dois passos (baixar e depois bash) em vez de curl | bash, e só a linha do export (não um comentário) conta como o ~/.local/bin no PATH do .bashrc (E119.5)
