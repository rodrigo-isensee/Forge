---
tipo: qa
contrato: 1
pedido: vv-2
branch: melhoria/vv-2
commit: 6396f2da9d1344b665ed829634fc84d3670e0499
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA: VV-2 (volta por delta)

Código testado: `6396f2d` (o HEAD da branch, `1a87dbf`, só soma os pareceres de review e segurança em `docs/`). Worktree `~/.forge-contrib/wt/vv-2`, sem alteração de código.

## Achados

## Critério → teste → resultado
| Critério (escopo do pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1, caso 1: `--desde` mostra só a última delegação | `test_desde_mostra_so_a_ultima_delegacao` | intervalo de uma delegação; `tests/config.json` da 1a fora | passou |
| E1, caso 2: `--desde` sem conferência, fora da branch, anterior ao Base-sha, abreviado | `test_desde_sem_conferencia_anterior_reprova_e_volta_ao_base_sha`, `test_desde_anterior_ao_base_sha_reprova`, `test_conferida_so_vale_no_historico_com_sha40` | sha inexistente, abreviado, fora do Histórico | passou |
| E1, caso 3: merge da base depois do `--desde` | `test_merge_da_base_depois_do_desde_com_base_sha_antigo_e_novo` | arquivos só da base fora da lista | passou |
| E1, caso 4: intervalo vazio e autoria de parecer | `test_volta_por_delta` (classe `Entrega`, casos de intervalo vazio e autoria) | vazio; autoria ausente ou hash diferente | passou |
| E1, caso 5: sem `desde` e `pr` iguais a antes | `test_sem_desde_e_a_branch_inteira`, `test_arquivos_da_entrega_sem_desde_e_igual_ao_de_antes`, `test_desde_nas_etapas_de_branch_inteira_reprova` | branch inteira em PR e merge | passou |
| E2, caso 6: `brief --anterior` | `test_anterior_na_raiz_de_brief_do_forge`, `test_anterior_fora_de_docs_briefs_ou_da_raiz_rc_2` | caminho fora de `docs/briefs`, symlink | passou |
| E2, caso 7: `delta` | `test_delta_por_commit_mostra_arquivos_e_trechos`, `test_delta_so_le` | commit inexistente rc 2; só leitura | passou |
| E3, casos 8 e 9: `gerar --volta` e conferência de `Volta-de` | `BriefDeVolta` (`test_gera_blocos_copiados_decisoes_achados_e_prova`, `test_decisao_do_dono_nova_do_pedido_entra_na_volta`, `test_volta_dois_conta_a_partir_do_anterior`, `test_parecer_escrito_pelo_modelo_passa_no_gerar_volta`, `test_volta_fora_de_docs_briefs_recusa`) | parecer sem bloco; achado faltando; sha errado | passou |
| E5, caso 10: PQ `--is-ancestor` | `test_etapa_de_merge_acrescenta_o_pq_por_ancestralidade`, `PqDeMerge` | etapas sem merge sem o PQ | passou |
| E4, caso 10: hook libera `entrega` e `delta`, recusa opção com `-`; agentes usam E1 a E3 | `test_conferente_usa_entrega_desde_e_imprime_a_conferida`, `test_desde_vem_da_mensagem_do_jarvis_e_o_texto_do_hook_e_exato`, `test_pareceres_trazem_achados_e_leem_o_delta`, `tests/test_hooks.py` | opção iniciada por `-` | passou |
| Critério de pronto: falso "escopo: fora" por diff acumulado = 0 | uso de ponta a ponta abaixo | `tests/config.json` da 1a delegação fora do intervalo da 2a | passou |

## Cenários e resultado real
- Suíte inteira, `python3 -m unittest discover -s tests` na raiz da worktree: `Ran 865 tests in 150.169s`, `OK`. Sem skip.
- `scripts/validar-plugin.sh`: rc 0, `Validation passed` (marketplace e plugin). As negações de rede ao `api.anthropic.com` vieram do sandbox, sem efeito no resultado.
- Vermelho antes do verde: `git archive 7226ba7` (base) em `$TMPDIR/vermelho` com `tests/test_volta_por_delta.py` da branch: `FAILED (failures=71, errors=2)`. Com a implementação: verde.
- Uso de ponta a ponta numa cópia em `$TMPDIR/e2e-vv2` (repositório com `develop` e `melhoria/x`, 2 delegações: C1 com `tests/config.json` e `a.txt`, C2 com `b.txt`; pedido do fixture com `## Histórico` e `entrega conferida <C1>`):
  - `forge-check entrega ... --etapa codigo` sem `--desde`: rc 0, lista `a.txt`, `b.txt`, `tests/config.json`.
  - `... --desde C1`: rc 0, `intervalo: <C1>..<C2>` e só `escopo: confira "b.txt" +1 -0`; nenhum `tests/config.json`, ou seja, o falso "escopo: fora" por diff acumulado não aparece na volta.
  - `... --desde C2` (sem conferência): rc 1, `escopo: --desde sem conferência anterior`, volta ao Base-sha. `--etapa pr --desde C1`: rc 1, `escopo: --desde fora da etapa`, branch inteira.
  - `forge-check delta C1`: rc 0, `delta: "b.txt" +1 -0`. `delta` de commit inexistente: rc 2. `delta --parecer docs/reviews/p1.md`: rc 0, intervalo do `commit:` do parecer até o HEAD.
  - `forge-check docs`: rc 0.
  - `forge-check brief gerar --volta ... --ref melhoria/x`: rc 0; copia Objetivo, Fora do escopo, Relatório; `Volta-de` com sha256; 1 item por bloqueante (A1); recomendado A2 em lista à parte com `PREENCHER`; PQ-4 com `--desde <C1>`.
  - `forge-check brief <volta> --anterior <brief 1>`: rc 0, linhas `delta: +`/`delta: -`, `volta: ok`, `resultado: aprovado`. Sem `--anterior`: rc 0, as mesmas linhas sem `anterior:` e `delta:`.

## Observações
- Não rodei mutação (a stack do Forge não traz ferramenta de mutação); o vermelho acima cobre a regra nova.
- Risco do plano (e): o `--desde` depende da linha `conferida` gravada pelo Jarvis; o conferente reconfere a ancestralidade e `forge-check pr` cobre a branch inteira.
