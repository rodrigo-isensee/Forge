---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-teste-carga
commit: 171232b97fb8f5a84b426b2fabc5f2a5f1ef5170
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 · E5.2 (testes de tempo pela carga)

Branch: melhoria/v047-teste-carga. Head revisado: 3da64e12. Sem PR e sem check-run `bateria` ainda (máquina com carga 12 a 17 em 12 CPUs); rodei só os testes afetados e leves.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fator = min(2, max(1, carga/núcleos)) | `test_fator_segue_a_carga_por_nucleo_entre_1_e_2` (0.2, 4, 6/4, 8/4 e 400/4) | piso 1, teto 2, carga igual a núcleos | passou; mortos M-piso, M-teto, M-por-núcleo, M-min/max |
| Leitura da carga que falha dá 1 | `test_carga_ilegivel_deixa_o_limite_de_sempre` | OSError | passou; morto M-retorno e M-exceção |
| Limite do corpus escala, teto 2x ainda pega regressão | `test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha` | 0.5, 12/8, 999/8 | passou; 4 mutantes do spec mortos |
| Prazo do gh pendurado escala e o defeito (`sleep 30`) continua barrado | `Hooks.test_rotulo_so_dono_gh_pendurado_...` | teto 9 s x 2 = 18 s < 30 s | passou em 5,9 s; mutante `* 0` morto |
| Leitura de 1 min e núcleos padrão | nenhum | n/a | SEM TESTE (A1, A2) |

Teto de 2x: o corpus tem limite de 90 s por trabalhador, o máximo é 180 s; o gh vai a 18 s contra os 30 s do `sleep 30`. Regressão acima do dobro falha em qualquer carga. Ressalva: o fio `limite_de_cpu_do_corpus_sob_carga()` em `test_corpus_nos_dois_hooks` não tem teste próprio (o corpus leva uns 270 s); lido por revisão, correto.

## Vermelho antes do verde
```
vermelho: base=9b2c6474cc1e head=ddc19d86616b módulos=test_medida_cpu (restrito por --modulos)
revertidos à base: changelog.d/v047-teste-carga.md, tests/apoio_volta_unica.py
tests.test_medida_cpu.LimitesPelaCargaDaMaquina.test_carga_ilegivel_deixa_o_limite_de_sempre · H=ok · B=erro · prova (API ausente)
tests.test_medida_cpu.LimitesPelaCargaDaMaquina.test_fator_segue_a_carga_por_nucleo_entre_1_e_2 · H=ok · B=erro · prova (API ausente)
tests.test_medida_cpu.LimitesPelaCargaDaMaquina.test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha · H=ok · B=erro · prova (API ausente)
contagem: não prova (herdada da base)=5; prova (API ausente)=3
```
O head desse comando é ddc19d86 (3da64e12 mais o meu commit de spec, que só acrescenta `tests/mutantes/v047-teste-carga.json`). A execução sem `--modulos` estourou 500 s sob carga e não vale como vermelho.

## Mutantes da fórmula
`bin/forge-mutante` recusa mutar arquivo de teste (`arquivo de teste não se muta`), e `fator_de_carga` mora em `tests/test_hooks.py`. A spec `tests/mutantes/v047-teste-carga.json` traz só os 4 mutantes do `limite_de_cpu_do_corpus_sob_carga` (em `tests/apoio_volta_unica.py`):
```
forge-mutante: pedido=v047-teste-carga rev=ddc19d86616b
M1 · morreu · tests/apoio_volta_unica.py:55
M2 · morreu · tests/apoio_volta_unica.py:55
M3 · morreu · tests/apoio_volta_unica.py:55
M4 · morreu · tests/apoio_volta_unica.py:55
```
Os mutantes de `fator_de_carga` fiz à mão numa cópia, rodando `tests.test_medida_cpu` (árvore restaurada em seguida):

| Mutante | Resultado |
|---|---|
| TETO 2 -> 3 | morto (2 falhas) |
| `max(1.0, ...)` -> `max(0.5, ...)` | morto (2) |
| `carga / nucleos` -> `carga` | morto (3) |
| `except OSError: return 1.0` -> `return 2.0` | morto (1) |
| `min(` -> `max(` | morto (5) |
| `except OSError` -> `except ValueError` | morto (1) |
| `getloadavg()[0]` -> `[2]` | SOBREVIVEU (A1) |
| `nucleos or nucleos_do_processo() or 1` -> `nucleos or 1` | SOBREVIVEU (A2) |

## Cenários e resultado real
- `python3 -m unittest tests.test_medida_cpu`: 8 testes, OK.
- Teste do gh pendurado: OK em 5,9 s.
- Não rodei o corpus nem a suíte: sem PR e com a máquina sob carga; o CI do PR cobre.

