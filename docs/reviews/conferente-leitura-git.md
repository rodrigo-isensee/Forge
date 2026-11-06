---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/conferente-leitura-git
commit: dcfc75052a01d12cbea143d8c428710495adc53d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033, CONFERENTE-LEITURA-GIT (o conferente lê `git branch` e `git worktree list` por gramática exata)

Escopo: `dc615c25a89cf801dbff0356ff3e07cf491e4567...dcfc75052a01d12cbea143d8c428710495adc53d`, 2 commits (`ce4409a` feat, `dcfc750` test), 6 arquivos. Revisor de outra instância (`principal-c`), em worktree própria.

Veredito: **aprovado**, sem achado bloqueante; três recomendados (A1 a A3), que não devolvem.

## Suposições
- O brief da implementação (E8, critérios C-1 a C-6) não está no repositório nem em `~/.forge-contrib/docs/briefs/`: o pedido `versao-033` foi reconstruído. A conferência foi feita contra o que o código, a docstring, `docs/hooks.md` e `agents/conferente.md` declaram, não contra o Entregar original.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_guarda_conferente tests.test_hooks tests.test_hooks_volta_corpus` (D-5, só os testes tocados e os de hooks): `Ran 106 tests in 1612.254s` / `FAILED (failures=2, skipped=1)`, as duas falhas em `test_muitos_heredocs_recusam_dentro_do_orcamento` (formas `sh -s` e `python3 -` com 3000 heredocs, papel `dev`): o hook estourou o prazo com a máquina em carga 12 e recusou pela mensagem genérica, caminho que não passa pelo código novo (só o papel só de leitura chega a `git_so_leitura`). Rodado sozinho no mesmo head: `Ran 1 test in 23.501s` / `OK`. `tests.test_guarda_conferente` sozinho: `Ran 19 tests in 18.238s` / `OK`.
- `bin/forge-testes --listar --base origin/develop`: `tests/test_guarda_conferente.py sem mapa` (cai na suíte completa, que fica com o QA e o CI).
- shellcheck: nenhum shell no diff. Mutação no diff: do autor antes do push (V2); não refeita.

## Conferência da mudança
| Item | Resultado |
|---|---|
| `git worktree` só `list` sem argumento | ok: `hooks/conformidade.py:403-404` (`args == ["list"]`); `--porcelain`, `add`, `prune`, `remove` e a forma vazia recusadas nos testes |
| `git branch`: sem argumento, `--list [padrão]`, `-r`, `--contains <commit>`/`--contains=<commit>`; padrão só com `--list` | ok: `hooks/conformidade.py:405-422`; toda opção fora dessas (curtas agrupadas como `-rd`, abreviações como `--cont`, `--`) recusa; nome solto sem `--list` (criação de branch) recusa |
| Valor de `--contains` não vira opção | ok: precisa começar com letra ou dígito (`:397`); `--contains -D` e `--contains` sem valor recusam |
| Os demais subcomandos seguem pelo laço antigo (`GIT_EXECUTA`, `%G`, `ls-remote`) | ok: o desvio em `:1137-1141` só pega as duas chaves novas e retorna |
| Outros papéis | ok: `GIT_LEITURA` sem `branch` e `worktree`; `so_leitura.papeis` segue só `conferente` |
| Sondas no hook (`hooks/conformidade.py` com entrada do conferente) | `git branch --contains abc`: rc 0; `git branch x`: rc 2 (`fora das formas de leitura`); valor com quebra de linha: rc 2 pela gramática da ADR 0011, antes da função nova |
| Documentação | ok: `agents/conferente.md:26`, `docs/hooks.md:37` e a descrição em `hooks/conformidade.json` coerentes com o código |
| Fragmento `changelog.d/conferente-leitura-git.md` | ok: `### Alterado`, uma linha, marca que afrouxa |
| Commits | ok: Conventional Commits em português, um comportamento por commit (regra e reorganização do teste) |

## Conta de linhas (decisão M14)
`git diff --numstat --no-renames origin/develop...dcfc750`, código e teste: `hooks/conformidade.py` 35+1, `hooks/conformidade.json` 1+1, `tests/test_guarda_conferente.py` 39+2; total **79**, dentro do teto de 150, sem exceção. Em `hooks/`, uma classe de comportamento (a lista branca de leitura do git no papel só de leitura), com casos próprios em `tests/test_guarda_conferente.py:124-155` (como em impl-furo-hook-a, testes no módulo, sem fixture em `tests/hooks/`). Fora de `PROTEGIDOS` de `tests/catraca.py`.

## Segurança
Afrouxa a lista branca de um papel só de leitura (rótulo `afrouxa-regra` é do dono). Nenhum achado com gatilho no review; o parecer próprio fica com o `security-engineer` (`docs/security/`, `R-SEGURANCA`), que corre em paralelo nesta branch.

## Achados
- A1 (recomendado) hooks/conformidade.py:397 · a regex usa ^...$ com re.match, e o $ aceita valor com \n no fim (sonda: forma_de_leitura_git aceita 'abc\n'); hoje a gramática da ADR 0011 recusa antes, mas a função sozinha não fecha; sugestão: re.fullmatch sem âncoras
- A2 (recomendado) tests/test_guarda_conferente.py:152 · o nome promete outro papel, mas o teste só confere GIT_LEITURA, sem rodar git branch com outro agent_type; sugestão: renomear ou somar um caso com outro papel pelo hook
- A3 (recomendado) tests/test_guarda_conferente.py:36 · três linhas em branco entre as classes (o padrão do arquivo é duas); sugestão: tirar uma

## Parecer
Aprovado. A gramática é lista branca exata, falha fechada em toda forma não prevista, e os testes cobrem as nove formas de leitura e 25 formas de escrita ou fora do limite (`R-CONFORMIDADE` no stderr). A1 a A3 são recomendados: nenhum é defeito com gatilho no caminho real do hook.
