---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0476-conformidade-formas
commit: 391011df0cac676754564741cc370fb38c656ec9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0476-conformidade-formas (E3.50, E3.97)

## Achados

## Critério → teste → resultado
Sem especificação de UX: as obrigações são os itens do changelog (E3.50) e a ADR 0011 (nada mais frouxo).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3.50: recusa por `$` diz o valor literal | `test_hooks.Hooks.test_fixtures_do_e350` (10 fixtures); mutante M1 | variável em caminho protegido | passou, M1 morreu |
| E3.50: recusa por heredoc diz `FORMA_DO_HEREDOC` | mesmo teste; M2 | `<<` sem aspas bloqueia, com aspas libera | passou, M2 morreu |
| E3.50: leitura só com `$` diz caminho literal | mesmo teste; M3 | variável de caminho recusada, literal liberado | passou, M3 morreu |
| E3.50: brief cita o texto único do heredoc | `test_brief_forma_aceita.FormasNoBrief.test_brief_traz_a_forma_do_heredoc_do_hook`; M4 | forma em bloco | passou, M4 morreu |
| E3.50: laço do log da skill com caminho literal | `test_esperar_estado.LacoDoLog`; M5, M6, spec `pn5-espera-envio` (M1-M5) | teto 150 s, log ausente (rc 1) | passou, todos morreram |
| ADR 0011: nada fica mais frouxo | fixtures `e350-*-bloqueia` ao lado de cada `-libera` | chaves entre duplas, heredoc sem aspas | passou |

## Cenários e resultado real
- `test_brief_forma_aceita.py` (discover, TMPDIR): 18 testes, OK. `test_esperar_estado.py`: 15 testes, OK. `test_fixtures_do_e350`: 1 teste, OK.
- Vermelho (`forge-testes --vermelho 3d8ad440 --modulos tests.test_brief_forma_aceita`): `test_brief_traz_a_forma_do_heredoc_do_hook · H=ok · B=erro · prova (API ausente)`; `contagem: não prova (passa na base)=17; prova (API ausente)=1`. Para `test_hooks`, o vermelho completo estourou o prazo de 550 s (rc 124, sem veredito); a prova do teste de fixtures vem da mutação (M1-M3 morrem) e as fixtures `e350-*` são novas.
- Mutação, `bin/forge-mutante tests/mutantes/v0476-conformidade-formas.json`: `pedido=v0476-conformidade-formas rev=eb18768bd45a`; M1 a M6 `morreu`.
- Delta de spec editada: `bin/forge-mutante --base 3d8ad440 tests/mutantes/pn5-espera-envio.json`: `base=3d8ad440… rev=eb18768bd45a`; M1 a M5 `morreu`.
- Cobertura (`--cobertura --base 3d8ad440`): condições de conformidade.py 813, 816 e 1897 `coberta`, rc 0; o resto do diff é texto/shell sem condição Python.
- A bateria completa roda no CI do PR (check-run `bateria`); não rodada aqui.

## Revalidação (delta eb18768b..b4bd700e)
`forge-check parecer delta` lista `bin/forge-check` (ref_publicada, documento_sem_parecer, E3.49), `skills/esperar-estado/SKILL.md` e `envio-longo.md` (texto movido, sem regra nova de código).
- `tests.test_revisar_sha` (4), `tests.test_parecer_delta` (4), `test_esperar_estado` (15), `test_forge_tamanho` (24), `test_metricas_texto` (2), `test_ambiente_git` (20): OK.
- Vermelho: `forge-testes --vermelho eb18768b --modulos tests.test_revisar_sha,tests.test_parecer_delta`: `contagem: não prova (passa na base)=4; prova (asserção)=4`; os 4 que passam na base são testes de guarda, mortos pelos mutantes.
- Mutação: `bin/forge-mutante tests/mutantes/v0476-revisar-sha-delta.json --base eb18768b`: `base=eb18768bd45a... rev=b4bd700e8eeb`; M1 a M6 `morreu`.
- Catraca (`--base origin/develop`): só 3 linhas `R-CONFORMIDADE` (bin/forge-check, hooks/_comum.py, hooks/conformidade.py: rótulo `afrouxa-regra` do dono); nenhuma guarda sem mutante.
- Bateria completa: check-run `bateria` do CI do PR; não rodada aqui.

## Revalidação (delta b4bd700e..391011df)
Delta: `docs/hooks-fixtures.md` regenerado (E3.181) e merge limpo da `develop` (57a8cc8c); `e9986b4a` só acrescenta parecer de review. Nada de regra nova da branch.
- `tests.test_indice_fixtures` (7), `tests.test_hooks.Hooks.test_fixtures_do_e350` (1), `tests.test_metricas_texto` (2), `tests.test_ambiente_git` (20): OK.
- Catraca (`--base origin/develop`, rc 1): só as 3 linhas `R-CONFORMIDADE` (bin/forge-check, hooks/_comum.py, hooks/conformidade.py: rótulo `afrouxa-regra` do dono); nenhuma guarda sem mutante.
- Sem teste novo da branch no delta: vermelho e mutação do parecer anterior seguem valendo.
- Bateria completa: check-run `bateria` do CI do PR; não rodada aqui.
