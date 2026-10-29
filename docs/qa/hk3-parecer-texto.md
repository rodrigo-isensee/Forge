---
tipo: qa
contrato: 1
pedido: hk3-parecer-texto
branch: melhoria/hk3-parecer-texto
commit: 7b2a225fb476be9c09c3b1a2b41792b7fcaec6ad
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: hk3-parecer-texto (PR B do HK3: o hook parecer aceita a palavra do merge, do pull ou do gh pr que só aparece no texto)

Plano: pedido de correção do controle do Forge, sem especificação de UX; as obrigações são o E2 do pedido HK3-PARECER e as decisões técnicas de 10:40 (palavra crítica no texto: merge-base, `sh -c` inofensivo, corpo de heredoc; M3 mantido para python3, git, gh e forge-check) e de 2026-10-29 12:34 (isenção do heredoc só em chamada inteira de `cat`; `sed -n <números>p <arquivo>` lido como `cat`). Diff conferido: `d14a713...7b2a225`, só `hooks/parecer.py` (+47 -8), `tests/test_hooks_parecer_pasta.py` (+9), 57 fixtures `texto-*`, 3 specs de mutantes, `docs/hooks.md` e o fragmento do changelog; escopo igual ao da entrega. Carga conferida antes de cada rodada (abaixo de 7).

## Achados
- A1 (recomendado) hooks/parecer.py:516 · a troca `SED_LE.sub(r"cat\2", comando)` não tem mutante declarado (a `--cobertura` só lista condição Python); o mutante Q1 que escrevi, sem a troca, morre no corpus, então o teste a protege; incluir na spec do autor (AR-1)

## Detalhe dos achados
- Nenhum bloqueante. A conferência da lista de mutantes contra o diff: toda condição Python mudada (linhas 88, 91, 101, 103, 106, 546, 587) tem mutante declarado na saída de `--cobertura`; as constantes `MERGE`, `SED_LE`, `SO_CAT`, `LE_O_TEXTO`, `SO_ESPERA` e `CONTROLE` (linhas 36 a 47) têm T14 a T39. Só a linha 516 (chamada, não condição) ficou sem, e o meu Q1 prova o teste.
- Mutantes extras meus (Q1 troca do `sed -n` removida, Q2 terminador do `SED_LE` removido, Q3 lookahead do `MERGE` removido): os três morrem em `test_corpus_texto_passa_e_barra`.
- Sondas próprias (46 linhas, repositório descartável em `develop`, branch `melhoria/x`, sem parecer; hook sobre o head): barram (rc=2) `git merge` depois de `cat <<'EOF'`, `cat … && git merge`, `sh -c 'grep …; git merge …'`, `sh -c` com laço e merge no fim, `sh -c "echo $(git merge …)"`, `sh -c` com crase, `sh -c` com quebra de linha, `&` e pipe, `sed -n … | sh -c 'git merge …'`, heredoc sem aspas com `$(git merge …)`, crase ou `$(gh pr merge …)` no corpo de `cat`, `sed -n` e `sed -n … <<EOF`, e `sed -n 1p f g h ; git merge`. Passam (rc=0) os casos de texto: corpo de heredoc só de `cat` com a palavra, `git merge-base`, `merge-bases`, `sh -c 'echo a' -c '…'` e `sh -c 'cat f' -- git merge …` (a palavra vira argumento posicional, que o bash não roda). Nenhum caminho novo de execução sem parecer achado.
- Limite conhecido, igual ao da base e fora do E2: `sed -n 1p -e 'e git merge …' f` e `sed -n 1pe f` passam (o `SED_LE` não os troca por `cat`, e o hook não lê o programa do sed); ofuscação registrada pelo pedido.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2: `git merge-base` não é merge | `PastaDoGit.test_corpus_texto_passa_e_barra` (`texto-passa-merge-base-*`, `texto-barra-merge-base-e-merge`) | `merge-base` x `merge` na mesma linha | passou (T14 a T16, Q3 morrem) |
| E2: corpo de heredoc só de `cat` (e `sed -n <números>p` lido como `cat`) é texto | idem (`texto-passa-heredoc-*`, `texto-passa-grep-com-merge-no-argumento`) | só `cat`, sem `;`, pipe, aspa ou `$` | passou (T10 a T13, T17 a T26, Q1, Q2 morrem) |
| E2: `sed -i`, `sed` com `e`, opção depois, metacaractere tiram a isenção | idem (`texto-barra-heredoc-gravado-e-sed-*`, `texto-barra-sed-com-metacaractere-nao-vira-cat`) | limite do `SED_LE` | passou |
| E2: `sh -c` cujo texto só lê ou espera passa | idem (`texto-passa-sh-c-*`) | só `grep`, `cat`, `sleep`, `echo`, laços e condições | passou (T27 a T39 morrem) |
| E2: `sh -c` que executa merge, pull ou gh pr, com crase, `$( )`, processo, aspa sem par, argumentos ou `eval` segue barrado | idem (`texto-barra-sh-c-*`, `texto-barra-eval-*`) | texto que o shell executa | passou |
| M3: heredoc gravado que roda python3, git, gh, forge-check, sh ou bash com merge, pull ou gh pr segue barrado | idem (`texto-barra-heredoc-gravado-roda-*`, `texto-barra-heredoc-bash-executa-*`, `texto-barra-heredoc-sh-*`) | decisão B do dono de 2026-10-27 | passou |
| Corpus tem os dois lados e o mínimo de itens | idem (mínimo de 30 fixtures; 10 ou mais que passam) | pasta renomeada | passou (57 fixtures `texto-*` novas mais 1 antiga) |
| Pasta do git (PR A) e corpus anterior sem regressão | `PastaDoGit.test_corpus_pasta_passa_e_barra`, `test_hooks_volta_corpus`, `test_hooks_volta_propriedades` | regressão contra a base | passou |
| Cada guarda nova tem teste que a derruba | `forge-mutante` nas specs `hk3-parecer-texto{,-2,-3}.json` (39 mutantes) | guarda sem teste | passou (39 mortos) |

