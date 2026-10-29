---
tipo: qa
contrato: 1
pedido: t1-conf-escopo
branch: melhoria/t1-conf-escopo
commit: 5d1e769b0165f2e892f7d51b2569c5f8cb34b86b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: t1-conf-escopo (lote 1 e volta 1, T1-CONF-ESCOPO-REV, E3.1)

Sem UX nem API; as obrigações são E1 a E4 do pedido T1-CONF-ESCOPO e os achados A1 a A3 da rodada anterior. Revalida o head 5d1e769 (volta 1: f8b0962, ccca64d, 91efab7, fd5bbcf; o merge da develop f3f63f9 e o corte da linha em branco do `agents/conferente.md`, 110 linhas). Não escrevi o diff. QA em paralelo com review e segurança (decisão ACELERA-RODADA, item 4). A suíte completa e o `scripts/validar-plugin.sh` ficam fora do item (brief); rodei os módulos do item.

## Achados

## Critério → teste → resultado
| Obrigação | Teste / comando | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 da rodada anterior: aceite e `tests/config.json` nunca saem `ok` na merge-integracao, com pareceres aprovados | `test_aceite_e_config_nunca_sao_anexo_nem_com_pareceres_aprovados` (ref viva e mergeCommit) | arquivo protegido com os três pareceres válidos | passou; vermelho na base; M18 e M19 morreram |
| A2: dois pedidos nos reviews do mergeCommit reprovam em vez de escolher um | `test_dois_pedidos_nos_reviews_do_squash_reprovam` (pedido `z`, que ordena depois de `x`) | dois pedidos / um só | passou; vermelho na base; M20 morreu |
| A3: parecer trazido por merge só é anexo com tipo da pasta, `parecer` válido e branch do pedido | `test_parecer_trazido_por_merge_so_vale_com_tipo_parecer_e_branch_do_pedido` (3 subtestes) | tipo trocado, parecer inválido, outra branch | passou; passa na base (a base não tinha anexo), a prova é por mutação: M21, M22 e M23 morreram |
| E1: pareceres aprovados no head, ref apagada, sem parecer ou reprovado | `test_branch_com_parecer_aprovado_no_head_nao_marca_arquivo_fora`, `test_sem_parecer_ou_com_parecer_reprovado_continua_reprovando`, `test_ref_apagada_le_o_merge_commit_do_squash`, `test_merge_commit_sem_parecer_reprova` | parecer ausente, reprovado, squash | passou; vermelho na base |
| E1: `--desde` mantém a leitura do delta | `test_desde_nas_etapas_de_branch_inteira_le_so_o_delta` | delta | passou; M17 morreu |
| E2: fragmento da própria branch e parecer da própria branch trazido por merge, só por acréscimo | `test_fragmento_do_changelog_da_propria_branch`, `test_parecer_da_propria_branch_so_vale_trazido_por_merge`, `test_anexo_com_remocao_continua_confira` | remoção; edição depois do merge | passou; vermelho na base (o da remoção passa na base, esperado) |
| E3/E4: módulo novo no mapa, contagem 29 | `test_testes_tocados`, `test_forge_check_roda_os_modulos_dele` | contagem do mapa | passou |
| Texto do `conferente.md` (item 2, merge-integracao) cita as duas exceções e 110 linhas | leitura + teste de 110 linhas do `test_forge` (não rodado aqui; ver Execução) | teto de linhas | `wc -l` = 110; a ser confirmado pelo pre-push |

## Execução (módulos de `forge-testes --listar bin/forge-check`: 30, com `test_mensagem_conferente` vindo da develop; carga abaixo de 3 antes de cada lote)
- `test_conf_escopo`, `test_testes_tocados`, `test_volta_por_delta`, `test_conferencia_base_dono`, `test_conferencia_registrar`, `test_mensagem_conferente`, `test_fechar_base_andou`: `Ran 219 tests` / `OK`.
- `test_anotar`, `test_brief_gravar`, `test_catraca`, `test_citacao`, `test_doutor_relogio`, `test_erros_no_brief`, `test_hook_ansi_c`, `test_estado_da_branch`, `test_etapa_do_brief`, `test_guarda_conferente`, `test_guarda_git`, `test_isencoes`, `test_medida_cpu`, `test_medidas_m14b`, `test_pedido_fora`, `test_portao_diff_proprio`, `test_sobreposicao_quadro`, `test_voltas`, `test_hooks_parecer_pasta`: `OK`, rc 0 (a saída traz só avisos "catraca: a API do GitHub não respondeu", sandbox sem rede, que o teste espera).
- `test_forge`, `test_hooks` e os três `test_hooks_volta_*`: não rodados nesta passada; o delta da volta 1 não toca `hooks/`, e o `test_forge` só confere o `conferente.md` (110 linhas e a linha `**Entregas paralelas**`). Ficam ao pre-push e ao CI do PR.

