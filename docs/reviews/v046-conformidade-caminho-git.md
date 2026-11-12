---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: c072741112e9383735cb82019aa0523acb4fa6a6
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.12, conformidade-caminho-git, revalidação por delta)

## Escopo lido
Delta lido por `forge-check parecer delta docs/reviews/v046-conformidade-caminho-git.md`: intervalo 22187bae..c0727411 (volta E20.10: 44b75270 fix, 90bea40b e c0727411 test), 28 arquivos no domínio: `hooks/conformidade.py` +23/-6, `tests/test_hook_git_comum.py` +3/-2, 22 fixtures `gitcomum-*`, a spec `tests/mutantes/v046-conformidade-caminho-git-2.json` (G9 a G14), o índice e o fragmento. M14 da branch inteira contra a base 8b5a44d5: 91 linhas de código e teste, abaixo da orientação de 150; uma classe de comportamento em `hooks/` com corpus próprio. Instância que não fez a entrega, numa worktree destacada minha; rodei só `tests/test_hook_git_comum.py` (R-TETO): 1 teste OK, 42 fixtures (27 recusam, 15 liberam), conferidas por contagem do `esperado.codigo`.

## Achados
- A3 (bloqueante) hooks/conformidade.py:330 · A1 da segurança segue aberto fora da forma exata da regex: `--git-path` com o argumento entre aspas, `2>/dev/null` ou `-q` dentro do `$(…)` e `git -C . rev-parse` sem resto liberam rc 0 a escrita em .git/hooks/pre-push (S1 a S5)
- A4 (recomendado) hooks/conformidade.py:954 · A4, A6 e A7 da segurança (E20.8) deviam estar em cartão; não achei cartão no KANBAN.md nem no pedido para eles; pendente: do Jarvis, não do autor

## Sondas
- S1 · cp x "$(git rev-parse --git-path 'hooks/pre-push')" · espera: rc 2 R-CONFORMIDADE · obtido: rc 0
- S2 · cp x "$(git rev-parse --git-path \"hooks/pre-push\")" · espera: rc 2 R-CONFORMIDADE · obtido: rc 0
- S3 · cp x "$(git rev-parse --git-path hooks/pre-push 2>/dev/null)" · espera: rc 2 R-CONFORMIDADE · obtido: rc 0
- S4 · cp x "$(git rev-parse -q --git-path hooks/pre-push)" · espera: rc 2 R-CONFORMIDADE · obtido: rc 0
- S5 · cp x "$(git -C . rev-parse --git-path hooks/pre-push)" · espera: rc 2 R-CONFORMIDADE · obtido: rc 0

## Parecer
**Reprovado** no head c0727411, pelo A3.

O que a volta pediu e está feito (conferido por leitura e por sonda própria, fixture montada pela máquina do `tests/test_hooks.py` na minha worktree, fora do corpus):
- A1/A3 da segurança na forma exata: `$(git rev-parse --git-dir|--git-common-dir|--absolute-git-dir)` e `--git-path <x>`, com espaços internos, `--path-format=absolute`, crase, sem aspas, sem resto e em variável da linha (`d=$(…); tee $d/config`, `cp x "$d"`) recusam; `cat "$(git rev-parse --git-dir)/config"`, `git rev-parse --git-dir` e `cp x "$(git rev-parse --git-dir)/../docs/y.md"` liberam.
- A2: `${d%/}/config` recusa (`SO_VARIAVEL` vai até o `}`; `VARIAVEL_INTEIRA` não troca `${d%/}` pelo valor).
- A5: `cp --target-directory=<pasta>` é conferido como `-t`.
- Falso positivo (A1 do review anterior, A1 do QA): a mensagem agora diz que o valor foi lido como `.git` e manda usar o caminho literal (fixture `gitcomum-tmpdir-logs-recusa-limite`, `stderr` "use o caminho literal"); o limite do changelog tira `$(pwd)`, `$PWD`, `$HOME` e `$CLAUDE_PROJECT_DIR`, o que fecha o A2 do review anterior.
- Mutantes G9 a G14 declarados um por guarda nova (linhas 956, 1013, 1401, 1483, 1484 e 1170); a execução deles é do QA, cito sem refazer.

A3 · hooks/conformidade.py:330 (`_REV_PARSE`) · problema: a correção reconhece a substituição só quando o corpo dela é exatamente `git rev-parse [--path-format=x] --opção [arg sem aspas]`; qualquer outra palavra dentro do `$(…)` (aspas no argumento, redirecionamento, `-q`, `git -C <pasta>`) deixa a substituição opaca e, sem resto, nada é conferido: a escrita em `.git/hooks/pre-push` passa, que é o gatilho do A1 da segurança (instalar hook e contornar `R-VERIFY`). O `git -C <pasta> … sem resto` (S5) foi declarado na entrega (Histórico 12:30); as aspas no argumento, o `2>/dev/null` e o `-q` (S1 a S4) não. Sugestão: falhar fechado pela presença, não pela forma: substituição (`$(…)` ou crase) cujo corpo cita `rev-parse` e uma das opções `--git-dir`, `--git-common-dir`, `--absolute-git-dir` ou `--git-path` vale como `${DIR_DO_GIT}`, com o argumento do `--git-path` tirado das aspas (`shlex`) quando houver, ou, sem argumento legível, como o próprio `.git` (recusa). Fixture para S1 a S5 e um mutante por guarda nova. Severidade: bloqueia.

A4 · recomendado, não é do autor: o brief da E20.12 dá A4, A6 e A7 da segurança como "em cartão"; não achei o cartão (busca por `E20.8`, `opaco` e `caminho-git` no KANBAN.md). Registrar antes do merge.

Cito e não refaço (`R-SEGURANCA`): a segurança revalida o mesmo delta na E20.13 e o QA na E20.14.
