---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-limpeza-fim-item
commit: 9aa1e723f310c9cb3607ceddeb8864f1ac5b87b4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-limpeza-fim-item (revalidação)

Etapa E68.8 do pedido v0478. Revalidação por delta (R-REVIEW) da rodada anterior (E68.3, head 71996730, no git). Delta lido: `forge-check parecer delta` sobre `71996730..9aa1e723`; no domínio, só `bin/forge-copia`. Fora do domínio: changelog, mutante e testes, lidos só os casos novos de A1 e A2.

## Gatilhos
Gatilhos: apagamento de arquivo no disco (cópias de trabalho), controle do fluxo de fechamento (`forge-fechar --limpar`), leitura de dado vindo do GitHub (`gh pr list`).

## Estado dos achados anteriores
- A1 (recomendado, corrigido) `bin/forge-copia:114-121`: o `gh pr list` agora pede `state,isCrossRepository`, e só entra em `estados` a linha com dois campos e `isCrossRepository == false`. PR de fork é ignorado. Sem PR próprio, vale só `vazio: sim` (fail closed). Teste: `test_pr_fechado_de_fork_com_o_mesmo_nome_nao_encerra_o_item`. O falso `gh` do teste sai com 1 se a chamada não pedir `isCrossRepository`.
- A2 (recomendado, corrigido) `bin/forge-copia:131-169`: as checagens viraram `sujeira()` e rodam de novo depois de `fim_do_item`, logo antes do `worktree remove` ou do `rmtree`. Teste: `test_escrita_durante_a_consulta_ao_gh_fica`, que escreve na cópia dentro de `fim_do_item` e espera rc 2 com a cópia intacta. A correção mantém também a checagem anterior, e por isso a cópia suja fica sem consultar o `gh` (`test_copia_suja_fica` com o `gh` em falha). Resta uma janela local de milissegundos entre a 2ª checagem e o `rmtree`. Ela fica sem rede no meio, e no caso da worktree o próprio `git worktree remove` sem `--force` refaz a checagem. Isso não é achado.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodei no head `tests.test_forge_copia.Limpar` e `tests.test_forge_fechar.LimparSemMerge`: 28 testes, OK. No head, não há PR nem CI. A suíte inteira fica com o CI do PR, que é o portão do merge (R-FLUXO). Faltaram no PATH: `gitleaks`, `semgrep` e `shellcheck`. O delta não toca credencial nem dependência.
