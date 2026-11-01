---
tipo: qa
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido-p2
commit: 11a3bdbaac2c6f53b80dcad437bcd3e9fb2fab38
parecer: reprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-01
---
# QA: heredoc-rapido, passo 2

Etapa E1.10. Diff lido: `299f01f..11a3bdb` (o que o passo 2 acrescenta à develop atual): `hooks/_comum.py` +23/-10, `tests/test_hooks.py` +24/-3, 6 fixtures C-8 (a a f) em `tests/hooks/conformidade/`, spec `tests/mutantes/heredoc-rapido-p2.json`, fragmento de changelog. O pedido: marca curta `__fh` (fonte única `marca`/`MARCAS`) e a `aspa_escapada` lida na linha sem marcas (`sem_marcas=resto`). Os pareceres anteriores deste arquivo eram do passo 1 (#417) e foram substituídos.

## M14 (agents/tech-lead.md:19)
`git diff --numstat --no-renames 299f01f 11a3bdb`: contam `hooks/_comum.py` 33 e `tests/test_hooks.py` 27, total 60 linhas (limite 150); fixtures, spec e changelog ficam fora. Um comportamento (a leitura da linha marcada fica mais barata), uma classe em `hooks/`. Cumpre a M14.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-2: a marca é palavra comum, entre espaços, fora de `COMPOSTOS`, só `MARCAS` a casa | `Hooks.test_marca_do_heredoc_e_palavra_comum_entre_espacos` | marca sem espaço (P1), marca com `=` (P2), terminador `__` (P7) | passou |
| C-8 (a)-(f): recusa igual (R-MAIN, R-VERIFY, R-CONFORMIDADE) | `Hooks.test_fixtures`: `heredoc-marca-c8a` a `c8f` | pipe, `eval "$(`, barra e pipe na outra linha, marca escrita pela pessoa, composto, `#` com aspa | passou |
| C-8 (g): dono procurado pela marca certa | `test_fixtures` (P6 morto) | dono menor se a marca erra | passou |
| C-7: 3000 heredocs dentro de 5,0 s (parede e CPU), 4 formas | `Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento` | 3000 heredocs, limite 5,0 s inalterado | passou |
| E1: decisão igual em todo o corpo de fixtures | `Hooks.test_fixtures` | todas as fixtures dos hooks | passou |
| C-1/C-3: a `aspa_escapada` (HOOK-ANSI-C) lida na linha sem marcas, não em texto vazio | nenhum | `sem_marcas` vazio troca o dono por menor | **sem teste (P5 sobreviveu, A1)** |

## Execução (head 11a3bdb, 2026-11-01)
- `bin/forge-mutante --cobertura --base 299f01fd88830223998939d47992967b33a942e1`, rc=0: `coberta · hooks/_comum.py:1751 · tests/mutantes/heredoc-rapido-p2.json:P3 · declarado, não provado`. Conferi o diff: as linhas 822, 827, 829, 847 (MARCA), 848 (MARCAS), 958 e 1253 mudaram; a spec do autor (P1 a P4) cobre 822, 847 e 1753; a 827 só por P4, que é equivalente declarado.
- `bin/forge-mutante tests/mutantes/heredoc-rapido-p2.json` (spec do autor, P1 a P4), rc=0:
```
P1 · morreu · hooks/_comum.py:822
P2 · morreu · hooks/_comum.py:847
P3 · morreu · hooks/_comum.py:1753
equivalente: P4 · na decisao: a aspa_escapada da linha marcada e a da linha sem marcas sao iguais ...
```
- Mutantes que somei (P5 a P7, na spec; limite 16), mesma rodada com os 7, rc=1:
```
P5 · sobreviveu · hooks/_comum.py:827   (sem_marcas=resto trocado por sem_marcas="")
P6 · morreu · hooks/_comum.py:829       (marca(operador + 1))
P7 · morreu · hooks/_comum.py:848       (MARCAS sem o terminador __)
```
- Testes: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures ...test_muitos_heredocs_recusam_dentro_do_orcamento ...test_marca_do_heredoc_e_palavra_comum_entre_espacos`: `Ran 3 tests in 103.081s`, `OK`.
- Medida de tempo do hook (3000 heredocs, parede em s, WSL, load 4 a 6, 5 medidas, mesmo roteiro do teste de orçamento; a base é um `git archive` de 299f01f):

| Forma | develop 299f01f | head 11a3bdb |
|---|---|---|
| um por linha | 1,51 1,45 1,47 1,40 1,43 | 1,16 1,17 1,17 1,16 1,16 |
| `&&` | 1,46 1,47 1,48 1,50 1,49 | 1,21 1,24 1,22 1,25 1,21 |

  Redução de cerca de 19% (um por linha) e 17% (`&&`). Com a razão CI/local do pedido (2,6 a 3,1), o pior caso (1,25) dá 3,3 a 3,9 s no runner, abaixo dos 4,5 s de alerta e dos 5,0 s. A medida no runner sai do CI do PR (E1.11), não daqui.

## Por que P5 importa
Com `sem_marcas=""`, a guarda HOOK-ANSI-C deixa de valer para a linha marcada. Comparando `tirar_heredocs` do head e do mutante em 6000 linhas aleatórias, saiu diferença em 2, e uma delas dá dono menor: um comando com `$'\''`, `$'a\'b'`, um heredoc `<<F` e `; bash` na mesma linha, com `git push origin main` no corpo, devolve dono sem o `bash`, então o corpo passaria como dado (C-3: nunca dono menor). Na decisão ponta a ponta a recusa continua, porque outra guarda (R-CONFORMIDADE: `$'` com ação crítica) fala antes; uma fixture de conformidade não mata o P5 (testei: passa com o mutante). Só um teste no nível de `tirar_heredocs` o mata.

## Achados
- A1 (bloqueante) tests/test_hooks.py:1682 · P5 sobreviveu (`sem_marcas=""`, hooks/_comum.py:827): nenhum teste guarda que a `aspa_escapada` é lida na linha sem marcas; o dono sai menor (sem o `bash`) numa linha com `$'\''` e heredoc. Falta teste em `tirar_heredocs`; a spec P5 já está escrita.
- A2 (recomendado) tests/test_hooks.py:1826 · a forma `x=$(` do orçamento recusa pelo teto de palavras (6004 palavras), não por R-MAIN: mede a leitura da marcada, mas a ordem das recusas (C-7, a regra específica fala primeiro) não é provada por ela.
- A3 (recomendado) docs/pedidos/heredoc-rapido.md:1 · a medida no runner do CI (alerta acima de 4,5 s, teto 5,0 s) sai do CI do PR (E1.11); local, o pior caso estimado é 3,9 s.

## Parecer
Reprovado por A1: o mutante P5 sobrevive e a regra pede teste ou equivalência aceita; aqui há diferença provada no nível de `tirar_heredocs`, só sem efeito ponta a ponta. O resto cumpre: M14 (60 linhas), recusas iguais nas 6 fixtures C-8, P1 a P3, P6 e P7 mortos, o tempo cai 17 a 19% e o orçamento de 5,0 s continua. Bugs de produção: 0. Não rodei `forge-testes --vermelho` (fora do brief).
