---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-tempo-fixture
commit: 57150d5ee607032f8e302e5319882ed3eeb0edac
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E164.2, PR #850, TEMPO-FIXTURE-INSTAVEL)

Escopo: o commit 57150d5e sobre a base 8f37daf8 (`hooks/conformidade.py` +5/-1, mutante `tests/mutantes/v0480-tempo-fixture.json`, fragmento `changelog.d/v0480-tempo-fixture.md`). Tamanho (H1): 5 linhas de código, um comportamento.

## Sondas

## Parecer
Aprovado, sem achados.

**Equivalência da decisão.** O ramo antigo `\b(git|gh)\b[^\n]*\b(ação)\b` casa quando, numa mesma linha, existe um `git`/`gh` seguido da ação. O novo parte do início da linha (`(?<![^\n])`) e o grupo atômico fixa o primeiro `git`/`gh` dela; como qualquer ação depois de um `git`/`gh` posterior também está depois do primeiro, o conjunto de linhas casadas é o mesmo, e o `[^\n]*` continua sem atravessar a quebra. Os grupos de captura seguem dois e o `CRITICO` só é usado como booleano (`search` em `conformidade.py:2199`, `:2207`, `:2213`, `:2245`, `:4041`, `:4423` e nos padrões concatenados `:3982` e `:4045`), então a concatenação não muda numeração que alguém leia. Grupo atômico exige Python 3.11; o README pede 3.12 e o CI roda 3.12 e 3.14.

**Sonda do revisor (independente dos 344.007 textos do autor).** Comparei o ramo antigo com o novo em 29 textos fixos e 400.000 aleatórios (tokens `git`, `gh`, ações, `env`, `sudo`, `/`, `;`, `&&`, `|`, `=`, `_`, `\n`, `\r`, `\t`, `\x0b`, U+2028, `é`, maiúsculas): 0 diferenças. Fixos conferidos, todos com a mesma decisão nos dois e no `CRITICO` inteiro: `env A=1 git push origin x`, `sudo gh pr merge 1`, `/usr/bin/git push`, `echo a; git push`, `x=1 && gh pr ready 3`, `GIT_DIR=x git -C y push`, `echo ok\n  /opt/gh/bin/gh  pr  review 2`, `a\r\ngit push`, `\n\ngh label x`, `agh git x push`, `git x push\ngit y` (casam); `git status\necho push`, `git\npush`, `legit push`, `ghgit push`, `git_x push`, `égit push`, `push git`, `gh git\ngh x\nfoo push` (não casam). Custo em 8 KB de `gh repo `: antigo 0,17 s, novo 0,00 s de CPU.

**Testes e mutante (só o do item).** `tests.test_hooks.Hooks.test_marcador_critico_tambem_na_forma_juntada` e `test_fixtures_do_repo_publico` (que mede `trava-gh-marcador-linear-libera` contra metade do prazo): OK, 2 testes. `bin/forge-mutante tests/mutantes/v0480-tempo-fixture.json --processos 1`: `TF1 · morreu · hooks/conformidade.py:65`. A guarda mudada é uma linha só, com um mutante declarado. Nenhuma outra spec de `tests/mutantes/` cita o texto antigo do padrão.

**Suíte.** Não rerrodada (R-REVIEW): o CI do PR #850 estava em andamento na leitura (bateria, instalação e árvore verdes; partes da suíte pendentes); o merge depende dele verde.

**Commit e changelog.** Mensagem em Conventional Commits, com causa medida (cProfile) e limite da fixture sem mudança; fragmento em `changelog.d/` sem editar o `CHANGELOG.md`.
