---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/entrega-push-proxy
commit: 843e6b752849bf4b62fcf3d41dcc83c22a6f74e5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: v046 (E12.1 e E12.2, ENTREGA-PUSH-PROXY)

## Escopo lido
`git diff 11ba4fa6..a5fec3a0` (Base-sha 11ba4fa6), 2 commits e 5 arquivos. a2dfb22b é o `fix` em `bin/forge-check`, com o teste, os mutantes e o fragmento; a5fec3a0 põe o módulo no MAPA de `bin/forge-testes`. Contam para a M14 107 linhas: `bin/` 15 e `tests/*.py` 92 (o json de mutantes fica fora). Ficam abaixo da orientação, e o PR tem um comportamento só. As mensagens seguem os Conventional Commits.

## Verificação
- `bin/forge-check:474-484`: `rede` só vale quando `args[0]` está em `{"ls-remote", "fetch"}`. Nesse caso passam apenas as chaves que casam por inteiro (`fullmatch`) com `GIT_CONFIG_(COUNT|PARAMETERS|KEY_n|VALUE_n)`. `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM` e `GIT_CONFIG_SYSTEM` continuam fora, e o `fullmatch` impede que um prefixo como `GIT_CONFIG_COUNTX` passe. Uma chamada com opção antes do subcomando cai no ramo restrito, o que é seguro. Os comandos locais continuam sem nenhuma `GIT_*`.
- Hooks: só usam `git()` com `config --get alias.<sub>` (`hooks/conformidade.py:1619`) e com `ls-files` (`:1716`), além do repasse genérico de `hooks/_comum.py:222`. Nenhum hook chama `ls-remote` nem `fetch` por `git()`, então nenhum hook ganha caminho de rede com configuração injetada. O `CONFIG_NO_AMBIENTE` da conformidade (`hooks/conformidade.py:209`) continua barrando `GIT_CONFIG_*` atribuída na linha de comando. Os chamadores de rede são `bin/forge-check:7065` e `:9254`, ambos `ls-remote origin refs/heads/<branch>`, que é a prova de push. O `_git_da_area` (`:4233`) é outra função e não mudou.
- Segurança: a configuração herdada vem do ambiente do próprio processo, a mesma que o `git` do usuário já usa. O parecer de segurança é do `security-engineer` (classe C) e não é refeito aqui.
- `tests/test_git_rede_config.py`: o remoto só é alcançável pelo `insteadOf` `falso://r`, sem rede. Há casos para `ls-remote` e `fetch` com COUNT/KEY/VALUE, para `GIT_CONFIG_PARAMETERS`, para `GIT_DIR` e `GIT_CONFIG_GLOBAL`, que seguem fora no comando de rede, e para o comando local, que não herda nada. Os testes não abrem subprocesso Python, e o ambiente de cada caso sai limpo de `GIT_*`.
- Na base o módulo fica vermelho (4 falhas, com o `bin/forge-check` de 11ba4fa6) e no head fica verde (6 OK).
- `forge-mutante tests/mutantes/v046-entrega-push-proxy.json`: M1 a M6 morreram, e cada mutante tem um teste próprio. `forge-mutante --cobertura --base 11ba4fa6`: as guardas de :482 e :484 estão cobertas. A linha antiga (:475 da base) foi apagada.
- MAPA: `test_git_rede_config` entrou em `FORGE_CHECK` (`bin/forge-testes:96`). A contagem fixa que confere esse mapa não foi atualizada (A1).

## Testes dos arquivos tocados
Rodados numa worktree destacada em a5fec3a0, sem escrever na branch:
- `tests.test_git_rede_config`: 6 OK.
- `tests.test_selo_e_entrega`: 37 OK.
- `tests.test_testes_tocados`: 143 testes, 1 falha. `Mapa.test_forge_check_roda_os_modulos_dele` dá `AssertionError: 69 != 68`. Com o `bin/forge-testes` da base o mesmo caso passa, então a falha vem do diff e o CI do PR vai reprovar.

## Achados
- A1 (bloqueante) tests/test_testes_tocados.py:66 · a contagem fixa do MAPA FORGE_CHECK continuava 68 e o mapa tem 69 (bin/forge-testes:96). Resolvido em 843e6b75: contagem 69 e nota `v046 E12.1: + test_git_rede_config` no comentário.

## Sondas
- S1 · python3 -m unittest tests.test_testes_tocados.Mapa.test_forge_check_roda_os_modulos_dele (worktree em a5fec3a0) · espera: OK · obtido: FAIL, AssertionError: 69 != 68

## Delta lido (revalidação, a5fec3a0..843e6b75)
Um commit, 843e6b75, 3 arquivos, 6 linhas de código e teste: `tests/test_testes_tocados.py:66` (68 para 69 e a nota), `bin/forge-check:475` (`\d+` virou `[0-9]+` em KEY_n e VALUE_n) e `tests/mutantes/v046-entrega-push-proxy.json` (M3, M4 e M6 com o texto novo da linha). O `[0-9]` é mais estrito que `\d`, que aceita dígito Unicode; com `fullmatch` nada que passava deixa de passar entre `GIT_CONFIG_KEY_0` e `_9...`, e nome com dígito não ASCII agora fica fora, o que é o lado seguro. A guarda não mudou de forma. Rodado numa worktree destacada em 843e6b75: `tests.test_git_rede_config` e o caso do mapa, 7 OK; `forge-mutante` com a spec: M1 a M6 morreram. Total M14 do PR: 107 mais 6, abaixo da orientação.

## Parecer
Aprovado. O A1 está resolvido: o mapa conta 69 e o caso `Mapa.test_forge_check_roda_os_modulos_dele` passa. A troca para `[0-9]` só aperta a regex, e os mutantes atualizados continuam morrendo. O resto do parecer anterior (correção restrita a `ls-remote` e `fetch`, hooks sem caminho de rede) segue valendo, porque o delta não os toca. A suíte inteira fica para o CI do PR.
