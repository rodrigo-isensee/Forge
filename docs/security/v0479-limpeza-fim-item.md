---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-limpeza-fim-item
commit: 70115210cd8bb0d1d0579f11b651ffe536a06ed6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-limpeza-fim-item (revalidação)

Etapa E68.13 do pedido v0478. Esta é uma revalidação por delta (R-REVIEW). A rodada anterior foi a E68.8, aprovada no head 9aa1e723, e está no git. Li o delta com `forge-check parecer delta` sobre `9aa1e723..70115210`. No domínio entrou só `bin/forge-fechar`. Fora do domínio ficaram o changelog, `tests/mutantes/v0479-limpeza-fim-item-5.json` e `tests/test_forge_fechar.py`. Desses, li só os 5 casos novos e os 4 mutantes.

## Gatilhos
Gatilhos: apagamento de arquivo no disco (cópias de trabalho), controle do fluxo de fechamento (`forge-fechar --limpar`), leitura de dado vindo do GitHub (`gh pr list`).

## Delta lido
- `bin/forge-fechar:796-801` `fim_sem_merge`: devolve 0 só em dois casos. O primeiro é uma linha `CLOSED` com `isCrossRepository == false`, porque o PR de fork com o mesmo nome não conta, como no A1 do `forge-copia`. O segundo é `forge-check vazio` com rc 0 e saída começando por `vazio: sim`. Rc diferente de 0 dá `return 1`. As saídas `vazio: não` e `vazio: não verificável` não casam com o prefixo. Em todos esses casos a função falha fechado.
- `bin/forge-fechar:1306-1311`: o `gh pr list` passou a pedir `isCrossRepository` como 5º campo. A ordem ficou assim: PR `OPEN` recusa, depois sem `fim_sem_merge` recusa com a mensagem anterior, e só então vem `limpar_copias_sem_merge`. A prova também não substitui a do `forge-copia limpar`, que relê o fim do item e a limpeza da cópia antes de apagar. São duas travas em série, e nenhuma apaga branch. `$check` vem de `forge-check` real fora de `FORGE_FECHAR_TESTE=1` (linhas 200-211). Assim, o ambiente não troca o oráculo da prova.
- Conclusão: nada é apagado sem prova. O caminho sem prova sai com rc 1 e a mensagem de antes, e a cópia fica.

## Estado dos achados anteriores
- A1 e A2 (recomendado, corrigidos em 9aa1e723): continuam corrigidos. O delta não toca o `bin/forge-copia`.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodei no head `tests.test_forge_fechar.LimparSemMerge` e `tests.test_fechar.Fechar.test_c3_limpar_sem_prova_de_pr_merged_recusa_e_nao_apaga_nada`: 13 testes, OK. Apliquei à mão o mutante M29, que tira o filtro de fork. O teste `test_pr_fechado_de_fork_nao_e_prova_e_a_copia_fica` falhou, ou seja, matou o mutante. Depois restaurei o arquivo. A suíte inteira fica com o CI do PR, que é o portão do merge (R-FLUXO). Faltaram no PATH `gitleaks`, `semgrep` e `shellcheck`. O delta não toca credencial nem dependência.
