---
tipo: qa
contrato: 1
pedido: impl-d5b-promocao
branch: melhoria/impl-d5b-promocao
commit: ffa8b00957735dd90ac7e318379a6a084766063d
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: impl-d5b-promocao

Escopo: `git diff c092f1b..ffa8b00` (script `scripts/promover-homolog.py`, `tests/test_promover_homolog.py`, classe `GuiaDaPromocao`, guia `docs/promocao-integrador.md`, ajuste em `docs/fechamento-integrador.md`, fragmento do CHANGELOG). Depois de ffa8b00 entraram só os pareceres de review e segurança. Pedido sem `CA-n` em EARS: o E1 do pedido e o desenho (item 22, PA-5, e ação 1 da retrospectiva da 0.28.0) foram a obrigação.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `--dry-run` não muda nada (arquivo, branch, GitHub) | `test_dry_run_nao_muda_nada_e_nao_chama_gh`; sonda real na worktree (status e `for-each-ref` iguais antes e depois) | refs e árvore intactas; `gh` não chamado | passou |
| E1: não mescla | `test_dry_run_nunca_mescla`, `test_abre_o_pr_..._imprime_o_merge_sem_executar`; mutação sem `--match-head-commit` derrubada | merge só impresso | passou |
| E1: só develop → homolog (`R-MAIN`, `R-FLUXO`) | `test_recusa_main_como_base_e_branch_fora_do_fluxo`, `test_pr_aberto_com_base_main_para`; sondas reais com `--base origin/main` e `--ref` de feature (rc 1) | main e par fora do fluxo | passou |
| E1: pareceres na ref | `test_parecer_aprovado_passa`, `..._sem_frontmatter_ou_sem_valor_para`, `..._modelo_com_sublinhado_...`, `..._reprovado_regravado_...`, `test_parecer_ruim_para_antes_de_abrir_o_pr` | sem frontmatter, valor vazio, modelo `_`, parecer antigo | passou |
| E1: versão e CHANGELOG | `test_sem_versao_nova_...`, `test_versao_menor_...`, `test_entrada_da_versao_ausente_...`, `test_nao_publicado_com_conteudo_para`, `test_fragmento_pendente_...` | versão igual, menor, entrada ausente, README da pasta | passou |
| E1: checks, rótulo, sem rede nem `gh` real (`R-CUSTO`) | `test_check_pendente_sai_3_...`, `test_check_vermelho_para`, `test_catraca_vermelha_sem_rotulo_...`, `test_sem_checks_ainda_...`, `test_gh_falso_sem_a_variavel_de_teste_e_ignorado_com_aviso`; `gh` falso e remoto local | pendente, vermelho, catraca, sem check | passou |
| Guia e referência cruzada | `tests.test_forge.GuiaDaPromocao` | guia existe, diz o que não faz, cita reversão | passou |

## Cenários e resultado real
- Suíte do alvo numa cópia limpa do ffa8b00 em `$TMPDIR`: `python3 -m unittest tests.test_promover_homolog tests.test_forge.GuiaDaPromocao tests.test_forge.Neutralidade`: `Ran 28 tests ... OK`. A suíte inteira roda no pre-push do envio deste parecer.
- Vermelho antes do verde: sem `scripts/promover-homolog.py`, `tests.test_promover_homolog` e `GuiaDaPromocao` dão `Ran 26 tests ... FAILED (failures=25)`; a classe de guia passa por não depender do script, os 25 do script falham todos.
- Mutação manual no script (cópia em `$TMPDIR`): derrubaram o teste a mutação do `--dry-run` (passa a escrever), a que trata catraca vermelha como erro comum, a que tira `--match-head-commit`, a que tira a versão igual e a que tira a recusa de PR com base fora da homolog. Sobreviveram duas: tirar o `--diff-filter=AM` (é a R2 informativa do review) e remover o aviso de rótulo já aplicado (só a mensagem; o código de saída 3 é o mesmo).
- Sonda real na worktree: `--dry-run` sobre as refs locais (develop 23 commits à frente da homolog, versão 0.28.0 nas duas, quatro pareceres aprovados): rc 0; árvore e refs idênticas depois.
- Review (ae110be) e segurança (ae0c778): sem bloqueante. R1 (PR de fork cuja branch se chama `develop`; `--json` sem `headRepositoryOwner`) e R2 (parecer apagado na leva não é visto) confirmados como recomendações; sem caminho realista hoje (repositório privado, ADR 0008).

## Recomendações (não bloqueantes)
- Antes de tornar o repositório público: filtrar PR de fork em `pr_aberto` (R1 da segurança), com teste no `gh` falso.
- O `--dry-run` lê as refs locais sem `git fetch`; com refs velhas o resultado é velho. O script e o guia dizem isso; rodar `git fetch origin` antes quando a defasagem importar.
- Acrescentar teste para o aviso de rótulo já aplicado com catraca vermelha (mutante sobrevivente).
- Guia sem teste de mapa em `bin/forge-testes` (cartão D5B-MAPA do pedido, fora do escopo).
