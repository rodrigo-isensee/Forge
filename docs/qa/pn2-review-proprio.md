---
tipo: qa
contrato: 1
pedido: pn2-review-proprio
branch: melhoria/pn2-review-proprio
commit: 8e7abd9e65ef4b5272ec4b19be2c04523b796955
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: pn2-review-proprio

Diff conferido contra o escopo do pedido (E1 a E2): `bin/forge-check` (`aviso_de_review_proprio`, chamada por `avaliar_brief`), `tests/test_etapa_do_brief.py`, `tests/mutantes/pn2-review-proprio.json`, fragmento do changelog. Sem gatilho de segurança (só acrescenta linha de aviso, rc inalterado); sem teste de abuso.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: branch nova, pedido sem etapa de review: aviso, rc inalterado | ReviewProprio.test_branch_nova_sem_etapa_de_review_avisa_e_o_rc_nao_muda | sem rede (ls-remote falha): nada; rc 0 nos dois casos | passou (vermelho na base) |
| E1: pedido com `(tech-lead): code review` não avisa; code review de outro papel avisa | ReviewProprio.test_pedido_com_etapa_de_code_review_nao_avisa | papel diferente | passou (vermelho na base) |
| E1: branch já em origin não avisa | ReviewProprio.test_branch_ja_no_remoto_nao_avisa | branch existente | passou (guarda por M4) |
| E1: brief sem `Branch:` não avisa | ReviewProprio.test_brief_sem_branch_nao_avisa | cabeçalho sem Branch | passou (guarda por M1) |

## Cenários e resultado real
- `python3 -m unittest tests.test_etapa_do_brief` em 8e7abd9: 63 testes, OK. Os demais módulos que chamam `brief` (erros_no_brief, agentes_hash_brief, pedido_fora, mensagem_conferente, brief_gravar, voltas, volta_por_delta, citacao, isencoes, estado_da_branch, guarda_conferente): 210 testes, OK.
- Mutantes (`bin/forge-mutante tests/mutantes/pn2-review-proprio.json`): M1 a M7 morreram, rc=0. Conferência contra o diff: as condições novas (`if not branch`, `papel == "tech-lead" and ...`, `not conferido or remota`) têm mutante; `--cobertura --base 042e5d8` lista as três como cobertas (M1; M2 e M7; M3 e M4), rc=0; M5 cobre o sinal de não reprovar e M6 a chamada em `avaliar_brief`. Sem linha de guarda sem mutante.
- Vermelho (`bin/forge-testes --vermelho 042e5d8f73fc659615a4313c7213a661dfc32ce0 --modulos test_etapa_do_brief`): `vermelho: base=042e5d8f73fc head=8e7abd9e65ef`, revertidos à base `bin/forge-check` e o fragmento; 2 testes provam (asserção) na base, 61 não provam, rc=0. Os dois testes negativos (branch no remoto; sem Branch) passam na base por natureza (ausência de aviso) e são guardados pelos mutantes M4 e M1.
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0.
- PA-7 conferido: nenhuma classe de AR-1 a AR-10 se repete (lista de mutantes completa, sem `python` sem -I novo, sem hook tocado).
