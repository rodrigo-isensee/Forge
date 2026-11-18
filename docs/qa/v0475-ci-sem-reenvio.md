---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-sem-reenvio
commit: 6cbb20bc801d3b0014ce62f97cdc8b20221edfd4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0474 E3.43 (CI sem reenvio, R-CUSTO)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3.43: agentes que enviam (tech-lead, devops, qa, 3 de stack) trazem a linha `**CI pago**` com as partes da regra | `test_agentes_que_enviam_trazem_a_regra` (6 subtestes) | exatamente 1 âncora por arquivo; ID R-CUSTO exceto qa-engineer (teto do orçamento) | passou |
| Detalhe em `ritmo-e-corte.md` | `test_detalhe_no_ritmo_e_corte` | seção `## CI pago` presente; 7 partes | passou |
| Skill de envio aponta o detalhe | `test_skill_de_envio_manda_ler_o_detalhe` | ponteiro + R-CUSTO | passou |
| CI vermelho no brief de volta, sem rerun | `test_ci_vermelho_vai_no_brief_de_volta_sem_rerun` | exatamente 1 parágrafo | passou |
| Lista de stacks é a das que enviam | `test_stacks_listadas_sao_as_que_enviam` | `Antes do push` presente | passou |
| Texto encurtado não estoura o orçamento nem as métricas | `test_orcamento_instrucao` (8), `test_metricas_texto` (2) | tetos de `docs/regras/orcamento.json` | passou |
| Módulo novo entra no plano dirigido | `test_testes_tocados` (162, 1 skip pré-existente) | varredura de pasta | passou |

## Cenários e resultado real
- Diff lido contra o pedido: só texto (agentes, skills, 3 stacks, fragmento de changelog) e o teste; sem código de controle, então não há `forge-mutante` nem guarda a minutar. Sem gatilho de segurança.
- Vermelho antes do verde, feito em cópia da base (`git archive 2fa505d7` mais o teste novo, `python3 -I -m unittest`): `Ran 5 tests ... FAILED (failures=9)` (6 agentes, volta, detalhe, skill de envio). No head: `Ran 5 tests ... OK`. O `forge-testes --vermelho 2fa505d7` ficou sem veredito (timeout do sandbox, fila R-TETO ocupada por outra sessão); a prova acima é a manual, equivalente na base.
- `forge-check docs` sem erro. Texto encurtado nos agentes (frases de apoio) não removeu o que é cobrado por invariantes: `test_orcamento_instrucao` e `test_metricas_texto` verdes.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), não rodada aqui.
- Nota: o remoto da branch estava em 88626f51, diferente do head local 6cbb20bc; revisado o head do brief.
