### Adicionado
- B19a (E20): `forge-check juncao <pedido> --ref <branch> [--base develop]` lista as partes da junção da versão (os segundos pais dos merges da primeira linha de pais desde a `origin/<base>`); merge da base não é parte, merge de mais de dois pais sai com rc 1 e git que falha com rc 2. Só leitura.
