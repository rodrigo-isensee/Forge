---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-devcontainer-sem-gh
commit: a5f6c0f1343dbad87df1f227b647e9c0e8460515
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 E35.7 (DEVCONTAINER-SEM-GH, #926), volta 2 por delta, opção 1 do dono

Delta lido: `forge-check parecer delta docs/reviews/v0481-devcontainer-sem-gh.md`, intervalo `046cd9a1..a5f6c0f1`. O código do brief (`e1c3ba7c..a5f6c0f1`) é o mesmo: `e1c3ba7c` e `a56b218b` só mexem em pareceres. No domínio estão `.devcontainer/devcontainer.json`, `changelog.d/v0481-devcontainer-sem-gh.md`, `scripts/preparar-estacao.sh` (só o cabeçalho), `tests/mutantes/v0481-devcontainer-sem-gh.json`, `tests/test_ambiente_recriacao.py` e `tests/test_forge.py`. Commits: `84e2ca81` e `a5f6c0f1`. O código mudou 1 linha de comando e o comentário, dentro do H1.

## Verificação
- ci: a5f6c0f1343dbad87df1f227b647e9c0e8460515 verde
- CI lido: runs 45924918762 e 45924918779 do head; vermelhos só `bateria` e `bateria (pareceres)`, que esperam os pareceres; instalação, suítes 3.12 e 3.14, passos, verificações longas, teto de pulados e catraca verdes.
- Local (flock trava-teste-a): `python3 -m unittest tests.test_forge.PrepararEstacao tests.test_ambiente_recriacao.ConfiguracaoDoContainer`: 37 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v0481-devcontainer-sem-gh.json`: M1 a M12 morreram. `--conferir --base ee05ee84`: os trechos estão no lugar.
- A1 da 1.ª rodada resolvido: M6 (L467, tmux), M7 (L468, `~/.config/gh`) e M8 (L469, link) morrem por testes que rodam o preparo e afirmam rc 1 e a linha `erro:`. São eles: `sem_tmux`, `~/.config` como arquivo e o `~/.forge-contrib` com dados, que continuam no lugar. A guarda de L457 ganhou os dois ramos (M9 fora da simulação, M12 dentro dela).
- A2 da 1.ª rodada resolvido: M3, M4 e M11 morrem por testes que rodam o `postStartCommand` literal, com a URL trocada por um remoto `file://`. O caso de falha afirma rc 1 e `ERRO:`. O caso bom afirma que o script da main recebe `1 --container`. M10 (a guarda do grep) morre com uma main sem a marca. Nenhum desses testes lê o texto da fonte.
- Desenho da opção 1: como root só roda o clone raso e anônimo da main (`credential.helper=` vazio, `GIT_TERMINAL_PROMPT=0`, URL fixa no arquivo). O teste forja `origin/main`, a main local e o script do work tree, e confirma que o forjado não roda e que o `gh` falso não é chamado. O repositório é público (`gh repo view`: PUBLIC), e a main atual já traz `FORGE_PREPARO_ESSENCIAL:-0`, então a guarda do grep passa hoje. A URL é a mesma do `repository` de `.claude-plugin/plugin.json` (R-NEUTRO: é a própria fábrica).
- O modelo de projeto (`templates/projeto/.devcontainer/devcontainer.json`) não mudou. O teste fundido segue exigindo `; true` nele.

## Achados
- A3 (recomendado) .devcontainer/devcontainer.json:30 · `d=$(mktemp -d);` não para se o mktemp falhar: com `d` vazio, o root clona em `/r` e roda o script de lá (ainda a main do remoto). Trocar `;` por `&&` (ou `d=$(mktemp -d) || exit 1`) fecha o caso

## Parecer
Aprovado. A volta 2 aplica a opção 1 do dono: o postStart baixa da main o script de preparo, sem o gh, roda-o com o essencial e, se faltar algo ou o clone falhar, avisa em `ERRO:` e sai com 1. Nada da cópia de trabalho roda como root, e o teste de abuso prova isso rodando o comando. Os bloqueantes A1 e A2 da 1.ª rodada estão resolvidos com mutantes e testes do ramo de falha. Todos os 12 mutantes morreram e o CI do head está verde.

O A3 é só recomendação e vira cartão depois do merge. A parte de segurança do desenho (root, URL fixa, clone anônimo) é da `security-engineer` e não foi refeita aqui.