## Revalidação por delta até 171232b9 (E5.15)
Head revisado: 171232b97fb8f5a84b426b2fabc5f2a5f1ef5170 (delta de 3da64e12: a fórmula foi para `tests/apoio_volta_unica.py`, testes novos em `tests/test_medida_cpu.py`, 14 mutantes na spec). Sem PR nem check-run `bateria`; só testes leves e afetados (carga ~8 em 12 CPUs). Parecer: APROVADO. Os A1 e A2 anteriores estão resolvidos; nenhum achado bloqueante novo.
Resolvidos: A1 (`test_le_a_carga_de_1_minuto_e_nao_a_de_15` mata M11) e A2 (`test_sem_nucleos_dados_usa_os_do_processo` mata M12) da rodada anterior.

## Achados
- A3 (recomendado) tests/apoio_volta_unica.py:30 · mutante manual `except OSError` -> `except ValueError` em `nucleos_do_processo` sobrevive em `test_medida_cpu`; código movido sem mudança de lógica, por isso não bloqueia. Teste com `os.sched_getaffinity` levantando OSError esperando `None` mata.
- A4 (recomendado) tests/apoio_volta_unica.py:30 · mutante manual `else os.cpu_count()` -> `else 1` (recuo sem afinidade) sobrevive; mesmo caso de A3, código herdado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fator = min(2, max(1, carga/núcleos)) | `test_fator_segue_a_carga_por_nucleo_entre_1_e_2` | piso 1, teto 2, carga = núcleos | passou; M5 a M7, M9 mortos |
| Carga ilegível dá 1 | `test_carga_ilegivel_deixa_o_limite_de_sempre` | OSError | passou; M8, M10 mortos |
| Lê a média de 1 min (A1) | `test_le_a_carga_de_1_minuto_e_nao_a_de_15` | índice 0 do `getloadavg` | passou; M11 morto |
| Carga dada vale mais que a lida | `test_carga_dada_vale_mais_que_a_lida` | `None` vs valor | passou; M13 morto |
| Núcleos do processo quando não dados (A2) | `test_sem_nucleos_dados_usa_os_do_processo` | `nucleos=None` | passou; M12 morto |
| Sem leitura de núcleos conta 1 | `test_sem_leitura_de_nucleos_conta_um` | `nucleos_do_processo()` = None | passou; `or 1` removido (manual): morto (erro) |
| Limite do corpus escala, teto 2x | `test_limite_do_corpus_escala_e_regressao_de_mais_do_dobro_ainda_falha` | 0,5, 12/8, 999/8 | passou; M1 a M4 mortos |
| Afinidade manda no pool | `PoolDosFixtures.test_pool_le_a_afinidade_e_ignora_o_forge_nproc` | `hasattr(sched_getaffinity)` | passou; M14 morto |
| gh pendurado escala, `sleep 30` barrado | `Hooks.test_rotulo_so_dono_gh_pendurado_...` | 18 s < 30 s | passou em 5,8 s |

## Vermelho antes do verde (rodada de 171232b9)
```
vermelho: base=9b2c6474cc1e head=171232b97fb8 módulos=test_medida_cpu (restrito por --modulos)
mantidos no HEAD: tests/mutantes/v047-teste-carga.json, tests/test_hooks.py, tests/test_hooks_volta_corpus.py, tests/test_medida_cpu.py
7 testes de LimitesPelaCargaDaMaquina · H=ok · B=erro · prova (API ausente)
5 testes de MedidaDeCpuDosTestesDeDesempenho · não prova (herdada da base)
contagem: não prova (herdada da base)=5; prova (API ausente)=7
```

## Mutantes (`bin/forge-mutante tests/mutantes/v047-teste-carga.json --processos 2`)
```
M1 a M4 · morreu · tests/apoio_volta_unica.py:79
M5 · morreu · :35   M6 · morreu · :47   M7 · morreu · :47   M8 · morreu · :44
M9 · morreu · :47   M10 · morreu · :44 (erro: o teste declarado dá erro sob o mutante e passa sem ele)
M11 · morreu · :43  M12 · morreu · :46  M13 · morreu · :43  M14 · morreu · :30
```
14 de 14 mortos, saída 0. Conferência contra o diff: `forge-mutante --cobertura --base 9b2c6474` lista as condições mudadas (L30, L43, L46) cobertas por M14, M13 e M12; as demais linhas da fórmula têm M5 a M11. Nenhuma linha de guarda sem mutante.

## Cenários e resultado real
- `python3 -m unittest tests.test_medida_cpu`: 12 testes, OK. `PoolDosFixtures`: 3 OK. Teste do gh pendurado: OK. Imports nas duas ordens (`test_hooks` e `apoio_volta_unica`): OK, o ciclo resolve.
- Não rodei o corpus nem a suíte; o CI do PR cobre.
