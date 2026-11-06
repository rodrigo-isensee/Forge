---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/conferente-leitura-git
commit: dcfc75052a01d12cbea143d8c428710495adc53d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: versao-033 (CONFERENTE-LEITURA-GIT, E8)

Base `dc615c2` (origin/develop), head revisado `dcfc75052a01d12cbea143d8c428710495adc53d`. Diff de 6 arquivos: `hooks/conformidade.py` (`forma_de_leitura_git` e o desvio em `git_so_leitura`), `hooks/conformidade.json` (`git branch` e `git worktree` em `so_leitura.comandos`), `agents/conferente.md`, `docs/hooks.md`, fragmento do changelog e `tests/test_guarda_conferente.py`.

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`, papel só de leitura do `forge:conferente`, `R-PROVA`, `R-BRIEF`). A mudança afrouxa a lista branca (rótulo `afrouxa-regra` cabe ao dono).

## Achados
- A1 (recomendado) tests/test_guarda_conferente.py:140 · o corpus de recusa não cobre formas longas e de cópia (`--delete`, `--move`, `--copy`, `-c`, `-C`, `-M`, `--set-upstream-to`, `--track`, `-r -d`), `worktree move|lock|repair` nem `;`/`&&`/`|`; a sonda prova a recusa, falta a regressão
- A2 (recomendado) agents/conferente.md:26 · o texto do agente e `docs/hooks.md:37` citam só `--contains <commit>`; o código (`hooks/conformidade.py:400`) aceita também `--contains=<commit>`; alinhar o texto ao código

## Detalhe dos achados
**Gramática exata (`hooks/conformidade.py:400` a `:422`).** `git worktree` passa só com `args == ["list"]`. `git branch` aceita apenas `--list`, `-r`, `--contains <v>` e `--contains=<v>` com `v` casando `^[0-9A-Za-z][0-9A-Za-z._/@^~-]*$` (`:397`, sem `-` inicial, sem vazio); qualquer outra palavra iniciada por `-` recusa (inclui `--`, agrupadas e abreviações), e palavra livre só vale com `--list` (padrão). Logo nenhum argumento que crie, apague, renomeie, copie ou mude upstream chega ao git: sem `--list`, nome solto recusa (`git branch x` criaria). O desvio em `:1137` retorna antes da checagem genérica, mas a gramática é mais estrita que ela (não há opção que execute programa nas formas aceitas). A opção global continua só `-C` e `--no-pager` (`:1109`); `-c`, `--git-dir`, `--work-tree`, `--exec-path` viram a chave `git <opção>`, fora da lista.

**Sonda adversarial (só local, hook real via `rodar` dos testes).** 77 das 78 formas da sonda recusadas com rc=2 e `R-CONFORMIDADE`, entre elas: `git branch -D|-d|-M|-m|-c|-C|-f|-t|-u`, `--delete|--move|--copy|--force|--track|--set-upstream-to[=]|--unset-upstream|--create-reflog|--recurse-submodules|--edit-description|--no-contains`, `-dr`, `-r -d`, `-r x`, `-- x`, `--list -- -D`, `--list x -d`, `--contains=`, `--contains=-D`, `--contains '-D'`, `--contains x y`, `--lis`, `-l x`, `--list=x`; `git worktree add|remove|prune|move|lock|repair|lis`, `list -v|--expire=now|x`; `git -c ...`, `--git-dir=`, `--work-tree=`, `--exec-path=`, `-Cx`; encadeamento `;`, `&&`, `||`, `|`, `&`, subshell `( )`, grupo `{ }`, nova linha; `$( )`, crase, `"$(echo -D)"`, `\-D`; `>`, `>>`, `2>`, `<`; `GIT_DIR=x`, `env`, `command`; ofuscação `g''it`, `b''ranch`, `-''D`, `'branch'`, `git br`. Corpus legítimo aceito: `git branch`, `--list 'melhoria/*'`, `-r`, `--contains 928e61b`, `-r --contains origin/develop`, `git worktree list`, `git --no-pager -C . branch -r`, `git branch && git worktree list`, `git branch | grep x`. `git branch --list 'a;git branch -D x'` passa, mas é um padrão entre aspas simples entregue inteiro ao git, só leitura.

**Efeito no disco.** Num repositório de teste com worktree órfã (`prunable`), `git worktree list`, `git branch`, `git branch -r --contains HEAD` e `git branch --list 'm*'` deixaram `.git/` idêntico (sha1 de todos os arquivos antes e depois) e a entrada `.git/worktrees/w` intacta: a listagem não poda. Pager e `core.fsmonitor` não se aplicam fora de terminal e sem índice; o risco de configuração do repositório é o mesmo de `git log`, já liberado.

- A1 · evidência `tests/test_guarda_conferente.py:140` · sem caminho de ataque hoje (a sonda recusa tudo); o risco é regressão futura da gramática sem teste que a pegue · informativa · correção mínima: acrescentar ao laço de recusa as formas listadas acima (todas as de `git branch` e `git worktree`, as de encadeamento e as globais) · esforço P · dono `tech-lead`.
- A2 · evidência `agents/conferente.md:26`, `docs/hooks.md:37` · sem caminho de ataque (a forma `=` é leitura e tem o mesmo filtro de valor) · informativa · correção mínima: escrever `--contains <commit>` ou `--contains=<commit>` nos dois textos · esforço P · dono `tech-lead`.

## Riscos aceitos e ferramentas
Sem risco aceito. Testes dos arquivos tocados (D-5): `python3 -m unittest test_guarda_conferente` (em `tests/`), 19 testes, rc=0; sonda em `$TMPDIR` com 77 recusas, 1 padrão entre aspas aceito (leitura) e 10 legítimas aceitas de 11 (a outra, `git branch 2>/dev/null`, recusada pela gramática da ADR 0011 já na base, fora deste diff). Ferramentas ausentes no PATH (lacuna, não instaladas): `gitleaks`, `semgrep`, `osv-scanner`; o diff não traz segredo nem dependência, por leitura.
