---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-avisos
commit: 4553163442c9ff33e3993de0bee982f924a16a5f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 (E1.163, lote do bin/forge-mutante)

Branch `melhoria/v047-mutante-avisos`, código testado no head 45531634 (o commit seguinte, fa06021d, só traz o parecer de segurança; trazido por fast-forward, sem rebase nem force). Sem especificação de UX: as obrigações são as três entregas do E1.140 (o fragmento `changelog.d/v047-mutante-avisos.md` as lista).

## Achados
- A1 (recomendado) tests/test_forge_mutante.py:1 · `forge-testes --vermelho` saiu 2 nas duas rodadas (módulo `test_forge` sem veredito); os 8 testes novos provam (B=falha, H=ok) e nenhum cai no HEAD. O autor deve colar um vermelho rc=0 (`R-QA`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `--conferir` acusa `de` que não aparece uma vez no arquivo da rev | `Conferir.test_de_no_lugar_sai_0_e_de_que_sumiu_depois_da_spec_sai_1_com_a_spec_e_o_trecho` | trecho 1 vez vs 0 vezes (spec igual, arquivo mudado) | passou; CF1-CF4 morreram |
| Arquivo vigiado que sumiu sai 1, sem cair | `Conferir.test_arquivo_vigiado_que_sumiu_sai_1_sem_cair` | arquivo ausente na rev | passou |
| `linha_base` da isenta confere na base | `Conferir.test_linha_base_que_bate_sai_0_e_a_deslocada_sai_1`, `test_isenta_em_arquivo_sem_parse_nao_bate` | linha certa, deslocada, arquivo sem parse | passou; CF5-CF8 morreram |
| Sem spec no diff sai 0; spec inválida ou base ilegível sai 2 | `Conferir.test_sem_spec_no_diff_sai_0_e_spec_invalida_ou_base_ilegivel_saem_2` | diff sem spec, spec vazia, base inexistente | passou |
| `--conferir` exige `--base` e recusa SPEC e `--cobertura` | `Conferir.test_conferir_exige_base_e_recusa_spec_e_cobertura` | 3 combinações inválidas | passou |
| Log só leitura vira aviso e o veredito fica | `Execucao.test_log_que_nao_se_grava_vira_aviso_e_o_veredito_fica` | `OSError` ao gravar o log; sem `Traceback` | passou; CF11-CF14 morreram |
| Controle vermelho diz qual teste está fora do commit | `Execucao.test_controle_vermelho_por_teste_fora_do_commit_diz_qual_teste_falta_commitar` (+ negativo no teste do controle vermelho existente) | módulo ausente, método ausente, teste presente | passou; CF15-CF19 morreram |

## Cenários e resultado real
- Diff `origin/develop..45531634`: `bin/forge-mutante` (+105/-10), `tests/test_forge_mutante.py` (+101), 3 specs de mutantes e o fragmento do changelog. Escopo bate com o E1.140.
- Linhas de guarda mudadas: todas têm mutante (`--cobertura` rc=0, 11 condições `coberta`, nenhuma sem mutante; as isentas não existem nas 3 specs).
- `--conferir` rodado sobre o próprio lote (`--base e60183d0`): `conferidas`, rc=0, ou seja, as 3 specs batem com o arquivo da rev.
- Mutantes: 19 de 19 morreram (3 specs, 8+8+3), rc=0, rev 45531634.
- Suíte inteira: o branch não tem PR, então não há check-run `bateria` do sha; a suíte roda no CI do PR. Rodei só os cenários do lote (vermelho e mutantes).
- Sem bug novo; sem classe repetida (nenhuma linha `AR-<n>` nova).

## Provas
```
vermelho: base=e60183d0a41d head=4553163442c9 módulos=test_changelog,test_forge,test_forge_mutante
revertidos à base: bin/forge-mutante, changelog.d/v047-mutante-avisos.md
mantidos no HEAD: tests/mutantes/v047-mutante-avisos-2.json, tests/mutantes/v047-mutante-avisos-3.json, tests/mutantes/v047-mutante-avisos.json, tests/test_forge_mutante.py
test_forge · sem veredito (prazo, sinal ou executor sem registro em H,B)
Conferir.* (6 testes) e Execucao.test_controle_vermelho_por_teste_fora_do_commit... e Execucao.test_log_que_nao_se_grava... · H=ok · B=falha · prova (asserção)
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.
rc=2
```
```
forge-mutante: pedido=v047 rev=4553163442c9 (3 specs)
CF1 a CF19 · morreu (19 linhas, todas "morreu")
rc=0
```
