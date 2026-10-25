---
tipo: qa
contrato: 1
pedido: lote-s1-scripts
branch: melhoria/lote-s1-scripts
commit: 979c1ffd8ef43e608aca0f792c56afa4dd6d27d6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-s1-scripts

Pedido LOTE-S1-SCRIPTS (E1 a E4; revisão LOTE-S1-SCRIPTS-REV, E3.1), revalidação 2. Head testado `979c1ffd8ef43e608aca0f792c56afa4dd6d27d6` (código idêntico ao do commit seguinte, que só traz pareceres), base `3c66b881af31817ce5d2dde996c7ca56d54cb511`; parecer anterior sobre `61cd77261133a31fe4ba900d12b668a740f51e50` (reprovado: A1 bloqueante, A2 recomendado). Sem especificação de UX nem contrato de API: as obrigações são os itens E1 a E4 do pedido e as decisões da volta 1 (teto 1 a 75 s, conferência da remota com `ls-remote`, documentação do integrador).

## Achados

## Revalidação dos achados anteriores
- A1 (spec de mutantes): resolvido. `tests/mutantes/lote-s1-scripts.json` (M1 a M8, um por guarda mudada na entrega original) e `tests/mutantes/lote-s1-scripts-volta.json` (V1 a V3, as guardas da volta 1; dois arquivos pelo teto de 8 do `forge-mutante`). Conferido contra o diff: as guardas mudadas na volta (faixa 1 a 75 na linha 107, `[ -z "$sha_depois" ]` na 468, falha do `ls-remote` na 467) têm mutante cada uma.
- A2 (M8, `[ -O . ]`): justificativa aceita. O mutante sobrevive, é equivalente para usuário comum: o `chmod` em pasta de outro dono falha com EPERM (cai no `die`) e a checagem de dono do caminho vem antes (linha 168); a guarda é defesa em profundidade contra a troca do caminho depois dela, o que não há como provocar de forma determinística. A justificativa consta no campo `guarda` do M8 na spec.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 modo da pasta do log vira 700, setuid e setgid saem | tests.test_fechar_log_check.FecharLogCheck.test_pasta_do_log_do_proprio_usuario_com_modo_diferente_de_700_vira_700_com_aviso (4755 e 6755 novos) | modos 755, 777, 500, 2755, 4755, 6755 | passou |
| E1 chmod age sobre a pasta já aberta, não sobre o caminho (TOCTOU) | ...FecharLogCheck.test_o_chmod_da_pasta_do_log_age_sobre_a_pasta_ja_aberta_e_nao_sobre_o_caminho | argumento do chmod é `.` | passou |
| E2 push --delete que trava é cortado pelo teto, 3 tentativas, remota dita viva, código 3 | tests.test_fechar_orfao.Teste.test_push_delete_que_trava_e_cortado_pelo_teto_e_a_remota_viva_e_dita | teto 1 s; remota segue no servidor | passou |
| E2 teto 1 a 75 s, padrão 75 s; pior caso 3x75 + 2x30 + 10 = 295 s (volta 1) | ...Teste.test_teto_do_delete_fora_da_faixa_e_recusado_e_o_pior_caso_das_tres_tentativas_fica_em_300s | 0, 1, 75, 76, 100, 101, não numérico | passou (vermelho na base 61cd772) |
| E2 corte depois de o servidor apagar a ref: confere com ls-remote, remota=ok, sem "continua viva" (volta 1) | ...Teste.test_corte_depois_que_o_servidor_apagou_a_remota_confere_e_nao_diz_que_ela_continua_viva | ref ausente no servidor | passou (vermelho na base) |
| E2 ref ainda no servidor após o corte: segue dita viva, pendente, código 3 | ...Teste.test_corte_com_a_remota_ainda_no_servidor_segue_dizendo_que_ela_continua_viva | ref presente | passou (guarda; passa na base por desenho) |
| E2 ls-remote falha: pendente, sem afirmar que está viva | ...Teste.test_corte_com_a_conferencia_da_remota_falhando_fica_pendente_sem_afirmar_que_esta_viva | leitura da remota falha | passou (vermelho na base) |
| Doc do integrador descreve chmod u-s, teto 1 a 75 e a conferência da remota (volta 1) | leitura de docs/fechamento-integrador.md:20,52,58,71 contra o código | n/a | conferido, bate com bin/forge-fechar:25,107,466-476,178 |
| E3 changelog.d link: release não publica nem apaga .md externos | tests.test_changelog.Release.test_changelog_d_como_link_para_fora_da_raiz_nao_publica_nem_apaga_os_md_externos | pasta como link para fora | passou |
| E3 fragmento que é link para fora recusado, alvo fica | ...Release.test_fragmento_que_e_link_para_fora_da_raiz_e_recusado_e_o_alvo_fica | arquivo como link | passou |
| E3 `novo` com changelog.d link não grava fora | ...Release.test_novo_com_changelog_d_como_link_e_recusado_sem_gravar_fora | pasta como link | passou |
| E3 versão aninhada antes da de topo com manifesto já na versão alvo recusada | ...Release.test_versao_aninhada_antes_da_de_topo_com_o_manifesto_ja_na_versao_alvo_falha_sem_gravar_nada | topo = alvo, aninhado antes | passou |
| E4 aviso do perfil directory não sai como ✘ com validação passando | tests.test_forge.ValidarPluginAviso.test_aviso_do_perfil_directory_com_validacao_passando_nao_sai_como_x | rc 0 | passou |
| E4 falha real mantém ✘ e código | ...ValidarPluginAviso.test_validacao_que_falha_mantem_o_x_e_o_codigo | rc 1 | passou (guarda; passa também na base, por desenho) |

