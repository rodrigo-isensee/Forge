---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-modelo
commit: 2b5fbd83fb4776c16dd6668448b0accb9d0a9657
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: pré-envio no modelo de projeto (E1.35, diretriz 23, partes b, c e e)

Head 27c40107. Sem PR aberto na hora do parecer (`gh pr list --head` vazio): sem check-run `bateria` para citar; rodados só os testes afetados e a prova de mutação (máquina com carga ~22).

## Achados
- A1 (recomendado) templates/projeto/.githooks/pre-push.local:8 · `rapido='...'` entre aspas simples: comando de stack com `'` quebra o arquivo gerado. As stacks de hoje não têm; vale checar na stack nova.

## Critério → teste → resultado
O pedido não tem especificação de UX; as obrigações são as da entrega (E1.16).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Stack declara pronto rápido e completo | test_cada_stack_declara_pronto_rapido_e_completo | n/a | passou |
| Modelo de PR com as seções cobradas | test_modelo_de_pr_tem_as_secoes_que_o_review_cobra | n/a | passou |
| forge-init grava os dois | test_projeto_novo_recebe_modelo_de_pr_e_pronto_rapido | n/a | passou |
| Migração leva ao projeto existente e o envio roda o rápido | test_projeto_atualizado_ganha_os_dois_e_o_envio_roda_o_pronto_rapido (+ test_adotar) | n/a | passou |
| Não sobrescreve o do projeto | test_atualizacao_nao_sobrescreve_o_pre_push_local_do_projeto, test_modelo_de_pr_do_projeto_fica | arquivo existente | passou |
| Stack desconhecida, fora da forma (`../`), inexistente ou sem rápido não gera | test_stack_desconhecida..., test_stack_fora_da_forma_ou_inexistente_nao_gera, test_stack_sem_pronto_rapido... | stack inválida, travessia | passou |
| CLAUDE.md sem a linha vale node-react | test_claude_md_sem_a_linha_da_stack_vale_node_react | arquivo ausente | passou |
| Sem código da stack, pula com aviso; stack sem Detecção | test_sem_codigo_da_stack_o_pronto_rapido_pula_com_aviso, test_stack_sem_deteccao_gera_o_pre_push_local_que_pula | lista vazia | passou |
| `--sem-versionar` / config quebrada vai ao exclude | test_sem_versionar_os_criados_vao_para_o_exclude | False, True, inválido | passou |
| forge-upgrade roda vários passos em ordem, um commit cada | test_forge_upgrade_roda_os_passos_da_versao_em_ordem_um_commit_cada | ordem migrar < migrar-<passo> | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge.PreEnvioDoModelo`: 14 testes, OK. `tests.test_adotar`: 24 testes, OK.
- Vermelho antes do verde: `forge-testes --vermelho c5aa70e1 --modulos test_forge,test_adotar` estourou o prazo com a máquina carregada (rc 124), sem veredito, que não vale como vermelho. Recuo manual: cópia em `$TMPDIR` no head com `bin/`, `templates/`, `stacks/` e `migrations/` da base, sem os arquivos novos: `Ran 14 tests ... FAILED (failures=15, errors=5)`, os 14 testes novos caem.
- `bin/forge-mutante` das três specs (21 mutantes): todos `morreu` (M1 a M21). `forge-mutante --cobertura --base c5aa70e1`: toda condição Python mudada em `bin/forge-upgrade` e na migração está `coberta`; `pre-push.local` (shell, `não coberto` pela ferramenta) tem M3, M4 e M21; a mudança no `pre-push` é só comentário.
- `bin/forge-check docs`: sem erro.

## Revalidação por delta 27c40107..2b5fbd83 (E1.58, head 2b5fbd83)
Delta: pre-push do modelo (só texto: `docs/**`, `*.md`, `changelog.d/**` e junção com a origin/develop pulam o pronto rápido; apagar ou criar código roda), `pre-push.local` (`${arquivos[@]+...}` contra array vazio), textos de stacks e migração, seção de veredito do vermelho em TypeScript, testes e spec de mutantes `-4`.
| Critério (decisão do dono 13/11 17:31) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Texto, parecer e fragmento passam sem o rápido | test_envio_so_de_texto_nao_roda_o_pronto_rapido | `changelog.d/.gitkeep` (fora de `*.md`) | passou |
| Código ou misto roda | test_envio_com_codigo_ou_misto_roda_o_pronto_rapido | texto + código no mesmo envio | passou |
| Apagar código roda | test_envio_que_apaga_codigo_roda_o_pronto_rapido | arquivo ausente na origin/develop | passou |
| Junção sem código novo pula; código mexido depois roda | test_juncao_com_a_develop_sem_codigo_novo_nao_roda_o_pronto_rapido | blob igual ao da develop x diferente | passou |
| TS tem mapa e veredito explícito | test_vermelho_em_typescript_tem_mapa_e_veredito_explicito | `não verificável`, pop sempre | passou |
- Rodados no head: `PreEnvioDoModelo`, `TextosAQ3Stack`, `VerificarContribuicao` (37 testes, OK); `tests.test_prepush_so_docs` (62 testes, OK, 9 pulados pelo sandbox: não exercitam o delta aqui, o CI os roda).
- Vermelho: `forge-testes --vermelho 27c40107` não terminou no prazo (carga ~13), sem veredito; vale o recuo manual: cópia do head com `pre-push` e `node-react/pronto.md` da base, 3 testes novos: `FAILED (failures=3)` (só_texto, junção, TS). Apagar e misto são guardas de regressão (passam na base), mortos pelos mutantes M31 e M32.
- `bin/forge-mutante tests/mutantes/mp1311-pre-envio-modelo-4.json`: M30, M31 e M32 `morreu` (pre-push:78, 80, 81), rc 0. Linhas de guarda mudadas no diff: as três têm mutante.
- Sem PR/check-run `bateria` do head citável por mim; a suíte inteira fica com o CI.
- A1 segue recomendado, sem mudança.

## Evidência de bugs
Nenhum bug aberto.
