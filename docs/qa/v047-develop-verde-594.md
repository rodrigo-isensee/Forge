---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-develop-verde-594
commit: 3932b52db16af1e0d21fdbc2a122a8ce01b77635
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047-develop-verde-594

Conserto da develop depois do #594 (PR 603): mapa do `bin/forge-testes` (spec de mutantes leva também ao `test_forge_mutante`), `ConferirTodas` com `self.env`, specs de mutantes realinhadas (AR-12). Base 58dfa2ab, head 3932b52d.

## Achados
- A1 (recomendado) tests/mutantes/hooks-corpus-rapido.json:1 · `forge-mutante --conferir --todas` ainda sai 1 com 31 trechos ambíguos ou ausentes em specs antigas (eram 38 na base); nenhum teste ou CI roda isso no repositório real, então não bloqueia (R-QA).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Spec nova leva ao campo `testes` e ao test_forge_mutante | tests.test_testes_tocados.MapaDosNovos.test_spec_nova_leva_aos_modulos_do_campo_testes_e_ao_test_forge_mutante | n/a | passou (cai com o forge-testes da base) |
| Spec ilegível ou sem teste segue na suíte completa | MapaDosNovos.test_spec_ilegivel_sem_teste_ou_com_teste_de_fora_segue_na_completa (mutante T8) | spec sem `testes` | passou |
| ConferirTodas monta self.env | tests.test_forge_mutante.ConferirTodas | n/a | passou |
| Specs realinhadas à fonte | mutantes T1-T8 de v047-specs-conferidas.json | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_testes_tocados tests.test_forge_mutante`: Ran 285 tests, OK (skipped=1; o pulo é o sandbox sem /proc do mesmo namespace). Suíte inteira: check-run `bateria` do CI, não rerrodada aqui.
- Vermelho: `forge-testes --vermelho 58dfa2ab...` estourou o prazo local (580 s, rc 124: sem veredito, não vale como vermelho). Prova manual numa cópia em $TMPDIR com `bin/forge-testes` da base: `MapaDosNovos` falha (FAILED failures=1; esperado inclui `test_forge_mutante`, obtido sem ele). Com o head, passa.
- Mutantes: `bin/forge-mutante tests/mutantes/v047-specs-conferidas.json` rc 0: T1 a T8 morreram (bin/forge-mutante:693,696,708,720,724,969,970; bin/forge-testes:320). `--cobertura --base 58dfa2ab`: `coberta · bin/forge-testes:320 · ...:T8 · declarado, não provado`; única linha de guarda mudada em código, sem mutante faltando. As specs editadas foram só alinhadas, sem guarda nova.
- `forge-check docs`: rc 0.
- PA-7 conferido: achados-recorrentes lido; AR-12 é a classe do item e nenhuma linha nova é necessária.
