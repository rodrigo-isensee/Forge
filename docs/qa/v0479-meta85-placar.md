---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-placar
commit: 87aff761c47ae4aa8bcf2b81c7565c71888cbcbc
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 (E36.4), forge-placar `fases`: meta de 42 min, mediana, p75, corte por hora e horas paradas

Escopo: só o que a branch acrescenta à `melhoria/v0479-placar-fases` (42c2a906, aprovada): `bin/forge-placar`, `tests/evals/test_placar.py`, mutantes `tests/mutantes/v0479-meta85-placar{,-2,-3,-4}.json` e os três `v0479-placar-fases-{2,3,4}.json` reescritos, texto de `docs/melhoria-continua.md` e o fragmento de changelog. Sem suíte local (é do CI do PR, `R-QA`).

## Achados
- A1 (bloqueante) bin/forge-placar:664 · Histórico sem nenhuma linha `PARADA <tipo>` devolve 0 em vez de `-`: a sonda deu `horas paradas, sessão: 0 h 00 min` e `promoção: 0 h 00 min` com "Sessão caiu" no histórico. Fere "sem a fonte, `-`". Sem linha do tipo, devolva None; falta teste e mutante desse ramo.

## Critério → teste → resultado
Obrigações lidas do cabeçalho de `bin/forge-placar`, do fragmento de changelog e da ordem do dono (19/11 14:52, meta 42 min).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Meta 42 min no json e no texto | `test_fases_e_primeira_rodada...`, `test_texto_traz_a_meta...` | n/a | passou |
| Média, mediana e p75 inclusivo | `test_media_mediana_e_p75` | dia sem item (None), um item só, três itens | passou |
| PR e hora do merge no `--json` | `test_pr_e_hora_do_merge_no_json` | merge sem PR (None) e squash | passou |
| Corte `[desde, ate)` por hora do merge, fuso opcional | `test_corte_por_hora_do_merge` | limite exclusivo, só `--desde`, só `--ate`, sem fuso (TZ) | passou |
| Corte inválido sai 2 | `test_corte_invalido_sai_com_2` | ate igual e antes de desde, data inexistente | passou |
| Parada de sessão e promoção pelo histórico, união sem dupla contagem, recorte na janela | `test_horas_paradas_de_sessao_e_promocao_pelo_historico` | sobreposição, intervalo contido, virada de dia | passou |
| Parada sem fonte sai `-` | `test_sem_historico_as_paradas_saem_tracinho...` | sem `docs/pedidos` | passou |
| Parada sem fonte sai `-` (histórico sem linha PARADA) | nenhum | histórico sem o tipo | **sem teste, e o código falha (A1)** |
| Develop vermelha pelo CI | `test_horas_paradas_da_develop_vermelha_pelo_ci`, `test_develop_ainda_vermelha_conta_ate_agora` | cancelado, em andamento, sem updatedAt, vermelha em curso | passou |
| `--ci` ilegível ou ausente sai 2 | `test_ci_ilegivel_sai_com_2` | quatro formatos ruins e arquivo ausente | passou |

## Cenários e resultado real
- `PYTHONPATH=. python3 -m unittest tests.evals.test_placar` no head: `Ran 47 tests ... OK`.
- Sonda: raiz com `docs/pedidos/p.md` cujo histórico só tem "Sessão caiu" e `fases --dia 2025-03-18 --raiz <raiz>`: `horas paradas, sessão: 0 h 00 min` (esperado `-`). Mesmo resultado do review (S1).

## Vermelho antes do verde
`forge-testes --vermelho 42c2a906 --modulos test_placar` sai 2 (`módulo sem arquivo em tests/: test_placar`; o teste mora em `tests/evals/`, e `evals.test_placar` não passa no padrão de `--modulos`); sem `--modulos` ele escolheu a suíte inteira e não devolveu veredito. Prova manual, em cópia em `$TMPDIR`: HEAD com só `bin/forge-placar` da base 42c2a906.
```
PYTHONPATH=. python3 -m unittest tests.evals.test_placar   (base)
ERROR: test_horas_paradas_da_develop_vermelha_pelo_ci, test_horas_paradas_de_sessao_e_promocao_pelo_historico,
       test_media_mediana_e_p75, test_pr_e_hora_do_merge_no_json, test_sem_historico_as_paradas_saem_tracinho_e_data_invalida_sai_com_2
FAIL:  test_ci_ilegivel_sai_com_2, test_corte_invalido_sai_com_2, test_corte_por_hora_do_merge,
       test_develop_ainda_vermelha_conta_ate_agora, test_fases_e_primeira_rodada_por_item_e_total_do_dia, test_texto_traz_a_meta_e_a_primeira_rodada
Ran 47 tests ... FAILED (failures=6, errors=5)      (HEAD: Ran 47 tests ... OK)
```
Onze testes caem na base e nenhum cai no HEAD.

## Mutação
`bin/forge-mutante --processos 2 tests/mutantes/v0479-meta85-placar{,-2,-3,-4}.json` (rev 87aff761c47a): rc=0, M1 a M28 todos `morreu`, nenhum sobrevivente. As specs reescritas `bin/forge-mutante --processos 2 tests/mutantes/v0479-placar-fases{,-2,-3,-4}.json`: rc=0, 31 `morreu`. `bin/forge-mutante --cobertura --base 42c2a906`: toda condição nova de `bin/forge-placar` com mutante `coberta ... declarado, não provado`; as três linhas `sem mutante` são de `tests/evals/test_placar.py`, não de guarda. Falta o mutante do ramo de A1.

## Parecer
Reprovado por A1, defeito provado e de correção pequena (agente da stack: `python-developer`/autor). O resto cumpre os critérios e tem teste e mutante. Pareceres de review e segurança do mesmo head já na branch (trazidos por merge).
