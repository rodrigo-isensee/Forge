---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-proximo-por-etapa
commit: 7d675afaa992f35ac6030fbf232c2b8fcc77b47a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 proximo por etapa (E2.121)

Código testado: `7d675afa`; o head local `e0e63bed` só soma o parecer de segurança (E2.120), sem código. Pedido de controle sem especificação de UX: as obrigações são as regras nomeadas no código e no changelog (PROXIMO-POR-ETAPA, PROXIMO-BRANCH-PR-MESCLADO, FORGE-CHECK-PROXIMO-LENTO). Sem PR aberto, não há check-run `bateria` para citar; rodei os testes do item localmente.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PROXIMO-POR-ETAPA: sem `--etapa`, só as abertas, contagem das fechadas | `Proximo.test_etapa_entregue_branch_e_ultimo_veredito_aprovado`, `ProximoPorEtapa.test_todas_entregues_nao_vira_pedido_sem_etapas` | todas entregues (lista vazia) vs pedido sem `## Etapas` | passou |
| PROXIMO-POR-ETAPA: `--etapa` mostra só ela, entregue ou não | `ProximoPorEtapa.test_etapa_mostra_so_ela_entregue_ou_nao` | n/a | passou |
| PROXIMO-POR-ETAPA: forma inválida ou fora do pedido, rc 2 | `ProximoPorEtapa.test_etapa_fora_da_forma_ou_do_pedido_rc_2` | `E1`, `;rm`, minúscula, 4 dígitos, id inexistente | passou |
| PROXIMO-POR-ETAPA: teto de linhas corta a lista, não o passo | `Proximo.test_teto_de_linhas_e_pedido_inexistente` | 59 etapas, teto 40 | passou |
| PROXIMO-BRANCH-PR-MESCLADO: merge ou parecer na develop = feita | `ProximoBranchMesclada.test_merge_commit_e_parecer_na_develop_poem_a_etapa_como_feita` | parecer só na branch não conta | passou |
| idem: nome parecido não conta; entregue segue entregue | `ProximoBranchMesclada.test_nome_parecido_nao_conta_e_entregue_segue_entregue` | prefixo `um`/`um-dois` | passou |
| idem: sem develop não quebra | `ProximoBranchMesclada.test_sem_develop_nada_sai_feito_e_nao_quebra` | develop ausente | passou |
| FORGE-CHECK-PROXIMO-LENTO: git por branch, não por par | `ProximoRapido.test_git_por_branch_nao_por_par_de_selo_e_conferida` | 30 selos x 10 conferidas, menos de 40 chamadas | passou |
| idem: selo de branch sem ref não entrega nem quebra | `ProximoRapido.test_selo_de_branch_sem_ref_nao_entrega_e_nao_quebra` | ref sumida | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_proximo` no head: 23 testes, OK (32 s).
- Vermelho antes do verde: `bin/forge-testes --vermelho bf475209 --modulos test_proximo --prazo 400` saiu rc=0. Abertura: `vermelho: base=bf475209bae4 head=e0e63bed0779 módulos=test_proximo (restrito por --modulos)`; `revertidos à base: bin/forge-check, changelog.d/v047-proximo-por-etapa.md, docs/security/v047-proximo-por-etapa.md`; `contagem: não prova (passa na base)=13; prova (asserção)=10`. Os 13 que passam na base são os herdados e os de guarda (`ProximoDoItem` inteira e `test_selo_de_branch_sem_ref...`); nenhum cai no HEAD.
- Mutação: `bin/forge-mutante` nas 3 specs (20 mutantes, PE-M1 a PE-M20), `--processos 3`, rc=0, os 20 `morreu` (primeira linha `pedido=v047 rev=e0e63bed0779`).
- Cobertura: `bin/forge-mutante --cobertura --base bf475209` rc=0, `base=bf475209bae4... mb=bf475209bae4...`; todas as condições mudadas `coberta`, uma `isenta` (índice por termo em `bin/forge-check:6923(base)`, com motivo que cita os testes que a provam).
- Achados recorrentes (PA-7): AR-1 (lista de mutantes incompleta) conferido, sem sobra; AR-2 (ramo de falha sem teste) coberto por rc 2 e develop ausente; demais AR são de review ou segurança e não tocam estes arquivos.
