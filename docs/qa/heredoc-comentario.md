---
tipo: qa
contrato: 1
pedido: heredoc-comentario
branch: melhoria/heredoc-comentario
commit: 262535c43f124882155c67d9fbd89b2bba788c2b
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-01
---
# QA: heredoc-comentario

Etapa E1.4. Base f534013 (develop, com o passo 2 do heredoc-rapido), head 262535c (revalidação da volta que trouxe a develop; o parecer anterior aprovou 1fa4398). Sem especificação de UX (pedido de correção do hook): as obrigações são o PQ-1 do pedido e os controles C-1 a C-6 do modelo de ameaças. A medida no runner do CI fica com a E1.5 (decisão do Jarvis de 2026-11-01 12:36).

## Achados
- A1 (recomendado) tests/hooks/conformidade/heredoc-comentario-3000-bash-no-ultimo-push-main-no-corpo-bloqueia.json:28 · a fixture C-6 (b) aceita qualquer recusa ("R-"), não só a regra do corpo; o oráculo test_donos_dos_heredocs_iguais_aos_da_base guarda o dono, então o risco é baixo.
- A2 (recomendado) tests/test_hooks.py:1795 · o C-6 (e), o vigia desligado (L1) com 3000 heredocs, não tem fixture; o teto de custo vale sem SIGALRM, mas só o teste do orçamento (vigia largo) o exercita, e M6 e M9 o matam.
- A3 (recomendado) tests/test_hooks.py:1892 · o teste C-5 (1000 heredocs, vigia de 3 s) passa também na base (não saiu na lista de falhas da base): ele guarda a não regressão do vigia, mas não prova a correção; quem prova é o teste do orçamento.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PQ-1 (3000 `# c` em 5,0 s) | test_muitos_heredocs_recusam_dentro_do_orcamento (6 formas novas) | N=3000, limite 5,0 s | passou; base falha nas 6 (22 a 41 s) |
| C-1 oráculo | test_donos_dos_heredocs_iguais_aos_da_base (mais de 4200 linhas) | N 1 a 40, 7 comentários, 7 separadores, 7 donos | passou |
| C-2 linear | formas do orçamento + mutantes M6, M9, M10 | N=3000 | passou (mortos) |
| C-3 orçamento | mesmo teste, formas `# c`, `x#c`, `;#c`, linha de `#`, `\| cat > f # c` | 5,0 s e mesma recusa da base | passou |
| C-4 teto de custo | test_dono_largo_acima_do_teto_de_custo | 150 mil caracteres; resto acima do teto = ilegível | passou; M4 a M8, M11, M12 mortos |
| C-5 vigia de produção | test_forma_com_comentario_recusa_pela_regra_com_o_vigia_de_producao | 1000 heredocs, 3 s | passou (R-MAIN) |
| C-6 (a) a (d) | 4 fixtures heredoc-comentario-3000-* (test_fixtures) | 3000 heredocs | passou |
| C-6 (e) | sem fixture | n/a | A2 |
| M14 (150 linhas) | `git diff --numstat` em hooks/ e tests/test_*.py | teto de 150 | 148 linhas sobre f534013 (40+12 e 89+7); uma classe de comportamento em hooks/ |

## Cenários e resultado real
- `bin/forge-mutante --cobertura --base e25d379`: rc=0; cobertas 923 (M10), 950 (M9), 954 (M11), 957 (M6), 958 (M12), todas "declarado, não provado". Conferi contra o diff: cada condição nova de `segmento` e `montar` tem mutante; `vestir` e `citadas` só movem código.
- `bin/forge-mutante tests/mutantes/heredoc-comentario.json`: rc=0, 13 mortos (M1 a M12, M4b), nenhum sobrevivente.
- Medida local (5 execuções, hook de produção, 3000 heredocs, sem carga extra):
  - develop e25d379, `# c`: 3,26 / 3,09 / 3,09 / 3,08 / 3,08 s (recusa pelo prazo de 3 s, mensagem de prazo, não a R-MAIN); `| cat > f # c`: 3,09 / 3,10 / 3,10 / 3,09 / 3,40 s (prazo).
  - head 1fa4398, `# c`: 1,75 / 1,76 / 1,88 / 1,78 / 1,77 s (R-MAIN); `| cat > f # c`: 1,24 / 1,30 / 1,29 / 1,30 / 1,35 s (teto de 6004 palavras, igual à base).
