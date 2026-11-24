---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d1-integrador-laco
commit: 0ba10e549428ad4bafbc0139eacbfc870956c89a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E173.29, D1 INTEGRADOR-EM-LACO, PR #865), volta por delta

Revalidação do parecer anterior (E173.15, `commit: 8b056d4d`, aprovado; o texto dele fica no git). Delta lido: `forge-check parecer delta` de `8b056d4d..0ba10e54`, sem o que veio da base. Efeito na postura: **neutro**.

Gatilhos: controle do fluxo de merge (forge-fechar), leitura de dado do GitHub que decide argumento de comando, variável de ambiente de teste.

## Delta lido
- **`docs/fechamento-integrador.md` (5f6c5db0, E173.17):** sinopse do `--laco`, item "Laço" e parágrafo de reversão. Conferido contra o código, sem promessa que o script não cumpra: só `--base`, `--espera`, `--espera-ci` e `--dry-run`; lista até 100 (`bin/forge-fechar:1299`) sem fork (`:1277`); aviso de parado só em stderr, sem rótulo nem comentário, e o PR sai da volta (`:1303-1309`); só `melhoria/*` com `check-ref-format` (`:1311-1312`); código 5 para o laço (`:1338`); `FORGE_FECHAR_AGORA` só com `FORGE_FECHAR_TESTE=1` (`:231`). Os limites citados (A2 e A3 do review: `UNKNOWN` sem aviso, `bateria (pareceres)` contada como vermelho) só afetam o aviso, que não decide merge; nenhum abre caminho de merge.
- **Merge de `origin/develop` (0ba10e54, a6e81a54):** limpo; a árvore do commit (`e294e6c3`) é a mesma do `git merge-tree --write-tree 8d373111 a6e81a54`, então não há resolução manual. As linhas de `bin/forge-testes` que o delta mostra (`test_forge_copia`, a regra de `hooks/decisao.py`) vieram da develop; `bin/forge-fechar` e `tests/test_fechar_laco.py` não mudaram desde `8b056d4d` (diff vazio).
- Fora do domínio: `tests/pesos-d4.json`; pareceres de review e QA da própria branch.

Achados anteriores: nenhum (o parecer E173.15 não tinha achado); nenhum novo.

Testes: `tests/test_fechar_laco.py` (10, OK) e `tests.test_forge.GuiaDaPromocao` (o que lê `docs/fechamento-integrador.md`, 1, OK), rodados neste head. A suíte inteira fica com o CI do PR #865, em andamento no head 0ba10e54 quando este parecer foi escrito (`bateria (pareceres)` vermelha à espera dos pareceres deste head).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `forge-check parecer delta`, `git diff`, `git merge-tree`, os testes acima e a leitura dos checks do PR pelo `gh` (só leitura). Varreduras de segredo e de workflow não se aplicam (o delta não toca workflow nem configuração).
