---
tipo: qa
contrato: 1
pedido: lote-m8-hook
branch: melhoria/lote-m8-hook
commit: 0e64acb2341f43de138ebfdfe405edb264617d11
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-26
---
# QA: lote-m8-hook

Base do diff: 35057a2c5436f7415a9473bf4bd656b85264125c (develop com o PR 1); 5 arquivos (`.githooks/pre-push`, `tests/test_pre_push_afetados.py`, `tests/test_testes_tocados.py`, `tests/mutantes/lote-m8-hook.json`, `changelog.d/lote-m8-hook.md`). Rodado em paralelo com review e segurança (ACELERA-RODADA, item 4); vale para este head.

## Achados
- A1 (recomendado) .githooks/pre-push:261 · a âncora `git merge-base "$base_dev" HEAD` não tem teste: o mutante `ancora="$base_dev"` sobrevive (no brinquedo a base é a própria âncora); com a base adiantada, o mutante só recuaria para a suíte inteira (mais seguro), então não é defeito, é lacuna de teste
- A2 (recomendado) .githooks/pre-push:251 · guardas de sha hexadecimal e não-zero e o `return 1` de `base_dev` mudaram sem mutante; os mutantes de QA sobrevivem por equivalência (a guarda HEAD = $unico_local já as cobre), sem correção

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
| NaoEPortao: só o pre-push cita o forge-testes em `.githooks`; recuo para a suíte inteira | test_so_o_pre_push_cita_o_script_em_githooks, test_pre_push_recua_para_a_suite_inteira | conjunto exato `{.githooks/pre-push}` | passou |

## Cenários e resultado real
* `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados`: Ran 94 tests, OK. Rodei só os testes do item (cada teste do hook roda o hook de verdade num repositório de brinquedo; sem suíte completa fora do pre-push).
* Brinquedo, a pergunta do brief: diff só em código mapeado (dirigido) roda `rodou-sugerir`, `rodou-forge`, e `verde` não existe; diff que muda `tests/test_a.py` roda as três suítes e a suíte inteira anota a árvore verde (os dois primeiros testes da tabela, passando). Quem anota é só a suíte inteira.
* Vermelho (`bin/forge-testes --vermelho 35057a2c5436f7415a9473bf4bd656b85264125c --modulos test_pre_push_afetados,test_testes_tocados`), rc=0:
  `vermelho: base=35057a2c5436 head=0e64acb2341f ...`; `revertidos à base: .githooks/pre-push, changelog.d/lote-m8-hook.md`; contagem: prova (asserção)=6, não prova (passa na base)=88; nenhum teste cai no HEAD. Provam: NaoRecuaDoHook.test_o_hook_cita..., test_base_e_a_ref_remota..., test_diff_que_toca_o_filtro..., test_falha_em_modulo_nao_afetado..., NaoEPortao.test_so_o_pre_push_cita_o_script_em_githooks e mais um do PrePushAfetados.
* Mutação, `bin/forge-mutante tests/mutantes/lote-m8-hook.json`, saída 0: M1 a M8 · morreu (linhas 253, 253, 253, 263, 263, 257, 305, 248). Conferida contra o diff: cobre árvore limpa, link, HEAD, diff vigiado (2), base remota, `completa=1` e `n_refs`.
* Mutantes extras de QA (spec descartável, fora da árvore): `refs/heads` morreu; plano `case` (X5) morreu; âncora sobreviveu (A1); sha hex/zero e `base_dev` sobreviveram por equivalência (A2).
* Acessibilidade e E2E de UI: n/a (portão local em shell).

## Riscos
Dirigido depende do mapa do `bin/forge-testes` do PR 1; a bateria completa segue no CI do PR (decisão do dono).
