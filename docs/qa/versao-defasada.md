---
tipo: qa
contrato: 1
pedido: versao-defasada
branch: melhoria/versao-defasada
commit: 4c078a96a811e88d4e1d8bc35b12a6b031283d9c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: versão defasada (E2.4)

Código testado: 4c078a9 (HEAD da worktree 67fc9c4, que só acrescenta os pareceres de review e segurança). Cópias falsas e fixtures, sem rede (as tentativas de rede do sandbox foram negadas e não afetaram nenhum teste).

## Execução
- `python3 -m unittest discover -s tests -q`: 923 testes, OK, 184 s. Nenhum teste falhou e passou de novo sem mudança (flaky: nenhum).
- `scripts/validar-plugin.sh`: "Validation passed" (marketplace, plugin e dev).

## Critério → teste → resultado
| Critério (brief) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Projeto com prova de atraso: `pr`, `entrega`, `brief gerar` erram com a frase de atraso | `FerramentaDefasadaNoProjeto.test_cache_com_atraso_bloqueia_pr_entrega_e_brief_gerar` | prova positiva de atraso | OK |
| `delta` e os outros só avisam | `test_delta_so_avisa_nos_projetos`, `test_cache_com_atraso_so_avisa_nos_outros` | exceção ao bloqueio | OK |
| Sem prova positiva não bloqueia | `test_sem_prova_positiva_nao_bloqueia` | ausência de prova | OK |
| Hook parecer barra `gh pr create` (código 2, uma linha) | `HookParecerGuardaDaVersaoNoProjeto.test_copia_atrasada_barra_o_portao`, `HookParecerGuardaDaVersaoNoForge.test_projeto_com_copia_atrasada_barra_o_pr_de_ponta_a_ponta` | código 2, saída única | OK |
| Em dia: hook mudo | `test_em_dia_passa_em_silencio` | limite igual/mais nova | OK |
| Forge e clone de contribuição: só avisa; hook mudo, código 0 | `FerramentaDefasadaNoForge.*` (atrasada com e sem o objeto, código de saída, quatro subcomandos), `HookParecerGuardaDaVersaoNoForge.test_no_forge_a_copia_atrasada_nao_bloqueia_e_o_hook_fica_mudo`, `test_manifesto_do_forge_num_projeto_nao_o_torna_o_forge` | Forge x projeto | OK |
| Verificação desligada: "versão não conferida (verificação desligada)" e não apaga prova | `test_verificacao_desligada_aparece_na_saida`, `test_verificacao_desligada_nao_apaga_a_prova_de_atraso`, `DoutorVersao.test_consulta_desligada_fica_no_cache_e_nao_apaga_a_prova_de_atraso` | consulta desligada | OK |
| Erro de comparação só avisa | `test_erro_na_comparacao_vira_aviso_e_segue`, `test_cache_ilegivel_vira_aviso_e_segue`, `test_erro_de_comparacao_nao_bloqueia_e_o_hook_fica_mudo` | cache ilegível, falha de comparação | OK |
| jarvis-forge avisa com o tmux aberto | `JarvisForgeDefasagem.test_com_a_sessao_aberta_atras_avisa_a_data_e_o_comando_sem_trocar_o_plugin`, `test_o_aviso_se_repete_em_toda_reanexacao`, `test_com_a_sessao_aberta_em_dia_fica_em_silencio` | em dia x atrás | OK |
| "ATRASADO desde" em falha de rede ou de rev-list | `test_com_a_sessao_aberta_e_sem_rede_diz_atrasado_desde_a_data`, `test_rev_list_com_falha_depois_do_fetch_diz_atrasado_desde_a_data`, `test_abertura_sem_rede_diz_atrasado_desde_a_data`, `test_abertura_com_recusa_diz_atrasado_desde_a_data` | sem rede, comparação falha | OK |

## Vermelho antes do verde
Cópia do HEAD em `$TMPDIR/vermelho` com `bin/`, `hooks/` e `scripts/` trocados pelos de 8833e1c (develop), testes novos mantidos: `python3 -m unittest -q tests.test_doutor.DoutorVersao tests.test_doutor.JarvisForgeDefasagem tests.test_forge.FerramentaDefasadaNoForge tests.test_forge.FerramentaDefasadaNoProjeto tests.test_hooks.HookParecerGuardaDaVersaoNoProjeto tests.test_hooks.HookParecerGuardaDaVersaoNoForge`. Resultado: 36 testes, FAILED, com falhas e erros em todas as seis classes (entre eles `test_cache_com_atraso_bloqueia_pr_entrega_e_brief_gerar`, `test_atrasada_sem_o_objeto_so_avisa_nos_quatro_subcomandos`, `test_verificacao_desligada_aparece_na_saida`, `test_rev_list_com_falha_depois_do_fetch_diz_atrasado_desde_a_data`, `test_abertura_sem_rede_diz_atrasado_desde_a_data`; as classes do hook parecer falham na importação). Os testes negativos (em dia, sem prova, `--dev`) passam nos dois lados, como esperado.

Mutação: não rodada por mim; review e segurança registraram que o mutante sem a guarda falha.

## Achados
