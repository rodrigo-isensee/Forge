---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 3ed7a573dc9999ff05f8cc9c485603286c72fc59
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E174.2 / E174.31, rastreio do critério à prova, PR #868), delta

Base aabc476c, head 3ed7a573; delta desde 64c4dd9b (parecer anterior, reprovado por A1). Mudança no domínio do QA: `provas_por_criterio` passa a ler o brief por `briefs_selados` (sha256 do selo confere), skill movida para `skills/produto-criterios/rastreio.md`, teste novo `test_brief_alterado_depois_do_selo_nao_prova`, `test_linha_id_do_pedido_da_o_nome_da_tabela` com `assertEqual` na lista inteira, mutantes D73 e D74 reescritos.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `C-n` com `PQ cobre:` de brief com entrega conferida sai entregue; sem prova, não entregue (rc 1) | `test_criterio_com_prova_conferida_entregue_e_sem_prova_nao_entregue` | selo repetido não duplica | passou; vermelho na base (asserção) |
| Todos entregues: rc 0 | `test_todos_entregues_sai_com_rc_zero` | `cobre: C-1, C-2` | passou; vermelho na base |
| Brief sem `entrega conferida` não prova | `test_brief_sem_entrega_conferida_nao_prova` | 0 entregues | passou; vermelho na base |
| Brief alterado depois do selo não prova (novo) | `test_brief_alterado_depois_do_selo_nao_prova` | sha256 diferente do selo | passou; vermelho na base; D73 morreu |
| `cobre:` fora do pedido reprova | `test_cobre_de_criterio_fora_do_pedido_reprova_mesmo_com_todos_entregues` | C-9 inexistente | passou; vermelho na base |
| Id repetido reprova, vale o primeiro | `test_id_repetido_reprova_e_vale_o_primeiro` | duplicata | passou; vermelho na base |
| Linha `id:` dá o nome da tabela | `test_linha_id_do_pedido_da_o_nome_da_tabela` | id diferente do nome do arquivo | passou; vermelho na base (asserção; A1 anterior resolvido) |
| Pedido sem `C-n` ou ilegível: rc 2 | `test_pedido_sem_criterio_c_n_ou_ilegivel_sai_nao_verificavel` | sem item; inexistente | passou; vermelho na base |

## Vermelho antes do verde
`bin/forge-testes --vermelho aabc476c5dbad3b3efced688e578bb5c71c5f722 --modulos test_criterios`, rc 0:
```
vermelho: base=aabc476c5dba head=3ed7a573dc99 módulos=test_criterios (restrito por --modulos)
(8 testes) H=ok · B=falha · prova (asserção)
contagem: prova (asserção)=8
```

## Mutação
`bin/forge-mutante --base 64c4dd9ba9c4b3484431167e1b7a42adc7b80ec5` nas 3 specs (`--processos 3`), rc 0: `base=64c4dd9ba9c4... rev=3ed7a573dc99`; D71 a D717 todos `morreu`, nenhum sobrevivente. `--cobertura --base aabc476c`: toda condição mudada em `bin/forge-check` está `coberta`; só `tests/pesos-d4.json` sai `não coberto` (dado, sem decisão).

## Métricas de texto
`test_metricas_texto` (2 testes) OK local no head: o achado A1 do review (skill acima do teto) está resolvido.

## CI
Check-run `bateria` do head 3ed7a573 ainda em andamento na minha leitura (run 45490715138); a suíte inteira vale por ele, não rerrodada aqui. `Catraca` (run 45490715036) vermelha neste sha: `python3 tests/catraca.py --modo regras --base origin/develop` reproduz `R-CONFORMIDADE: mudança em bin/forge-check ... só passa com o rótulo afrouxa-regra do dono, aplicado depois do último push`. É o portão de governança do ADR 0008, não defeito de código: depende do rótulo do dono após o último push.
