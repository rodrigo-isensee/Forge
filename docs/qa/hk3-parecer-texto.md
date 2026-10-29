---
tipo: qa
contrato: 1
pedido: hk3-parecer-texto
branch: melhoria/hk3-parecer-texto
commit: cf6bf0adc637685b8f4773e5f9ea2f59c373cbf1
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: hk3-parecer-texto, volta 1 (PR B do HK3: a palavra do merge, do pull ou do gh pr que só aparece no texto)

Plano: o da primeira rodada (as decisões de 2026-10-28 10:40, de 2026-10-29 12:34 e a de 13:44; sem especificação de UX). Esta rodada revalida o delta `7b2a225..cf6bf0a`: `hooks/parecer.py` +29 (`HEREDOC_SIMPLES` e `heredocs_simples` novos, `e_shell_c_de_texto` com `BASH_ENV=` e shell sem `-c`, âncora do `SED_LE`), 10 fixtures novas e a spec `hk3-parecer-texto-4.json`. O merge da develop `f3f63f9` traz só `forge-check`, `conferente.md`, `jarvis.md` e os pareceres do T6T3, fora do escopo do hook. Escopo do PR igual ao da entrega. Carga de 1 minuto conferida abaixo de 7 antes de cada rodada.

## Achados
- A1 (recomendado) hooks/parecer.py:46 · o `<<-` de `HEREDOC_SIMPLES` não tem teste (meu mutante Q2 sobrevive): `cat <<-'EOF'` com terminador de tab passa e nenhuma fixture `passa` o guarda; desvio para o lado seguro; incluir fixture `texto-passa-heredoc-menos-*` (AR-1, lista de mutantes incompleta)
- A2 (recomendado) hooks/parecer.py:117 · `"BASH_ENV=" in texto` é literal: `BASH_ENV+=e.sh bash -c 'sleep 1'` e `printf -v BASH_ENV …; export BASH_ENV` passam (rc 0 no head, 2 na base) e rodam o merge; mesma régua do A1 do review (a base já passa `printf … > e.sh; sh e.sh`); trocar por `"BASH_ENV" in texto`

