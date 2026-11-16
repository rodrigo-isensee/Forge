---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-554-revalidacao
commit: 7b3604a19b06273ea09e2692c8474b6d6cb4dc18
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: melhorias-de-projeto-1311 (pré-envio da fábrica, E1.55; revalidação E1.63)

Revalidação por delta 48bf85e8..7b3604a1 (já na develop, c5c3a449). No domínio do QA o que mudou foi só a renumeração do M10 para M13 em `tests/mutantes/mp1311-pre-envio-fabrica-2.json` (6035e27c) e o merge da develop, cujo conflito em `tests/test_testes_tocados.py` ficou na contagem do mapa (82 módulos, com `test_hook_erro_libera`) e no teste novo do E1.120, alheio ao #554. A1 e A2 seguem como no parecer anterior (recomendados, sem bloqueio). A3 resolvido: as duas specs juntas saem rc=0.

Suíte inteira: o PR 562 (head f2ceda8e, merge c5c3a449 = develop atual, que contém 7b3604a1) tem todas as suítes 3.12 e 3.14 (partes 1 a 3), teto de pulados, `bateria` e `catraca` verdes. O run 43619396917 do PR 554 teve a parte 3/3 vermelha (log inacessível daqui, sandbox); a mesma árvore passa no 562, então não bloqueia. Nada de produto mudou além do merge.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Caso código: catraca, texto e afetados | Gerar.test_codigo_traz_descricao_texto_e_testes_afetados | bin/ e tests/ | passou; prova (asserção) |
| Só texto sem afetados | Gerar.test_so_texto_fica_sem_os_testes_afetados | só docs/ | passou; prova |
| Junção (`pr`) sem afetados | Gerar.test_juncao_fica_sem_os_testes_afetados | etapa pr | passou; prova |
| Fora do Forge não cobra | Gerar.test_fora_do_forge_nao_cobra_o_pre_envio_da_fabrica | não-Forge | passou; só guarda |
| Parecer sem pré-envio do autor | Gerar.test_parecer_nao_leva_o_pre_envio_do_autor | etapa review | passou; só guarda |
| Parecer com PR: CI do head | Gerar.test_parecer_com_pr_so_aprova_com_o_ci_do_head_verde | PR aberto | passou; prova |
| Parecer sem PR | Gerar.test_parecer_sem_pr_diz_que_a_suite_fica_para_o_ci | pr == {} | passou; prova |
| Parecer sem gh | Gerar.test_parecer_sem_gh_mantem_a_regra | pr None | passou; prova |
| Lista do brief = lista do `--texto` | Texto.test_a_lista_do_brief_e_a_do_modo_de_texto | duas listas | passou; prova (API ausente) |
| `--texto`: um comando, rc e resumo | Texto.test_roda_os_testes_de_texto_num_comando_so_com_rc_e_resumo | rc, 1 linha | passou; prova (asserção) |
| `--texto` não combina | Texto.test_texto_nao_combina_com_outra_opcao | 8 opções, mensagem da guarda | passou; prova |

## Cenários e resultado real
- `python3 -m unittest -q tests.test_pre_envio_brief`: 11 testes, OK.
- `forge-testes --vermelho befd4cca --modulos test_pre_envio_brief`: base=befd4ccaa75e head=48bf85e84376; contagem: não prova (passa na base)=2; prova (API ausente)=1; prova (asserção)=8; rc=0.
- `forge-mutante` spec 1: M1 a M7 e M10 morreram, rc=0; spec 2: M8 a M12 morreram, rc=0 (guardas 792, 793, 824 de forge-testes cobertas, inclusive --vermelho, --modulos, --prazo). As duas juntas (delta, `--base 48bf85e8`): M1 a M7, M10, M8, M9, M13, M11, M12 morreram, rc=0 (era rc=2, A3). Rev da rodada c5c3a449.
- `python3 -m unittest -q tests.test_pre_envio_brief` no c5c3a449: 11 testes, OK; `tests.test_testes_tocados.Mapa.test_forge_check_roda_os_modulos_dele` (contagem 82): OK.