## Cenários e resultado real
Ambiente: worktree desanexada em `7b2a225`, Linux (WSL2), Python do sistema, carga de 1 minuto abaixo de 7 antes de cada rodada.

1. Testes do item e vizinhos: `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_hooks_volta_corpus tests.test_hooks_volta_propriedades`:
```
Ran 26 tests in 152.566s
OK
```
2. Mutação: `bin/forge-mutante tests/mutantes/hk3-parecer-texto.json tests/mutantes/hk3-parecer-texto-2.json tests/mutantes/hk3-parecer-texto-3.json`: T1 a T39 `morreu`, `rc=0` (sem sobrevivente nem equivalente). Linhas: parecer.py 36, 41, 44 a 47, 88, 91, 101 a 107, 546, 587.
3. Cobertura: `bin/forge-mutante --cobertura --base d14a7133eb608f3b02298931e76ddc8ccfe55c20`:
```
base=d14a7133eb60… rev=7b2a225fb476…
coberta · hooks/parecer.py:88 · …-2.json:T27, T28 · declarado, não provado
coberta · hooks/parecer.py:91 · …-2.json:T29, hk3-parecer-texto.json:T1, T2 · declarado, não provado
coberta · hooks/parecer.py:101 · T3
coberta · hooks/parecer.py:103 · T4, T5
coberta · hooks/parecer.py:106 · T6, T7, T8, T9
coberta · hooks/parecer.py:546 · T10, T11, T12
coberta · hooks/parecer.py:587 · T13
```
Sem linha "não coberta" nem "isenta".
4. Vermelho antes do verde: `bin/forge-testes --vermelho d14a7133eb608f3b02298931e76ddc8ccfe55c20 --modulos test_hooks_parecer_pasta`:
```
vermelho: base=d14a7133eb60 head=7b2a225fb476 módulos=test_hooks_parecer_pasta (restrito por --modulos)
revertidos à base: changelog.d/hk3-parecer-texto.md, docs/hooks.md, hooks/parecer.py
tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_pasta_passa_e_barra · H=ok · B=ok · não prova (passa na base)
tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_texto_passa_e_barra · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=1; prova (asserção)=1
rc=0
```
5. Sondas próprias e mutantes Q1 a Q3: acima. Mutantes Q1 a Q3: `bin/forge-mutante` numa spec em `$TMPDIR`, os três `morreu`.
6. Acessibilidade e E2E de navegador: não se aplicam (hook de linha de comando).
7. Suíte completa: não rodada por ordem do dono (carga); ela roda uma vez no pre-push e no CI do PR.