## Detalhe dos achados
- Nenhum bloqueante.
- Conferência da lista contra o diff: a `--cobertura` sobre `d14a713` lista `coberta` para toda condição Python mudada no `hooks/parecer.py` (linhas 90, 93, 102, 103, 105, 107, 108, 117, 122, 123, 126, 129, 569, 610) e nenhuma linha `não coberta` ou `isenta` em `hooks/`; as linhas de `bin/forge-check` que ela lista vêm do merge do T6T3 (spec própria `t6t3-mensagem.json`, outro pedido).
- Mutantes extras meus (spec em `$TMPDIR`, 7 mutantes das peças de `HEREDOC_SIMPLES` e de `heredocs_simples` sem mutante declarado): Q3 (lookahead do terminador) morreu; sobreviveram Q1 (`(?<!<)` removido), Q2 (`<<-` removido), Q4 (`lstrip` do tab removido), Q6 (`pendentes[1:]` por `[]`), Q7 (`bool(m.group(1))` por `False`) e Q9 (terminador entre aspas duplas). Para cada um comparei o hook original e o mutado sobre 22 sondas (`<<<`, `<<"EOF"`, `<<-` com e sem tab, dois heredocs na linha com merge depois, sem aspa etc.): Q1, Q4, Q6, Q7 e Q9 dão o mesmo veredito em todas, pela razão das justificativas V2 a V4 do autor (a `SO_CAT.fullmatch` sobre o texto cortado recusa o resto: ela não aceita `<`, `$`, barra invertida, aspa nem `;`, e o desvio possível de Q6 é só barrar a mais); aceitos como equivalentes por redundância. Q2 difere só para o lado seguro (barra o `<<-` que o original deixa passar): é o A1.
- Equivalentes declarados V2, V3, V4, V10 e V12 do autor: conferidos contra o código; aceitos.
- Sondas no hook (repositório descartável em `develop`, worktree em `melhoria/x`, sem parecer): barram (rc 2) merge depois do corpo de `cat <<'A' <<'B'`, depois de `cat <<-A` com terminador de tab e depois de `cat <<"EOF"`; `cat <<<EOF` com merge; `sh -c 'sleep 1; git merge …'`; `sh -c 'echo git merge …' | sh` (a regressão do A1 do review, agora recusada); `BASH_ENV=e.sh bash -c`. Passam (rc 0): corpo de `cat` com a palavra, `<<-EOF` com terminador de espaços (o bash não o corta, o corpo vai até o fim, então é texto) e `timeout 900 sh -c 'until grep -q merge-base f; …'`. Limitação registrada do pedido (ofuscação): `sed -n 1p -e …` e as formas do A2.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2: `git merge-base` não é merge | `PastaDoGit.test_corpus_texto_passa_e_barra` (`texto-passa-merge-base-*`, `texto-barra-merge-base-e-merge`) | `merge-base` x `merge` na mesma linha | passou |
| E2: corpo de heredoc só de `cat` (e `sed -n <números>p` como `cat`) é texto | idem (`texto-passa-heredoc-*`, `texto-passa-grep-com-merge-no-argumento`) | só `cat`, sem `;`, pipe, aspa ou `$` | passou (T10 a T13, V1, V9, V10 morrem) |
| Volta 1: a isenção do heredoc só vale com o corte que o bash também faz (`<<$'EOF'`, `<<\`, `<<EOF\`, `<<<`, aspa e `$` no delimitador, `<<-` com barra no corpo) | idem (`texto-barra-heredoc-delimitador-*`, `-aqui-string`, `-barra-no-lugar-do-delimitador`, `-menos-com-barra-no-corpo`; `texto-passa-heredoc-so-lido-com-cifrao-no-corpo`) | `HEREDOC_SIMPLES`, `heredocs_simples` | passou (V1, V5, V6, V11 morrem; Q2 sobrevive, A1) |
| Volta 1: `sh -c` com shell no stdin ou `BASH_ENV=` na linha perde a isenção | idem (`texto-barra-sh-c-com-texto-enviado-a-shell-por-pipe`, `texto-barra-sh-c-com-bash-env`) | shell sem `-c`, `BASH_ENV=` | passou (V7, V8 morrem; formas sem `=`, A2) |
| E2: `sed -i`, `sed` com `e`, opção depois, metacaractere tiram a isenção | idem (`texto-barra-heredoc-gravado-e-sed-*`, `texto-barra-sed-com-metacaractere-nao-vira-cat`) | limite do `SED_LE` | passou |
| E2: `sh -c` que só lê ou espera passa; o que executa merge, pull ou gh pr, `eval`, crase, `$( )` segue barrado | idem (`texto-passa-sh-c-*`, `texto-barra-sh-c-*`, `texto-barra-eval-*`) | `grep`, `cat`, `sleep`, `echo`, laços | passou |
| M3: heredoc gravado que roda python3, git, gh, forge-check, sh ou bash segue barrado | idem (`texto-barra-heredoc-gravado-roda-*`, `-bash-executa-*`, `-sh-*`) | decisão B do dono de 2026-10-27 | passou |
| Corpus tem os dois lados e o mínimo de itens | idem (mínimo de 30; 10 ou mais que passam) | pasta renomeada | passou |
| Pasta do git (PR A) e corpus anterior sem regressão | `PastaDoGit.test_corpus_pasta_passa_e_barra`, `test_hooks_volta_corpus`, `test_hooks_volta_propriedades` | regressão contra a base | passou |
| Cada guarda nova tem teste que a derruba | `forge-mutante` nas 4 specs | guarda sem teste | 46 mortos, 5 equivalentes declarados |

## Cenários e resultado real
Ambiente: worktree desanexada em `cf6bf0a`, Linux (WSL2), Python do sistema.

1. `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_hooks_volta_corpus tests.test_hooks_volta_propriedades`:
```
Ran 26 tests in 125.996s
OK
```
2. Mutação: `bin/forge-mutante tests/mutantes/hk3-parecer-texto.json tests/mutantes/hk3-parecer-texto-2.json tests/mutantes/hk3-parecer-texto-3.json tests/mutantes/hk3-parecer-texto-4.json`: 46 `morreu`, 5 `equivalente` (V2, V3, V4, V10, V12), `rc=0`.
3. Cobertura: `bin/forge-mutante --cobertura --base d14a7133eb608f3b02298931e76ddc8ccfe55c20` sobre `cf6bf0a`: primeira linha `base=d14a7133eb60… mb=d14a7133eb60… rev=cf6bf0adc637…`; `coberta · hooks/parecer.py:{90,93,102,103,105,107,108,117,122,123,126,129,569,610}`, todas `declarado, não provado`; sem `não coberta` nem `isenta` em `hooks/`.
4. Vermelho antes do verde: `bin/forge-testes --vermelho d14a7133eb608f3b02298931e76ddc8ccfe55c20 --modulos test_hooks_parecer_pasta`:
```
vermelho: base=d14a7133eb60 head=cf6bf0adc637 módulos=test_hooks_parecer_pasta (restrito por --modulos)
tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_pasta_passa_e_barra · H=ok · B=ok · não prova (passa na base)
tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_texto_passa_e_barra · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=1; prova (asserção)=1
rc=0
```
5. Mutantes Q1 a Q9 e sondas próprias: acima (`rc=1` na spec dos meus 7 mutantes: 1 morto, 6 sobreviventes analisados).
6. Acessibilidade e E2E de navegador: não se aplicam (hook de linha de comando).
7. Suíte completa: não rodada por ordem do dono (carga; só os módulos do item); ela roda uma vez no pre-push e no CI do PR.