## Cenários e resultado real
- Testes do lote no head: `tests.test_fechar` `Ran 80 tests in 29.774s · OK`; `tests.test_fechar_log_check tests.test_fechar_orfao tests.test_changelog` `Ran 71 tests in 33.310s · OK (skipped=1)`. O skip é `FragmentoTemONomeDaBranch` (worktree em HEAD solta, branch não `melhoria/*`), preexistente. A suíte completa roda no pre-push; `test_forge` e `validar-plugin.sh` não mudaram desde o parecer anterior (577 testes OK no `8e22f17`).
- Vermelho (`forge-testes --vermelho 61cd77261133a31fe4ba900d12b668a740f51e50 --prazo 900`, saída 0): `vermelho: base=61cd77261133 head=979c1ffd8ef4`; `revertidos à base: bin/forge-fechar, docs/fechamento-integrador.md`; `contagem: não prova (passa na base)=1945; prova (asserção)=3; pulado=1`. Os 3 que provam, todos `H=ok · B=falha`: `test_corte_depois_que_o_servidor_apagou_a_remota_confere_e_nao_diz_que_ela_continua_viva`, `test_corte_com_a_conferencia_da_remota_falhando_fica_pendente_sem_afirmar_que_esta_viva`, `test_teto_do_delete_fora_da_faixa_e_recusado_e_o_pior_caso_das_tres_tentativas_fica_em_300s`. `test_corte_com_a_remota_ainda_no_servidor_segue_dizendo_que_ela_continua_viva` passa na base por desenho (guarda do comportamento que não podia mudar).
- Mutação, `forge-mutante` sobre a spec da branch: `lote-s1-scripts.json` rc=1 só por M8 (`M1 a M7 · morreu`, `M8 · sobreviveu · bin/forge-fechar:178`, equivalente justificado acima); `lote-s1-scripts-volta.json` rc=0 (`V1 · morreu · bin/forge-fechar:107`, `V2 · morreu · :468`, `V3 · morreu · :467`). Somei 3 mutantes meus (spec fora da branch, em `$TMPDIR`): `Q1` tirar `rem_st=pendente` da remota viva, `Q2` padrão 75 para 60, `Q3` tirar `rem_st=pendente` da conferência que falha: os três `morreu`, rc=0.
- Mão, `push --delete` que trava de verdade (remota real com `pre-receive` dormindo 30 s, `FORGE_FECHAR_TETO_DELETE=2`, fluxo completo sobre `gh` e `forge-check` falsos): `registro: apagando a branch remota melhoria/x (até 2s por tentativa, 3 tentativas)`, `limpeza: remota=pendente worktree=ok branch=ok`, aviso `a branch remota continua viva`, rc=3, 6,4 s, `ls-remote` ainda mostra a ref.
- Mão, servidor apaga antes do corte (`post-receive` dormindo 30 s, mesmo teto): `limpeza: remota=ok worktree=ok branch=ok`, `fim: código 0`, 2,4 s, sem a frase "continua viva", `ls-remote` vazio (o corte caiu depois de a ref sair; a rodada seguinte viu a ref ausente).
- Não executado: acessibilidade e E2E de navegador (sem interface). PA-7 (`docs/engineering/achados-recorrentes.md`) segue vazio ("nenhum ainda"): nada a conferir.

## Riscos
- `timeout` mata só o `git push`; um filho do pre-push que ignore o sinal pode sobreviver ao corte (não provado, não bloqueia).
- Sem o `timeout` no PATH (macOS), a limpeza roda sem teto (desenhado e documentado).
- A cota de 300 s do pior caso soma as pausas no máximo (30 s); o teste confere a aritmética, não mede o tempo de relógio.
