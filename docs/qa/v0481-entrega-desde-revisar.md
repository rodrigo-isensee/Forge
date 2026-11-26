---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-entrega-desde-revisar
commit: 3b5fde5f4ebfeb4a70792575d7ea6506d530134f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 entrega-desde-revisar (#904, volta E16.6, classe C, delta c056f38d..3b5fde5f)

Escopo: só o que o delta mudou no domínio do QA (`forge-check parecer delta`): `desde_do_parecer_aprovado` em `bin/forge-check`, `CicloDo878` (6 testes novos, 18 no total), specs ED1, ED6 e ED7, fragmento do changelog. O que veio da develop não se relê.

- ci: 3b5fde5f4ebfeb4a70792575d7ea6506d530134f verde

CI no head exato (`gh pr checks 904`, `headRefOid` conferido): verdes `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, as 10 partes da suíte (3.12 e 3.14), `teto de pulados` (2), `árvore já provada na develop`. Vermelhos fora da conta: `bateria (pareceres)`, `bateria` (agregado) e `catraca`, que esperam os pareceres e o rótulo.

## Achados da rodada anterior
- QA c056f38d: aprovado, sem achados.
- Review A1 (bloqueante, S1): corrigido. A guarda antiga (`any(parecer != aprovado)` só no head) saiu; agora os portões com X selado têm de ser exatamente os dos pareceres do head e `veredito_trocado` roda desde o Base-sha em todas as pastas de portão. O reprovado apagado, `_*.md` ou `contrato: 0` segue contando e devolve o Desde de sempre.
- Review A2 (recomendado, ED1 morria por exceção): atendido; o ED1 tem agora o teste `test_sem_conferida_pela_entrega_o_intervalo_parte_do_base_sha`, que afirma `intervalo: <Base-sha>..` pela `entrega --pedido`.
- Segurança A1 (S2 a S4): cobertos pelos testes `reprovado_apagado`, `reprovado_renomeado_para_sublinhado`, `reprovado_com_contrato_zero` e `reprovado_sem_brief_selado_apagado`.

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Reprovado sobre X apagado depois não libera o Desde (S1/S2) | `test_reprovado_apagado_depois_...` | parecer fora do head | passou |
| Renomeado para `_x.md` (S3) | `test_reprovado_renomeado_para_sublinhado_...` | arquivo ignorado | passou |
| `contrato: 0` (S4) | `test_reprovado_com_contrato_zero_...` | contrato inválido | passou |
| Reprovado de portão sem brief selado, apagado | `test_reprovado_sem_brief_selado_apagado_...` | portão fora do conjunto selado | passou |
| Portão com X selado sem parecer no head | `test_portao_selado_sem_parecer_...` | conjunto selado = conjunto do head | passou |
| Sem conferida, intervalo parte do Base-sha | `test_sem_conferida_pela_entrega_o_intervalo_parte_do_base_sha` | conferida vazia | passou |
| Os 12 do ciclo anterior | `CicloDo878` | ver parecer c056f38d | passou |

## Execução
- `python3 -m unittest tests.test_selo_e_entrega.CicloDo878`: Ran 18 tests, OK (89,7 s).
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-entrega-desde-revisar.json tests/mutantes/v0481-entrega-desde-revisar-2.json --processos 3`, saída 0, ED1 a ED12 todos `morreu` (ED1 em bin/forge-check:2732, ED7 em :2744, ED6 em :2746 incluídos). Nenhum sobrevivente.
- `bin/forge-mutante --cobertura --base 34ab6714cbc13e41c35907b13cb3a6b2b71d9688`: toda linha de guarda coberta (ED1 a ED12); só `tests/pesos-d4.json` sai `não coberto`, dado sem guarda.
- Vermelho: `bin/forge-testes --vermelho 34ab6714cbc13e41c35907b13cb3a6b2b71d9688 --modulos test_selo_e_entrega`, rc=0:
  `vermelho: base=34ab6714cbc1 head=3b5fde5f4ebf módulos=test_selo_e_entrega (restrito por --modulos)`; `contagem: não prova (passa na base)=186; prova (API ausente)=7; prova (asserção)=1`. Dos 6 testes novos, nenhum prova pela base: são guardas negativas (a base já devolve o Desde de sempre), e a prova deles é a morte dos mutantes ED1, ED6 e ED7 acima. Nenhum teste cai no HEAD.

## Parecer
Aprovado no 3b5fde5f. A correção fecha o furo do reprovado que sai do head e cada guarda trocada tem teste e mutante que morrem; nada afrouxa além do que a segurança já escreveu (opção A).
