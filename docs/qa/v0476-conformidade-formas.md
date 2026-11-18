---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0476-conformidade-formas
commit: eb18768bd45af2addb34c9603b5de85d305837f0
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
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
