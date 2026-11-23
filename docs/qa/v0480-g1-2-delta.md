---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: bdd44bc03d942aa8e119a16db562def9d3eb9a43
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 G1.2 (bloqueante novo só no que mudou)

Escopo: `fora_do_delta` em `bin/forge-check` (ligado em `cmd_docs` estrito e `cmd_pr`), textos dos agentes e regras, `tests/test_parecer_fora_do_delta.py`. Sem suíte local; a suíte inteira é do CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| G1.2: bloqueante novo fora do trecho mudado é recusado | test_bloqueante_novo_fora_do_delta_e_recusado, test_pr_recusa_pela_cli, test_docs_recusa_pela_cli | fora do delta | passou |
| Margem de 3 linhas | test_bloqueante_no_trecho_mudado_ou_na_margem_passa, test_fora_da_margem_de_3_linhas_e_recusado | limite da margem | passou |
| Repetição (mesmo id e arquivo) passa | test_bloqueante_repetido_da_rodada_anterior_passa, test_mesmo_id_em_outro_arquivo_nao_e_repeticao | id igual, arquivo outro | passou |
| Recomendado não é recusado; promovido é | test_recomendado_fora_do_delta_passa, test_recomendado_anterior_promovido_fora_do_delta_e_recusado | gravidade | passou |
| Segurança com `explorável: S<n>` e sonda | test_seguranca_exploravel_com_sonda_passa, test_seguranca_exploravel_sem_a_sonda_e_recusado, test_exploravel_no_review_nao_vale | sonda ausente, tipo review | passou |
| Faixa larga não cruza | test_faixa_larga_nao_cruza_o_delta | faixa >= 20 | passou |
| Sem rodada anterior, git falho, sem commit, mesmo commit, outro pedido, sem frontmatter: não recusa | test_primeira_rodada_nao_recusa, test_git_que_falha_nao_recusa, test_diff_que_falha_devolve_none, test_parecer_sem_commit_valido_nao_recusa, test_mesmo_commit_nao_e_rodada_anterior, test_rodada_anterior_de_outro_pedido_nao_conta, test_versao_sem_frontmatter_e_ignorada, test_docs_sem_base_nao_e_estrito_e_nao_recusa | vazio, falha | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_parecer_fora_do_delta.py`: Ran 21 tests, OK. `test_testes_tocados.py`: Ran 196, OK (skipped=1, já existente).
- Vermelho antes do verde: `forge-testes --vermelho 5cff9f6 --modulos test_parecer_fora_do_delta` → `vermelho: base=5cff9f6aa191 head=bdd44bc03d94`; 18 "prova (API ausente)", 2 "prova (asserção)", 1 "não prova (passa na base)" (`test_docs_sem_base_nao_e_estrito_e_nao_recusa`, guarda negativa: sem `--base` já não recusava); nenhum cai no HEAD; rc=0.
- Mutantes (`forge-mutante --base 5cff9f6 <spec>`, `base=5cff9f6aa191… rev=bdd44bc03d94`): v0480-g1-2-delta FD1–FD8 morreram; -2 FD9–FD16 morreram; -3 FD17–FD22, FL1, FL2 morreram. Nenhum sobrevivente; 24 mutantes sobre as linhas de guarda do diff em `bin/forge-check` (4126–4172, 479–480, 2045).

## Observações
Nada bloqueante. Sem bug registrado.
