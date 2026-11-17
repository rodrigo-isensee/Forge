---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-forge-sempre-atual
commit: 2bcad3855c8a1e54062b90ff3b1b6baab9eedd82
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 FORGE-SEMPRE-ATUAL (E1.53, ADR 0017)

Head 2bcad385, base 45615e20. Sem PR: não há check-run `bateria` para citar; a suíte inteira fica com o CI do PR. Rodei só os módulos tocados, com `TMPDIR` próprio, em primeiro plano.

## Achados
- A1 (recomendado) tests/test_oraculo_sempre_atual.py:458 · no sandbox, `/proc` é de outro namespace: 9 testes de ocupação (S2/S6) não se provam aqui; confira no CI do PR que o oráculo passa inteiro (59 testes).

## Critério → teste → resultado
O critério de parada é o do desenho (RD1 a RD11, D30b, seções 2 a 5 e 8) e da ADR 0017, no oráculo `tests/test_oraculo_sempre_atual.py` (59 testes).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Oráculo RD/D30b/SEG/S (atualiza, volta, registro, estado, trampolins, aviso, nunca reabre) | `test_oraculo_sempre_atual` | prazo, `ref` igual ao alvo, versão maior que a quebrada, permissão | 50 de 59 passam com a guarda de `/proc` neutralizada em cópia; 9 só caem na pré-condição `vivo()` (ambiente) |
| Ocupação S2/S6 (claude vivo, trava, suíte, integração, dúvida) | classe `Ocupacao` e `NuncaReabre.test_nao_mata...` | leitura em dúvida adia | não provado no sandbox; falta o CI (A1) |
| Núcleo, entradas, `forge atualizar`/`voltar-versao`, doutor, forge-check | `test_sempre_atual` (68), `test_atualizar` (109, 3 pulos de ambiente), `test_doutor` (105), `test_testes_tocados` (162, 1 pulo), `test_forge` (639) | n/a | passou |
| Mutantes declarados, 1 por guarda mudada | 8 specs, 77 mutantes | n/a | todos morreram, nenhum sobrevivente, nenhum equivalente |

## Cenários e resultado real
Ambiente x defeito (o autor viu o mesmo):
- No sandbox `/proc/self` (12) difere de `os.getpid()` (5): outro namespace de pid. `proc_coerente()` devolve falso por desenho (ADR 0017 item 5: leitura em dúvida conta como ocupado), então o escopo sai `adiado:duvida:proc` e 40 testes do oráculo caem (39 falhas, 1 erro: `FileNotFoundError` em `add.pid`, consequência do add que não rodou). Todos os 40 são o mesmo sintoma (`adiado:duvida:proc`, versão que não subiu). `unshare --pid --mount-proc` é negado, então não há como reproduzir um `/proc` coerente aqui: ambiente, não defeito.
- Prova do descarte: cópia de `git archive HEAD` em `$TMPDIR` com `return True` na primeira linha de `proc_coerente` (nunca na árvore do autor): 50 passam, 9 falham, todas em `vivo()` (`'' != 'claude'`: o `comm` do filho gerado não se lê no namespace alheio). Nenhuma falha de lógica.
- Prazo sob carga: não vi falha de prazo; o oráculo levou 58 a 79 s.
- Oráculo editado depois do commit 500e04c7: só 2bcad385 (duas linhas, `remoto_sem_manutencao` no repositório bare); não afrouxa nada. O autor é o mesmo do commit do oráculo; o hook `conformidade` barra a escrita de agente, e o commit é de ambiente. Registro para o review.
- Vermelho antes do verde (`forge-testes --vermelho`) não rodei: o brief limita aos módulos tocados e às specs.

## Provas
- Módulos: oráculo 59 testes, 19 ok no sandbox sem neutralizar e 40 por `/proc`; `test_sempre_atual` Ran 68 OK; `test_atualizar` Ran 109 OK (skipped=3); `test_doutor` Ran 105 OK; `test_testes_tocados` Ran 162 OK (skipped=1); `test_forge` Ran 639 OK.
- Mutantes (rc 0 em todas): v047-sempre-atual-1 16 mortos, -2 10, -3 15, -4 8, -5 8, -6 2, `fixacao-do-dono` 7, `v047-atualizar-hook-local` 11. Mortos com `(erro) o teste declarado deu erro sob o mutante e passa sem ele`: M25 (spec 2, `forge_sempre_atual.py:303`), A12 a A14 (spec 5, `forge-check:9365,9376,9382`), M4 e M6 da fixação (`forge_sempre_atual.py:929,916`); morrem por erro do teste, não por asserção: ver A1 só se o CI divergir.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: Ran 4 tests, OK.
