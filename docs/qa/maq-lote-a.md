---
tipo: qa
contrato: 1
pedido: maq-lote-a
branch: melhoria/maq-lote-a
commit: 8e8acf0a457d7b1a3810fcaa6cbad873b99751e1
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: maq-lote-a

Lote A da máquina: C5 (pesos regravados e teste de cobertura dos pesos), A3 (push de código em segundo plano) e A4 (V2 do autor dirigida, 1 processo, pela fila). Sem especificação de UX nem contrato de API; as obrigações são E1 a E3 do pedido `MAQ-LOTE-A`. Sem gatilho de segurança neste parecer. Suíte completa não rodada (só roda no pre-push, por decisão ACELERA-RODADA); rodei só os testes do lote, em cópia de `git archive` do head em `$TMPDIR/qa-engineer-maq-lote-a/`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (pesos regravados) | simulação da divisão (CT-01) | nenhum módulo fora; processo mais cheio cai | passou |
| E1 (aviso de mais de 20% sem peso) | `PesosDaSuite.test_no_maximo_20_por_cento_dos_modulos_sem_peso` | limite de 20%: 12 sem peso passa, 13 falha | passou |
| E2 (push em segundo plano) | `EsperaDoPushEVerificadores.test_push_de_codigo_em_segundo_plano` | cada uma das 2 frases | passou |
| E3 (V2 dirigida e na fila) | `EsperaDoPushEVerificadores.test_v2_dirigida_e_na_fila` | cada uma das 2 frases | passou |

## Cenários e resultado real
- CT-01 divisão com os pesos novos (`scripts/suite-paralela.py`: `ler_pesos`, `repartir`, lista `tests/test*.py`, 64 módulos; pesos novos 64 de 64, antigos 29):
  - `sorted(módulos da partição) == sorted(módulos)` para 2, 3 e 4 processos, com pesos antigos e novos: nenhum fora, nenhum repetido.
  - Soma do processo mais cheio, medida com os pesos novos (a melhor estimativa do real): 2 proc. 377,2 → 357,6 s; 3 proc. 276,8 → 238,5 s; 4 proc. 214,7 → 179,0 s (queda de 5%, 14% e 17%). Partes equilibradas (4 proc.: 179,0 / 179,0 / 178,4 / 178,6).
- CT-02 tirar peso (cópia, `tests/pesos-d4.json`): tirar 1 passa (1 de 64, abaixo de 20%); 12 passa (12*5=60 ≤ 64); 13 falha ("65 not less than or equal to 64 : 13 de 64 módulos sem peso"). Com os pesos antigos da base (29 de 64): falha ("35 de 64 módulos sem peso"). O teste morre no limite certo e prova o vermelho antes do verde da C5.
- CT-03 tirar cada frase nova de `agents/tech-lead.md` (cópia, substituída por `XX`): as 4 frases, uma por vez, derrubam o teste dela (`test_push_de_codigo_em_segundo_plano` nas 2 primeiras, `test_v2_dirigida_e_na_fila` nas 2 últimas); restaurado, 3 testes OK.
- CT-04 os 3 testes novos passam no head (`Ran 3 tests ... OK`). Na base não existem (classes novas), logo vermelho por ausência.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens (`nenhum ainda`), nada a conferir.
- Mutação: não se aplica (`bin/`, `hooks/`, `.githooks/` e `tests/catraca.py` não mudaram; sem `tests/mutantes/maq-lote-a.json`).

## Observações (sem devolver)
- O teste dos pesos olha só a presença da chave; peso obsoleto ou 0,0 passa. Cobre o que o pedido pediu (E1).
- O "brief-padrão" e o "brief da V2" citados em A3 e A4 não estão neste repositório; o diff cobre o `agents/tech-lead.md`, que é o texto do repositório, e E2 e E3 do pedido pedem só isso aqui.
