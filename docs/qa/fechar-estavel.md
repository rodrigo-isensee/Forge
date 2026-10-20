---
tipo: qa
contrato: 1
pedido: fechar-estavel
branch: melhoria/fechar-estavel
commit: 6a1f2b3fee83ca24ea8ba1e24da2ea2f7e97ef0d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: FECHAR-ESTAVEL

Código testado: `6a1f2b3` (o HEAD da branch, `7785caa`, só soma os pareceres de review, segurança e devops em `docs/`). Worktree `~/.forge-contrib/wt/fechar-estavel`, sem alteração de código. Sem `gh` real nem rede: o `gh` e o `git --delete` são os falsos de `tests/test_fechar.py`.

## Achados

## Critério → teste → resultado
| Critério (escopo do pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: head já na base não abre PR | `test_head_ja_mesclado_na_base_nao_abre_pr` | head ancestral de `develop`; zero `pr create` e zero merge | passou |
| E1: PR MERGED no mesmo head e base (passo 3) não abre nem mescla | `test_nova_rodada_com_pr_ja_mesclado_no_head_nao_abre_pr_nem_mescla` | MERGED com head igual | passou |
| E1: MERGED com outro head não conta | `test_pr_mesclado_com_outro_head_nao_impede_o_pr_novo` | head diferente (guarda) | passou |
| E1: MERGED em outra base não conta | ad hoc em `$TMPDIR` (MERGED em `homolog`: abre e mescla 1 vez) | base diferente | passou (sem teste no repo, ver recomendação) |
| E1, passo 6: PR já MERGED conta como sucesso sem novo merge | `test_merge_com_erro_mas_pr_merged_segue_sem_repetir`; ad hoc (estado MERGED na leitura do passo 6: zero merges) | estado MERGED lido no passo 6 | passou |
| E2: leitura do PR e dos checks repete e passa com 502 passageiro | `test_502_na_leitura_do_pr_repete_e_passa` (3 `pr list`), `test_502_na_leitura_dos_checks_repete_e_passa` | 2 falhas, 3ª tentativa | passou |
| E2: o estado relido no passo 6 repete | `test_estado_desconhecido_e_relido_e_merged_nao_abre_pr_nem_mescla_de_novo` | 2 falhas de estado | passou |
| E2: 3 falhas param, sem criar nem mesclar | `test_502_na_leitura_do_pr_em_tres_tentativas_para_sem_abrir_pr`, `test_502_nos_checks_em_tres_leituras_seguidas_para_no_passo_4`, `test_estado_desconhecido_nas_tres_leituras_para_sem_repetir_o_merge` | limite de 3 tentativas | passou |
| E2: `push --delete` repete até 3 vezes e depois só avisa | `test_502_no_push_delete_da_limpeza_repete_e_apaga`, `test_push_delete_que_falha_tres_vezes_so_avisa` | exatamente 3 chamadas, rc 0 | passou |
| E2: `pr create`, `pr ready` e merge nunca repetem | `test_502_no_merge_nao_repete_o_merge`, `test_criacao_de_pr_ready_e_merge_nunca_passam_pela_repeticao`; ad hoc (1 falha de `pr list`: 1 `pr create`) | 1 chamada do merge e da criação | passou |
| E3: item do rótulo igual no modelo e no corpo gerado, desmarcado | `test_modelo_de_pr_traz_o_item_do_rotulo_desmarcado_igual_ao_do_script` | um só item, `- [ ]`, texto idêntico | passou |
| E4: doc cita a fonte certa da regra do título | conferência do diff de `docs/fechamento-integrador.md` (E4 sem teste automático próprio) | n/a | conferido |
| E5: fragmento de changelog | suíte estrutural (testes de changelog) | n/a | passou |

## Cenários e resultado real
- Suíte inteira, `python3 -m unittest discover -s tests -q` na raiz da worktree: `Ran 1026 tests in 243.808s`, `OK`. Sem skip. Desvio de R-TETO: outra suíte (pid 250) começou nos segundos entre o `--status` (rc=1) e o início da minha; as duas correram juntas, sem efeito no resultado.
- `scripts/validar-plugin.sh`: rc 0, `Validation passed` (marketplace e plugin). As negações de rede (`api.anthropic.com`, datadog) vieram do sandbox.
- Vermelho antes do verde: `git archive HEAD` em `$TMPDIR/vermelho` com `bin/forge-fechar` de `ef71b3c` e os testes da branch: `Ran 47 tests`, `FAILED (failures=9, errors=1)` (repetido duas vezes, mesmo resultado). Falham: os 3 de `502_na_leitura_do_pr`/`checks` repete, `502_no_push_delete` (2 testes), `estado_desconhecido_e_relido`, `head_ja_mesclado`, `merge_com_erro_mas_pr_merged`, `nova_rodada_com_pr_ja_mesclado` e `push_delete_que_falha_tres_vezes` (FAIL), mais `test_pr_em_rascunho_vira_pronto_antes_do_merge` (ERROR: o `gh` falso agora devolve 3 campos; teste antigo, não novo).
- Só guardas (passam também com o script antigo): `test_estado_desconhecido_nas_tres_leituras_...`, `test_pr_mesclado_com_outro_head_...`, `test_502_nos_checks_em_tres_leituras_...`, `test_502_no_merge_nao_repete_...`, `test_criacao_de_pr_ready_e_merge_nunca_passam_pela_repeticao` (alarme estático por linha, não prova) e `test_modelo_de_pr_traz_o_item_...` (o script antigo já trazia o item; a guarda impede o modelo de divergir). O review contou 5; com o do modelo, são 6.
- Instabilidade: `tests.test_fechar` rodou 3 vezes (1 na suíte, 2 na cópia vermelha só no que importa para a ordem) e a suíte inteira uma vez; nenhum teste falhou e passou de novo sem mudança.
- Mutação: sem ferramenta gratuita para shell em `stacks/`; não rodada. Os 3 cenários ad hoc acima cobrem as lacunas de teste que o review apontou (A3) e a base diferente.

## Recomendações (não bloqueiam)
- Levar ao repo os dois cenários ad hoc (MERGED em outra base; MERGED lido só no passo 6, A3 do review), no pedido do cartão FECHAR-MERGED-HEAD, junto de R1 da segurança.
- Renomear o teste de A1 do review (o nome diz que não abre PR, mas afirma 1 criação e 1 merge).
