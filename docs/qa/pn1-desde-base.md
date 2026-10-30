---
tipo: qa
contrato: 1
pedido: pn1-desde-base
branch: melhoria/pn1-desde-base
commit: ee49b7ef07337f4abf940b5da94036fbba641028
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: pn1-desde-base

Escopo: `forge-check entrega` aceita o Base-sha do brief como Desde quando a branch nasce dele e a última `conferida` do Histórico não é ancestral do head (ou não há conferida); texto de `agents/conferente.md` (P-N1, `R-PROVA` sem afrouxar). Base-sha 99315cf, head ee49b7e.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: sem conferida, Base-sha vale como Desde (branch inteira) | DesdeNoBaseSha.test_sem_conferida_o_base_sha_vale_como_a_branch_inteira | Histórico sem conferida | passou |
| E1: branch nova depois de squash (última conferida fora do head) | DesdeNoBaseSha.test_conferida_de_branch_anterior_fora_do_head_aceita_o_base_sha | vale a última conferida; linha do dono não conta | passou |
| E1: conferida ancestral do head segue sendo o Desde; Base-sha recusado | DesdeNoBaseSha.test_com_conferida_no_historico_o_base_sha_segue_recusado | permissão (não afrouxa R-PROVA) | passou |
| E1: branch que não nasce do Base-sha segue recusada | DesdeNoBaseSha.test_branch_que_nao_nasce_do_base_sha_segue_recusada | Base-sha não ancestral do head | passou |
| E2: spec de mutantes M1 a M6 | forge-mutante | uma por linha de guarda | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_conferencia_base_dono tests.test_volta_por_delta tests.test_conf_escopo tests.test_mensagem_conferente` sobre ee49b7e: Ran 111 tests, OK, rc=0.
- `bin/forge-mutante tests/mutantes/pn1-desde-base.json`, rc=0: M1 a M6 morreram (M1 bin/forge-check:1076; M2, M3, M5 :839; M4 :840; M6 :838).
- `bin/forge-mutante --cobertura --base 99315cf`: linhas 838, 839 e 1076 cobertas (M6; M2-M5; M1), todas "declarado, não provado"; conferido contra o diff: as três linhas de guarda mudadas e a 840 (M4) têm mutante; sem guarda sem mutante, sem isenta.
- Vermelho antes do verde, `bin/forge-testes --vermelho 99315cf --modulos test_conferencia_base_dono --prazo 500`, rc=0: `vermelho: base=99315cf head=ee49b7e`, revertidos à base agents/conferente.md, bin/forge-check, changelog.d/pn1-desde-base.md. Prova (asserção): test_sem_conferida_o_base_sha_vale_como_a_branch_inteira e test_conferida_de_branch_anterior_fora_do_head_aceita_o_base_sha (H=ok, B=falha). Os outros dois da classe (recusas) passam na base por serem guarda contra afrouxamento; são provados pelos mutantes M3 e M4. Contagem: não prova=26, prova=2. A rodada sem `--modulos` estourou o prazo (rc=124, sem veredito, não vale como vermelho).
- Texto de `agents/conferente.md`: a exceção descreve `Desde:` igual ao Base-sha com a última conferida fora do head (`--is-ancestor` rc 1) e a linha `base: Base-sha do brief (sem conferida na branch)`, igual à saída do código.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).