- Testes: test_muitos_heredocs_recusam_dentro_do_orcamento, o oráculo, o dono largo e o C-5: 4 testes OK (161 s). test_fixtures e tests.test_hooks_volta_corpus (corpus de recusas): 17 testes OK (149 s).
- Vermelho: `forge-testes --vermelho e25d379` saiu rc=2 ("test_hooks · sem veredito (prazo, sinal ou executor sem registro)"), sem veredito, e não vale. Recuo manual, teste do head sobre o código da base, numa worktree descartável: `vermelho: base=e25d379 head=1fa4398`; o orçamento falha nas 6 formas novas (`' # c'` 21,9 s; `' x#c'` 29,8 s; `';#c'` 33,4 s; `'linha de #'` 32,8 s; `'cat a<i> # c'` 29,7 s; `'| cat > f # c'` 41,3 s, todas "not less than 5.0"); o oráculo e o dono largo dão ERROR na base (sem `vestir`/`segmento`), o que também prova que não existiam.
- Não rodei a suíte inteira nem o pre-push antes do parecer; o pre-push do envio a roda.

## Revalidação no head 262535c (volta que trouxe a develop f534013)
- Delta lido (`forge-check delta --parecer`, 1fa4398..262535c): `hooks/_comum.py` (822-855, 990, 1281, 1757-1781: a mescla do passo 2, `DonosDosHeredocs.montar` com a versão desta branch e `citadas` via `MARCAS.sub`), `tests/test_hooks.py` (1682-1706 e 1828-1875: formas das duas linhas no teste do orçamento), e o que veio da develop (6 fixtures `heredoc-marca-c8*`, `tests/mutantes/heredoc-rapido-p2.json`, fragmento do passo 2). Já lido e não relido: fixtures C-6, spec de mutantes, achados A1 a A3 (seguem valendo, recomendados).
- Diff contra a develop f534013 (`git diff f534013 262535c -- hooks tests/test_hooks.py`): `montar` agora cacheia por segmento (`segmento`, `self.citados`, `iguais`), compara por `id`, alarga ao teto de custo (C-4) e vira `vestir`; a recusa por palavras (6004) e a R-MAIN ficam como na develop. Sem linha de guarda nova sem mutante.
- M14 (agents/tech-lead.md:19, teto de 150 linhas): `git diff --numstat` em hooks/ e tests/test_*.py contra f534013 dá 52 em hooks/_comum.py (40+12) e 96 em tests/test_hooks.py (89+7), 148 linhas, abaixo do teto; uma classe de comportamento em hooks/ (a leitura do `#` na linha do heredoc). Corpus, fixtures e mutantes ficam fora da conta. Cumpre.
- `bin/forge-mutante --cobertura --base f534013`: rc=0; cobertas 933 (M10), 960 (M9), 964 (M11), 967 (M6), 968 (M12), "declarado, não provado".
- `bin/forge-mutante tests/mutantes/heredoc-comentario.json`: rc=0, 13 mortos (M1 a M12, M4b), nenhum sobrevivente.
- Medida local, 5 execuções, 3000 heredocs, `rodar` do teste (hook real, sem a carga de outros processos; load 2 a 3): develop f534013, `# c`: 19,60 / 19,16 / 19,80 / 20,02 / 19,87 s (R-MAIN, tarde); `| cat > f # c`: 39,09 / 39,84 / 39,68 / 39,40 / 40,85 s (teto de 6004 palavras). Head: `# c`: 1,39 / 1,42 / 1,47 / 1,47 / 1,55 s (R-MAIN); `| cat > f # c`: 0,91 / 0,95 / 0,96 / 0,94 / 0,95 s (teto de 6004 palavras, igual à base). A medida no runner do CI fica com a E1.5.
- Testes: orçamento, oráculo C-1, dono largo e C-5 (4 testes) OK em 154 s; `Hooks.test_fixtures` e `test_hooks_volta_corpus` (17 testes) OK em 139 s. Código de hooks/ e tests/ do worktree igual ao de 262535c.
- Vermelho: o do parecer anterior segue valendo para os testes novos da branch (a base não tem `vestir`/`segmento`); na develop f534013 as 6 formas novas continuam lentas (19 a 40 s contra o limite de 5,0 s).
- Não rodei a suíte inteira; o pre-push do envio a roda.

## Parecer
Aprovado no head 262535c. A branch cumpre a M14: 148 linhas contáveis sobre a develop f534013 (limite 150), um comportamento em hooks/, corpus e fixtures fora da conta; a recusa não muda (oráculo C-1) e o teto só alarga o dono ou recusa (T6). Sem bugs; três recomendações que não devolvem.