## Vermelho antes do verde
`bin/forge-testes --vermelho 87e32b6b254137b3a55e3796d6aac997f43b0e20 --modulos test_conf_escopo` (rc 0):
```
vermelho: base=87e32b6b2541 head=5d1e769b0165 módulos=test_conf_escopo (restrito por --modulos)
tests.test_conf_escopo.AnexosImplicitos.test_anexo_com_remocao_continua_confira · H=ok · B=ok · não prova (passa na base)
tests.test_conf_escopo.AnexosImplicitos.test_fragmento_do_changelog_da_propria_branch · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.AnexosImplicitos.test_parecer_da_propria_branch_so_vale_trazido_por_merge · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.AnexosImplicitos.test_parecer_trazido_por_merge_so_vale_com_tipo_parecer_e_branch_do_pedido · H=ok · B=ok · não prova (passa na base)
tests.test_conf_escopo.MergeIntegracao.test_aceite_e_config_nunca_sao_anexo_nem_com_pareceres_aprovados · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_branch_com_parecer_aprovado_no_head_nao_marca_arquivo_fora · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_dois_pedidos_nos_reviews_do_squash_reprovam · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_merge_commit_sem_parecer_reprova · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_ref_apagada_le_o_merge_commit_do_squash · H=ok · B=falha · prova (asserção)
tests.test_conf_escopo.MergeIntegracao.test_sem_parecer_ou_com_parecer_reprovado_continua_reprovando · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=2; prova (asserção)=8
```
Os dois "não prova" são esperados: o de remoção já existia, e o de A3 é negativo (na base nenhum parecer é anexo, então cai em `confira` de qualquer jeito); o que o prova são M21, M22 e M23.

## Mutantes
`bin/forge-mutante --cobertura --base 87e32b6b254137b3a55e3796d6aac997f43b0e20`, rc 0: toda condição Python mudada do T1 em `bin/forge-check` (1013, 1014, 1016, 1017, 1019, 1026, 1032, 1034, 1038, 1039, 1092, 1093, 1095, 1096, 1097, 1122, 1124) `coberta`; `isenta` em 1006 e 1037 (frontmatter ilegível vira `{}` e cai em guarda que M2 e M23 cobrem; aceito: trocar `{}` por `{"tipo": None}` é equivalente, porque `tipo` nulo nunca passa o `tipo and` seguinte). As linhas 4657 a 4721 e o `bin/forge-fechar` são da develop (T6T3-MENSAGEM e LOTE-0307-A), com mutantes dos pedidos deles. Lista conferida contra o diff: um mutante por linha de guarda do T1, inclusive a condição nova do A1 (M18, M19), a do A2 (M20) e as três do A3 (M21 a M23).

`bin/forge-mutante tests/mutantes/t1-conf-escopo.json tests/mutantes/t1-conf-escopo-2.json`, rc 0: 23 de 23 `morreu` (M1 a M23), sem sobrevivente nem equivalente declarado.

## Sonda do A1 anterior
A sonda de b9426d8 (`tests/config.json` e `docs/security/aceites/x.md` com os três pareceres aprovados) saía `escopo: ok` nos dois arquivos. No head, o teste novo cobre o caso, em ref viva e em mergeCommit, e exige `escopo: confira` nos dois com o arquivo de trabalho seguindo `ok`.

## Parecer
Aprovado, sem achado. O A1 bloqueante (aceite e `tests/config.json`) e os recomendados A2 e A3 estão corrigidos com teste e mutante; 23 mutantes mortos; módulos do item verdes. Observação sem bloqueio: a guarda do A1 segue lista negativa de dois nomes (classe AR-3); se o `conferente.md` listar outro arquivo protegido, a guarda e os M18/M19 precisam ganhar o nome junto. Não toquei `docs/engineering/achados-recorrentes.md` (decisão de 15:28: a linha AR vai pelo pedido T1-CONF-ESCOPO-2).
