---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae7-2-familias
commit: 22ca54c6464d3f29361f246623a97620e564a622
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: AE7.2 famílias geradas e alvo entrega do comparador (v0478 E107.5)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Famílias geradas somam ao corpus, semente fixa e impressa | `FamiliasGeradas.test_mesma_semente_da_os_mesmos_casos_e_cada_familia_tem_os_seus`, `test_familias_entram_no_corpus_com_a_semente_na_saida` | semente igual, família sem caso | passou |
| Caso gerado liberado no head é aceite novo; some no head é corpus-removido | `test_caso_gerado_que_o_head_libera_e_aceite_novo`, `test_caso_gerado_que_some_no_head_e_corpus_removido` | lado base x head | passou |
| Gerador sem semente fixa, que falha, que passa do prazo ou git que falha é recusado | `test_gerador_sem_semente_fixa_e_corpus_removido`, `test_gerador_que_falha_e_nao_verificavel`, `test_gerador_que_passa_do_prazo_e_nao_verificavel`, `test_git_que_falha_ao_ler_o_gerador_e_nao_verificavel` | prazo, rc != 0 | passou |
| Corpus ilegível ou só gerador | `test_corpus_que_nao_se_le_e_nao_verificavel`, `test_so_o_gerador_sem_corpus_e_medido` | corpus vazio | passou |
| Alvo entrega: aceite novo, sem aceite a mais, prazo, cópia por lado, sem fixture, extração, alvo desconhecido | `AlvoEntrega.*` (7 testes) | sem caso, não repositório, prazo | passou |
| Afrouxamento do E50 aparece como aceite novo | `CasoDoE50.test_afrouxamento_do_e50_aparece_como_aceite_novo` | n/a | passou |

## Cenários e resultado real
- Mutantes (R-QA, controle): 24 de 24 morreram nas 3 specs (`tests/mutantes/v0478-ae7-2-familias.json`, `-2`, `-3`); cada guarda do diff de `bin/forge_comparar.py` e `tests/comparar/geradores.py:38` tem mutante; nenhum sobrevivente, nenhum sem veredito.
- Vermelho antes do verde: `forge-testes --vermelho b0895f6cc --modulos test_comparar` saiu 2 (sem veredito: o módulo novo lê `geradores.py` na carga e a base não o tem). Prova manual equivalente: cópia do head com `bin/forge_comparar.py` da base, `-k Familias -k Entrega`: `Ran 17 tests ... FAILED (failures=12, errors=5)`; os 17 testes novos caem sem a implementação.
- `python3 -I -m unittest discover -s tests -p test_comparar.py`: 84 testes, 83 passam. A única falha é `LadosSeparados.test_hook_do_head_nao_alcanca_a_base`, que não é do diff.
- Teste `test_hook_do_head_nao_alcanca_a_base`: a falha é determinística no ambiente com `TMPDIR` abarrotado (aqui, 232 mil entradas): falhou 3 de 3 isolada, no head e na base `b0895f6cc`. Com `TMPDIR` limpo passa (3 de 3). Não é aleatório: o hook sondado varre `*/plugin/hooks/hooks.json` no pai do temporário, e esse glob varre o `TMPDIR` inteiro; num `TMPDIR` grande ou sob carga o hook estoura o prazo e o head fica aceite. O teste depende do tamanho e da carga do `TMPDIR`; é anterior ao item (mesma falha na base) e não bloqueia. O autor deve rodar com `TMPDIR` limpo; o CI tem `TMPDIR` limpo.
- Diff contra a lista: sem escopo novo; `tests/pesos-d4.json` sobe `test_comparar` de 3,8 para 103,7 s (módulo mede 80 a 166 s, coerente).

## Revalidação (volta única, delta cb2043bc..62d27eb6)
- `forge-check parecer delta`: no domínio `bin/forge_comparar.py`, `tests/test_comparar.py`, 3 specs de mutantes, `tests/pesos-d4.json`, changelog. Tetos do gerador (A2), `seguro` no nome da família (A1) e HOME/TMPDIR por caso (A3) lidos no diff; sem escopo novo.
- `TMPDIR` vazio, `python3 -I -m unittest discover -s tests -p test_comparar.py`: `Ran 89 tests in 141.213s · OK` (inclui `LadosSeparados`, que passa com `TMPDIR` limpo).
- `bin/forge-mutante tests/mutantes/v0478-ae7-2-familias-4.json --base cb2043bc55d7cf94bdc4fcaf0f4bfa17f9ee7995`: `base=cb2043bc55d7cf94bdc4fcaf0f4bfa17f9ee7995 ... rev=62d27eb6ca7c`; AE72-25 a AE72-29 `morreu` (bin/forge_comparar.py:109, 113, 113, 109, 423); nenhum sobrevivente.
- Sem achados.

## Revalidação (volta de CI, delta 62d27eb6..22ca54c6)
- `forge-check parecer delta`: no domínio, só `tests/mutantes/v0478-ae7-comparar.json`, `-3`, `-4`, `-6` e `tests/pesos-d4.json`; nenhum código de produção do AE7.2 mudou. A volta realinhou nove mutantes do AE7.1 à fonte atual (trecho `de` mais longo, para ficar único).
- `TMPDIR` vazio, `bin/forge-mutante --base 62d27eb6 tests/mutantes/v0478-ae7-comparar.json -3 -4 -6 --processos 2`: rc 0; CMP7 a CMP47 todos `morreu` (CMP22 em forge_comparar.py:320, CMP26 em :410; CMP23, CMP26 e CMP31 com `(erro)` sob controle verde); nenhum sobrevivente nem sem veredito.
- `bin/forge-mutante --conferir --todas` (`TMPDIR` vazio): nenhuma linha dos quatro specs `v0478-ae7-comparar*`; as 26 linhas restantes (ex.: `hk3-parecer-pasta-14`, `z075-prepush-relogio`, `v0441-*`) são de specs de outros pedidos, fora do diff, e não bloqueiam este item.
- Sem achados.
