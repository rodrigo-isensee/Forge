---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-prova-tmpdir
commit: ed99ab1e7e962f1ce851e12cc31556eb3951a781
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-prova-tmpdir

Escopo: E2.356 do pedido v047. Diff `1b88640e..a1eb19ef`: `bin/forge-check` (função `tmpdir_da_prova` e o uso em `rodar_prova`), `tests/test_forge_run.py` (classe `TmpdirDaProva`), `tests/mutantes/v047-prova-tmpdir.json` e o fragmento do changelog. Parecer completo (não havia parecer anterior).

## Gatilhos
`R-SEGURANCA`: muda o ambiente com que a conferência da entrega reexecuta a prova `cmd` (comando vindo da branch, rodado sem shell na worktree). Antes, o ambiente da prova era uma lista positiva (PATH, LC_ALL, PYTHONDONTWRITEBYTECODE, HOME); agora entra só mais o TMPDIR, e só quando ele passa pela guarda.

## Achados

## Sondas

## Detalhe dos achados
Requisito do brief conferido: o TMPDIR aceito não aponta para dentro do repositório nem para pasta de outro usuário.

- Guarda em lista positiva (`bin/forge-check:9005`): caminho absoluto, `realpath` antes de tudo (link simbólico é resolvido e a decisão é sobre o destino), `stat` de pasta, dono igual ao `getuid`, escrita e travessia (`W_OK|X_OK`), e fora da worktree e do pai do `.git` comum. Qualquer falha devolve `None` e a prova roda sem TMPDIR, como antes (falha fechada). Não é lista negativa (AR-3 conferido).
- A pasta do git sai de `git(pasta, ...)` (`bin/forge-check:520`), que tira as variáveis `GIT_*` herdadas: um `GIT_DIR` do ambiente não desvia o cálculo do `.git` comum (AR-7 conferido).
- `bin/forge-check:9033`: só o TMPDIR é acrescentado; nenhuma outra variável do ambiente do operador vaza para a prova.
- Caminho de ataque avaliado: quem controla o TMPDIR é o operador que roda a conferência, não o autor da branch; o autor controla só o comando da prova. O risco real seria a prova gravar temporários dentro da árvore conferida (sujando o que se confere) ou em pasta de outro usuário (link plantado); a guarda fecha os dois.
- Notas informativas, sem caminho de ataque realista (não viram achado, proporcionalidade): com `.git` comum fora do padrão `<repo>/.git` (clone nu ou submódulo), o pai do `.git` comum é uma pasta mais larga ou mais estreita que o repositório; no primeiro caso a guarda só recusa mais (seguro), no segundo a worktree em si continua coberta pela primeira verificação. A janela entre o `stat` e o uso (TOCTOU) exige escrever no próprio TMPDIR do operador, que já é do mesmo usuário.

Sondas executadas (nenhuma prova bloqueante, por isso fora do bloco `## Sondas`), com `tmpdir_da_prova(<clone>)`: TMPDIR = raiz do clone → None; `<clone>/.git` → None; link simbólico fora apontando para `<clone>/docs` → None; `<clone>/../<nome>/docs` → None; vazio → None; `/` → None; pasta própria fora → aceita; link para pasta própria fora → aceita (o destino resolvido).

Testes: `python3 -m unittest tests.test_forge_run` na raiz do clone, no head a1eb19ef: 19 testes, OK. Os oito testes de `TmpdirDaProva` cobrem relativo, inexistente, arquivo executável, outro dono, sem escrita, dentro da worktree e dentro do repositório principal de uma worktree ligada. A suíte inteira roda no CI do PR.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff, os testes do item e sondas locais na biblioteca padrão. Varredura de segredos e de workflow não se aplica (o diff não toca workflow nem configuração com credencial).

## Revalidação por delta (head ed99ab1e)
`forge-check parecer delta` (a1eb19ef..ed99ab1e, sem o que veio da base): só `bin/forge-check` no domínio (`juncao_limpa`, `--tempo`, `--media-por-agente`). Conferido com `git diff origin/develop -- bin/forge-check`: o item soma 27 linhas, todas da `tmpdir_da_prova` e do uso em `rodar_prova`, sem remoção; o resto do delta veio da develop (merge 3fc4724d). Guarda inalterada, nenhum achado novo. `python3 -m unittest tests.test_forge_run`: OK. Suíte inteira no CI do PR.
