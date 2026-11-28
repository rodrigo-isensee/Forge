---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-git-controle-gc1
commit: 29bdda157d3e984cf5cafd71c9647874b4769f1b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (E3.3, PR #957, GIT-CONTROLE-CONFIG-DA-COPIA corte GC1)

1ª rodada completa no head `29bdda15` (Base-sha `1ced5c09`, que é o merge-base com a `origin/develop`).

- ci: 29bdda157d3e984cf5cafd71c9647874b4769f1b verde (runs 46136636495 e 46136709586, `headSha` igual ao commit, conclusão success; suíte 5/5, catraca e catraca (conferência) verdes; o teste de custo `tests/test_hooks_volta_corpus.py` roda na suíte do CI)
- testes do item: `python3 -m unittest tests.test_forge_git` · 19 OK
- mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v048-git-controle-gc1*.json` · 25/25 mortos; `--cobertura --base 1ced5c09` · toda guarda mudada coberta por mutante declarado
- tamanho (H1): `bin/forge_git.py` com 139 linhas, docstring incluída, e um comportamento só (o ponto único); dentro do teto

## Achados
- A1 (bloqueante) bin/forge_git.py:82 · REATIVA compara o nome exato, mas o git aceita a abreviação da opção longa: `cat-file --filt` roda o filter.smudge da cópia e `grep --open-files` roda o core.pager dela, sem Recusado (S1, S2). Recuse todo prefixo de opção de REATIVA (e ponha -c core.pager=cat no NEUTRO), com teste.
- A2 (bloqueante) bin/forge_git.py:85 · a leitura de LEITURA vale se a palavra aparece em qualquer posição: `git(raiz, "worktree", "add", "list")` passa como leitura, cria a worktree `list` e roda o filter.smudge da cópia (S3). Confira o subcomando na posição dele (worktree, remote) e teste o caso.

## Sondas
- S1 · forge_git.git(copia, "cat-file", "--filt", "HEAD:f"), com info/attributes `* filter=y` e filter.y.smudge=<marcador> na config da cópia · espera: Recusado, marcador ausente · obtido: rc=0, marcador gravado (git 2.43.0)
- S2 · forge_git.git(copia, "grep", "--open-files", "-e", "b"), com core.pager=<marcador> na config da cópia · espera: Recusado, marcador ausente · obtido: rc=0, marcador gravado; "--open-files-in-pager" inteiro é recusado
- S3 · forge_git.git(copia, "worktree", "add", "list"), com info/attributes `* filter=y` e filter.y.smudge=<marcador> · espera: Recusado ("só a leitura") · obtido: rc=0, worktree criada e marcador gravado

## Parecer
Reprovado, por dois defeitos provados nas guardas do próprio ponto único; o resto da entrega está bom.

O desenho cumpre a E3.2: ambiente sem `GIT_*` nem `XDG_CONFIG_HOME`, `NEUTRO` na linha de comando antes do subcomando, chave por protocolo fechada por nome, lista positiva com a config local conferida para o que toca índice ou árvore, e `merge-tree` e rede num neutro fora do `TMPDIR`. Os testes têm duas metades (o cru executa o vetor, o `forge_git` não), em repositório descartável com HOME temporário, e cada guarda tem mutante que morre. O changelog e o `docs/indice-forge.md` estão atualizados. Sem chamador neste corte: os próximos cortes passam a depender destas guardas, e por isso as duas brechas bloqueiam já.

- A1 · `bin/forge_git.py:82` · `REATIVA` é uma lista de nomes inteiros, mas o parse-options do git aceita a abreviação única da opção longa. `cat-file` e `grep` estão em `LEITURA` e não passam pela `config_permitida`, então a abreviação reabre o programa da cópia (S1, S2). Sugestão: recusar o argumento `--x` (antes do `=`) que seja prefixo de algum item de `REATIVA`; para o pager, `-c core.pager=cat` no `NEUTRO` fecha também o caminho pelo nome inteiro. Teste do ramo de falha com a abreviação e mutante da nova condição. Severidade: bloqueia (defeito provado).
- A2 · `bin/forge_git.py:85` · `LEITURA[sub].intersection(resto)` aceita a palavra de leitura em qualquer posição. Em `worktree` e `remote`, ela é o subcomando, e um argumento posicional igual a `list` ou `get-url` libera `add` (S3). O `test_subcomando_misto_so_na_leitura` (`tests/test_forge_git.py:188`) cobre `worktree add w`, mas não esse caso. Sugestão: para os subcomandos com sub-subcomando, exigir que o primeiro argumento que não é opção seja o de leitura; para `config` e `branch`, manter a opção, com teste do caso posicional. Severidade: bloqueia (defeito provado).

Revalidação: na volta, leio só o delta (`forge-check parecer delta docs/reviews/v048-git-controle-gc1.md`) e as sondas S1 a S3 de novo.
