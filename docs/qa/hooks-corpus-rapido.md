---
tipo: qa
contrato: 1
pedido: hooks-corpus-rapido
branch: melhoria/hooks-corpus-rapido
commit: 1ead0ed775d77d8bdb15034e8350521fda23434c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: hooks-corpus-rapido

Escopo: revalidação 3 do pedido HOOKS-CORPUS-RAPIDO (CorpusHeredocVoltaUnica em 3 módulos, decisão em lote com teste de equivalência, teto de 225 s por módulo, mapa do `bin/forge-testes`). Base 363ceee; delta desde 2c14a56 (parecer anterior, 873067c): só `tests/test_hooks_volta_lancador.py` (a sonda do lançador pula a forma com `-a` no `env` que a recusa) mais os pareceres e o fragmento de changelog. `bin/` e o apoio não mudaram no delta, então a lista de mutantes (M1 a M6) continua cobrindo todas as linhas de guarda do diff. Decisão do dono 2026-10-27 14:32 "C": mínimo 2 formas vivas no runner com GNU 9.4, 20 onde o `env` aceita `-a`; o cartão CI-ENV-ARGV0 devolve a prova de 20 ao CI no PR seguinte.

## Achados

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 mesmo conjunto de textos | `DECIDIDOS` do apoio, comparado com 363ceee | 6 testes, 79 a 7152 textos | passou (idênticos) |
| E1 decisão em lote = hook real | `test_decisao_em_lote_igual_ao_subprocesso_do_hook` | códigos 0 e 2 | passou |
| E1 driver do lote igual ao `__main__` dos hooks | `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook` | CRITICO, argumentos, pasta do hook | passou; M6 morre |
| E2 classe em 3 módulos | `test_hooks_volta_corpus/_lancador/_propriedades` | n/a | passou |
| E3 teto por módulo 225 s | `test_pesos_teto` (2 testes) | 225 e 225,1 s | passou |
| Mapa do `bin/forge-testes` | `test_testes_tocados` (81 testes) | 5 regras + FORGE_CHECK | passou; M1 a M5 morrem |
| Decisão do dono "C": sonda do lançador adaptada ao `env` | `test_lancador_fora_da_tabela_com_efeito_real` | `env` sem `-a` (2 vivas) e com `-a` (20 ou mais); decisões dos hooks integrais (75 ou mais textos, código 2) | passou nos dois ambientes; cai com a sonda trocada por `True` |

## Execução (CI=true, </dev/null, worktree em 1ead0ed)
- test_hooks_volta_corpus: 15 testes, OK, 63 s
- test_hooks_volta_lancador: 20 testes, OK, 87 s
- test_hooks_volta_propriedades: 8 testes, OK, 57 s
- test_hooks: 51 testes, OK, 117 s
- test_pesos_teto: 2 testes, OK, 1 s
- test_testes_tocados: 81 testes, OK, 17 s
- Todos abaixo de 225 s (o tempo varia com a carga da máquina; o teto vale por módulo do `pesos-d4.json`).
- Nesta máquina o `env` é o uutils 0.8.0 e há `gnuenv` 9.7, os dois aceitam `-a`: a sonda exige o mínimo de 20 formas vivas e passou.

## Env sem `-a` (o do runner)
Reproduzido com um `env` embrulhado que se declara "GNU coreutils 9.4" e sai 125 em `-a` (`invalid option -- 'a'`), em um `PATH` de links que exclui o `env`, o `gnuenv` e o `genv` reais (`$TMPDIR/qa-engineer-hooks-corpus-rapido/shadowbin`; `env -a x true` dá rc=125):
- Head 1ead0ed: `PATH=shadowbin CI=true python3 -m unittest tests.test_hooks_volta_lancador.LancadorDaVoltaUnica.test_lancador_fora_da_tabela_com_efeito_real`: `Ran 1 test`, `OK (skipped=25)`. São 27 formas, 25 puladas (21 com `-a` e 4 de família uutils, ausente), 2 vivas (os controles `seg A2 A6` e `seg A2 A7`), igual ao mínimo de 2. As decisões dos hooks (75 ou mais textos, todos código 2) rodaram integrais antes da sonda.
- Mutação X2 (QA, cópia em `$TMPDIR`): trocar `return r.returncode == 0` por `return True` em `env_aceita_argv0`, no mesmo `PATH`: `FAILED (failures=22, skipped=4)`, `AssertionError: 2 not greater than or equal to 20`. A sonda não é decorativa.
- Vermelho antes do verde: o teste da base do delta (2c14a56) no mesmo `PATH`: `FAILED (failures=22, skipped=4)` (o defeito do runner); no head, verde.

## Mutação (saída de `CI=true bin/forge-mutante tests/mutantes/hooks-corpus-rapido.json`, rc=0)
```
forge-mutante: pedido=hooks-corpus-rapido rev=1ead0ed775d7 spec=bab279f96f5ad87521a2d3346e6e8719c0dd35f70b21414502b8035264200b76
M1 · morreu · bin/forge-testes:97
M2 · morreu · bin/forge-testes:101
M3 · morreu · bin/forge-testes:106
M4 · morreu · bin/forge-testes:107
M5 · morreu · bin/forge-testes:74
M6 · morreu · tests/apoio_volta_unica.py:343
```
Conferência da lista contra o diff: o diff do `bin/forge-testes` contra 363ceee não mudou no delta (`VOLTA_UNICA` em hooks/doutor.py, hooks/, stacks/, .claude-plugin/ e FORGE_CHECK, e a entrada `test_doutor_relogio`, esta coberta pelo X1 do parecer anterior). Linha de guarda sem mutante: nenhuma.

## Textos decididos (corpus não encolheu)
`BaseVoltaUnica.DECIDIDOS`, medido por execução dos três módulos no head (43 testes, OK): test_lancador_fora_da_tabela_com_efeito_real 79; test_propriedade_da_reavaliacao_com_marcador 7152; test_propriedade_do_alfabeto_de_escapes_com_marcador 936; test_propriedade_do_alfabeto_de_opcoes_do_lancador 1782; test_propriedade_do_lancador_que_divide_texto_com_marcador 2268; test_t9b_oraculo_do_gatilho 3576. Idênticos aos de 363ceee (parecer anterior, por conteúdo). O número de textos decididos não depende do `env` (as decisões rodam antes da sonda).

## PA-7
`docs/engineering/achados-recorrentes.md` sem achado registrado: nada a conferir.

## Notas
- A prova de 20 formas vivas fica fora do CI até o cartão CI-ENV-ARGV0 (decisão do dono "C"); não é achado.
- Ambiental e igual com e sem o diff: o `test_forge` falha 4 testes em cópia sem `.git` e sem rede (parecer anterior).
