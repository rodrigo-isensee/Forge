---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-fabrica
commit: 48bf85e84376c7be335f50742b2afebaa4875769
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: melhorias-de-projeto-1311 (pré-envio da fábrica, E1.55)

Head 48bf85e8, revalidação do parecer do f30ac8d2 (`forge-check parecer delta`: só `tests/test_pre_envio_brief.py` e `tests/mutantes/mp1311-pre-envio-fabrica-2.json` mudaram no domínio do QA). PR 554: suítes 3.12 e 3.14 (partes 1 a 3) e teto de pulados passam no run 43598148745 (sha igual ao head). Falham `bateria (pareceres)` (review desatualizado e este parecer reprovado) e `catraca` (rótulo `afrouxa-regra`, do dono): papelada, não produto.

## Achados
- A1 (recomendado) tests/test_pre_envio_brief.py:122 · resolvido na E1.44: agora o teste falha por asserção na base; `--vermelho` sai rc=0.
- A2 (recomendado) tests/test_pre_envio_brief.py:88 · dois testes de guarda seguem passando na base (fora do Forge, parecer sem pré-envio do autor); fronteira guardada, justifique no PQ do autor.
- A3 (bloqueante) tests/mutantes/mp1311-pre-envio-fabrica-2.json:26 · o id M10 existe nas duas specs; `forge-mutante <spec> <spec-2>` sai rc=2 ("id de mutante repetido entre as specs"). Renumere (ex.: M13) para a rodada única do pedido valer.

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
- `forge-mutante` spec 1: M1 a M7 e M10 morreram, rc=0; spec 2: M8 a M12 morreram, rc=0 (guardas 792, 793, 824 de forge-testes cobertas, inclusive --vermelho, --modulos, --prazo). As duas juntas: rc=2 (A3).
