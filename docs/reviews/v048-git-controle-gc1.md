---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-git-controle-gc1
commit: 841c557ea6eb82bddf4eec7bf48c816683b533b0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (E3.7, PR #957, GIT-CONTROLE-CONFIG-DA-COPIA corte GC1; delta das voltas 1 e 2)

Delta `29bdda15..841c557e` (voltas 1 `2a13fead` e 2 `841c557e`), lido pelo `forge-check parecer delta docs/reviews/v048-git-controle-gc1.md`, sem o que veio da base: no domínio, `bin/forge_git.py`, `changelog.d/v048-git-controle-gc1.md`, `tests/mutantes/v048-git-controle-gc1.json`, `-2.json`, `-3.json`, `-5.json`, `-6.json` e `tests/test_forge_git.py`. Parecer anterior: reprovado em `29bdda15` (A1, A2). Clone de revisão: `/root/.forge-contrib/wt/v048-git-controle-gc1-tech-lead-4`, no head `841c557e`.

## CI e ferramentas (citadas, não refeitas)
- ci: 841c557ea6eb82bddf4eec7bf48c816683b533b0 verde
- `gh pr checks 957`: runs `46145488828` (tentativa 2, a parte 5/5 rodada de novo por decisão do Jarvis) e `46145488817`, ambos com `headSha` = `841c557e`. Suíte 3.12 partes 1/5 a 5/5 (o teste de custo `tests/test_hooks_volta_corpus.py` roda nela), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `árvore já provada na develop`, `catraca` e `catraca (conferência)` verdes. Vermelho só `bateria (pareceres)`, que espera os pareceres.
- Testes do item: `python3 -m unittest tests.test_forge_git` · 24 testes, OK (git 2.43.0).
- Mutantes refeitos por mim (os logs do autor não valem, R-PROVA): `bin/forge-mutante --processos 1 tests/mutantes/v048-git-controle-gc1*.json` · rc=0, 38/38 mortos (M1 a M38). `bin/forge-mutante --cobertura --base 29bdda15`: toda guarda mudada de `bin/forge_git.py` (linhas 50, 78, 83, 84, 85, 86, 92, 93, 96, 100) coberta por mutante declarado; o único "não coberto" (`hooks/conformidade.json`) veio da `develop`, fora do delta.
- Tamanho (H1): `bin/forge_git.py` com 139 linhas no total, um comportamento só; dentro do teto.

## Sondas da 1.ª rodada, refeitas no head
Mesmo cenário da 1.ª rodada (filtro, textconv e pager da cópia apontando um marcador), por `python3 -I` com ambiente limpo e HOME temporário:
- S1 `cat-file --filt HEAD:f` (e `--textc`, `--filters --path=f`): `Recusado` ("reabre programa externo"), marcador ausente. A1 fechado.
- S2 `grep --open-files -e b` (e o nome inteiro): `Recusado`, marcador ausente; `core.pager=cat` agora no `NEUTRO` (`bin/forge_git.py:25`). A1 fechado.
- S3 `worktree add list`: `Recusado` ("só a leitura"), sem worktree nem marcador. A2 fechado.
- Sondas novas no delta, todas fechadas: `worktree --porcelain add list`, `remote -v add list x` e `branch --list -m novo` recusados; `log -p --ext`, `log --show-sig`, `show --textcon` e `grep --textc` recusados; `branch -r novo` dá rc=128 e `branch --contains HEAD novo` rc=0, sem branch criada; `status` e `ls-files --recurse-submodules` com submódulo recusados. Leituras legítimas (`worktree list`, `remote -v`, `branch --show-current`, `config --get`) passam.

## Parecer
Aprovado. Os dois bloqueantes da 1.ª rodada estão fechados e provados por sonda, teste e mutante.

- A1 · a montagem (`bin/forge_git.py:92-93`) recusa todo argumento `--x` (antes do `=`) que seja prefixo de um item de `REATIVA`, com o `--` separador fora; o custo é recusar também `--text` e `--filter` inteiros, uma falha fechada aceitável no ponto único. `--output` entrou em `REATIVA` (grava arquivo fora da árvore). Teste do ramo de falha em `test_opcao_abreviada_reabre_programa`, com a prova crua por `--textc`, que o git do runner aceita; mutantes M26 e M27.
- A2 · `_so_leitura` (`bin/forge_git.py:81-86`) confere a ação no 1.º posicional de `remote` e `worktree` (o `""` representa o `git remote` sem ação), só opções de listagem no `branch` e a opção no `config`. Teste em `test_leitura_pela_posicao_da_acao`, com os casos de escrita recusados e as leituras legítimas passando; mutantes M32 a M35 e M38.
- O resto do delta, vindo da segurança (gitlink no `INDICE`, chaves do VS Code em `PERMITIDAS`), lido no domínio do código: `sem_gitlink` falha fechado (rc diferente de 0 recusa), tem teste com o submódulo de config própria e mutantes M30 e M31; o changelog descreve a mudança. O mérito de segurança é do `security-engineer`.

Revalidação: nenhum bloqueante novo; numa próxima volta, leio só o delta a partir de `841c557e`.
