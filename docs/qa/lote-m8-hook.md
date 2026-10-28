---
tipo: qa
contrato: 1
pedido: lote-m8-hook
branch: melhoria/lote-m8-hook
commit: 0ff73965e955912d52fc078fa03d219a6f43e0a6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-m8-hook

Base do diff: 35057a2c5436f7415a9473bf4bd656b85264125c (develop com o PR 1); arquivos de código e teste (`.githooks/pre-push`, `tests/test_pre_push_afetados.py`, `tests/test_testes_tocados.py`, `tests/mutantes/lote-m8-hook.json`, `changelog.d/lote-m8-hook.md`). Rodado em paralelo com review e segurança (ACELERA-RODADA, item 4); vale para este head.

## Achados

## Critério → teste → resultado
Sem especificação de UX/CA numerado; as obrigações são as decisões do dono do pedido (A de 2026-10-23/24, C, corte 2) e o escopo E1 a E3.
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Envio dirigido roda só os módulos do mapa e não anota árvore verde | PrePushAfetados.test_so_os_modulos_do_mapa_rodam_e_nao_anotam_a_arvore_verde | prova de árvore só da suíte completa | passou |
| Opção C: módulo de teste mudado (`tests/test_a.py`) roda a suíte inteira e anota | PrePushAfetados.test_so_modulo_de_teste_mudado_roda_a_suite_inteira_e_anota | módulo de teste no diff | passou |
| Caminho sem regra no mapa cai na suíte inteira | test_caminho_sem_mapa_roda_a_suite_inteira_e_anota | caminho fora do mapa | passou |
| Falha fechada: sem base, sem ferramenta, árvore suja, link, HEAD diferente, várias refs, ref não-branch | test_sem_a_base..., test_sem_a_ferramenta..., test_arvore_suja..., test_ferramenta_que_e_link..., test_commit_enviado_diferente..., test_varias_refs..., test_ref_que_nao_e_branch... | cada pré-condição do dirigido | passou |
| Diff em filtro, mapa ou hook não se auto-julga | test_diff_que_toca_o_filtro_o_mapa_ou_o_hook_roda_a_suite_inteira | `bin/forge-testes`, `tests/config.json`, `.githooks/` | passou |
| Base é `refs/remotes/origin/develop`, não branch local homônima | test_base_e_a_ref_remota_mesmo_com_branch_local_de_mesmo_nome | ref ambígua | passou |
| Falha em módulo afetado barra; em não afetado não barra | test_falha_em_modulo_nao_afetado_nao_barra_e_no_afetado_barra | rc 1 | passou |
| Bloqueios de conteúdo (main, homolog, develop, não fast-forward) antes do filtro | test_bloqueios_de_conteudo_valem_antes_do_filtro | destino proibido, histórico reescrito | passou |
| Python do plano e da execução com `-I`: módulo falso em `bin/` não decide | test_modulo_falso_em_bin_nao_decide_o_plano_nem_a_execucao, test_modulo_falso_ja_na_base_nao_zera_a_execucao_dirigida | `bin/` da branch no sys.path | passou |
| Dirigido só para `refs/heads/melhoria/*` | test_dirigido_so_vale_para_melhoria | outra branch roda a suíte inteira | passou |
| Âncora do diff vigiado é a base comum com a develop | test_ancora_e_a_base_comum_com_a_develop_nao_a_ponta_da_develop | base adiantada | passou |
| NaoEPortao: só o pre-push cita o forge-testes em `.githooks`; recuo para a suíte inteira | test_so_o_pre_push_cita_o_script_em_githooks, test_pre_push_recua_para_a_suite_inteira | conjunto exato `{.githooks/pre-push}` | passou |

## Cenários e resultado real
Revalidação da volta 1, head 0ff73965e955 (antes: 0e64acb). Mudou desde o parecer anterior: `python3 -I` no plano e na execução, envio dirigido só para `refs/heads/melhoria/*`, teste da âncora merge-base, mutantes M9 a M12 (M1, M2, M3 e M8 saíram da spec).
* `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados`: Ran 98 tests, OK (só os testes do item).
* Vermelho, `bin/forge-testes --vermelho 35057a2c5436f7415a9473bf4bd656b85264125c --modulos test_pre_push_afetados,test_testes_tocados`, rc=0: `vermelho: base=35057a2c5436 head=0ff73965e955`; contagem: prova (asserção)=8, não prova (passa na base)=90, nenhum cai no HEAD. Provam, entre outros, test_ancora_e_a_base_comum_com_a_develop_nao_a_ponta_da_develop (novo, fecha o A1 anterior) e test_modulo_falso_ja_na_base_nao_zera_a_execucao_dirigida (-I).
* Mutação, `bin/forge-mutante tests/mutantes/lote-m8-hook.json`, saída 0: M4, M5, M6, M7, M9, M10, M11, M12 · morreu (linhas 265, 265, 259, 307, 266, 276, 252, 263). Conferida contra o diff: linhas de guarda mudadas (`-I` no plano, `-I` na execução, `refs/heads/melhoria/*`, `merge-base`) têm M9, M10, M11, M12 cada uma.
* M1, M2, M3 e M8 (que saíram da spec) em spec temporária em $TMPDIR (`bin/forge-mutante`, saída 0): M1 · morreu (255), M2 · morreu (255), M3 · morreu (255), M8 · morreu (250). Ainda morrem no head.
* A1 anterior (âncora) fechado: o mutante `ancora="$base_dev"` (M12) morre pelo teste novo. O A2 anterior (guardas de sha hex e não-zero, `return 1` de `base_dev`) segue como equivalência já aceita (a guarda HEAD = commit enviado as cobre); sem bloqueio.
* Acessibilidade e E2E de UI: n/a (portão local em shell).

## Riscos
Dirigido depende do mapa do `bin/forge-testes` do PR 1; a bateria completa segue no CI do PR (decisão do dono).
