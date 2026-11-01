---
tipo: qa
contrato: 1
pedido: heredoc-rapido
branch: melhoria/heredoc-rapido-p2
commit: 3a8c5f064f8dbc483f7ba1dce7b2fc7c3f4e58ef
parecer: aprovado
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
| C-1/C-3: a `aspa_escapada` (HOOK-ANSI-C) lida na linha sem marcas, não em texto vazio | `Hooks.test_aspa_escapada_e_lida_na_linha_sem_marcas` | `sem_marcas` vazio troca o dono por menor | passou (volta 1: teste novo, P5 morre) |

## Revalidação no head (3a8c5f0, 2026-11-01)
`forge-check delta --parecer docs/qa/heredoc-rapido.md` listou `11a3bdb..3a8c5f0`: `tests/test_hooks.py` +10 (linhas 1697-1706) e `tests/mutantes/heredoc-rapido-p2.json` +32 (linhas 44-75). Li só isso: o teste `test_aspa_escapada_e_lida_na_linha_sem_marcas` (dono com `|` quando a linha tem `$'\''`, sem `|` quando não tem) e a lista de testes de P5, P6 e P7 na spec. `hooks/` não mudou desde 11a3bdb. A worktree está à frente (43fb2b5) só com os pareceres de review e segurança; o código é o de 3a8c5f0.
- `bin/forge-mutante --cobertura --base 299f01fd88830223998939d47992967b33a942e1`, rc=0: `coberta · hooks/_comum.py:1751 · tests/mutantes/heredoc-rapido-p2.json:P3 · declarado, não provado`.
- `bin/forge-mutante tests/mutantes/heredoc-rapido-p2.json` (7 mutantes), rc=0, rev=43fb2b5881a6 (uma rodada anterior saiu rc=2, "árvore mudou durante a rodada", porque os outros pareceres foram gravados no meio; descartada e refeita):
```
P1 · morreu · hooks/_comum.py:822
P2 · morreu · hooks/_comum.py:847
P3 · morreu · hooks/_comum.py:1753
equivalente: P4 · na decisao: a aspa_escapada da linha marcada e a da linha sem marcas sao iguais ...
P5 · morreu · hooks/_comum.py:827
P6 · morreu · hooks/_comum.py:829
P7 · morreu · hooks/_comum.py:848
```
- Testes (`test_fixtures`, `test_muitos_heredocs_recusam_dentro_do_orcamento`, o teste novo de P5 e `test_marca_do_heredoc_e_palavra_comum_entre_espacos`): `Ran 4 tests in 212.176s`, `OK` (load 12 a 14).
- Tempo do hook, 3000 heredocs, 5 medidas em s (parede; load 12 a 14, mais ruidoso que a medida anterior), develop 299f01f contra head:

| Forma | develop 299f01f | head 3a8c5f0 |
|---|---|---|
| um por linha | 1,98 1,97 1,93 3,35 1,55 | 1,59 1,62 1,45 1,61 1,41 |
| `&&` | 1,65 2,02 1,92 2,14 1,97 | 1,70 1,70 1,45 1,58 1,42 |

  Mediana: 1,97 para 1,59 (um por linha) e 1,97 para 1,58 (`&&`), cerca de 20% menos; a medida limpa anterior (load 4 a 6) deu 17 a 19%. A medida no runner sai do CI do PR (E1.11).

## Achados
- A1 (recomendado) tests/test_hooks.py:1833 · a forma `x=$(` do orçamento recusa pelo teto de palavras (6004), não por R-MAIN: a ordem das recusas (C-7) não é provada por ela. Não bloqueia.
- A2 (recomendado) docs/pedidos/heredoc-rapido.md:1 · a medida no runner do CI (alerta acima de 4,5 s, teto 5,0 s) sai do CI do PR (E1.11); local, o pior caso fica em cerca de 2 s.

## Parecer
Aprovado. O bloqueante da rodada anterior (P5 sobrevivente) fechou: o teste novo guarda a leitura da `aspa_escapada` na linha sem marcas e os mutantes P1 a P3 e P5 a P7 morrem (P4 equivalente declarado). A branch cumpre a M14: 60 linhas contadas (limite 150), um comportamento, uma classe em `hooks/`. Recusas iguais nas 6 fixtures C-8, orçamento de 5,0 s mantido e o tempo cai cerca de 20%. Bugs de produção: 0. Não rodei `forge-testes --vermelho` (fora do brief); o teste novo foi visto falhando pelo mutante P5.
