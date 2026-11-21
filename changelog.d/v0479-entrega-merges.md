### Corrigido
- forge-check entrega: o que o merge da develop trouxe, igual ao merge-base com a develop do git ls-remote (um só, na 1.a linha de pais da develop remota, e com o arquivo presente), sai do escopo do autor (ENTREGA-MERGE-DA-DEVELOP, v0478 E62.10, E62.19)
- forge-check entrega: o merge de um merge de pareceres vale pelo blob do parecer conferido mais novo da história do outro pai que muda o arquivo, o mesmo no outro pai e no merge (ENTREGA-MERGE-DE-PARECER-ANINHADO, v0478 E62.10, E62.19)
- forge-check: o `git ls-remote` da branch só vale pela linha de nome exato; `refs/heads/a/refs/heads/<branch>` não passa pela branch (v0478 E62.19, segurança A1)
