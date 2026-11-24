---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d1-integrador-laco
commit: 8b056d4d81fc3c68596c10afb7ba41f8003efe19
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E173.15, D1 INTEGRADOR-EM-LACO, PR #865)

Escopo: diff `8a6f5907..8b056d4d` (`bin/forge-fechar`, `bin/forge-testes`, `tests/test_fechar_laco.py`, mutantes, pesos, fragmento do changelog). Pergunta do brief: o `--laco` nunca mescla sem pareceres aprovados e todos os checks do head verdes, e nunca usa merge automático. Resposta: sim; o efeito na postura é **neutro** (nenhum portão afrouxado; o laço só escolhe e delega ao caminho do item, que continua sendo o único que mescla).

## Gatilhos
Gatilhos: controle do fluxo de merge (forge-fechar), leitura de dado do GitHub que decide argumento de comando, variável de ambiente de teste.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido, com evidência:

- **Sem merge novo, sem merge automático.** O diff não acrescenta nenhuma chamada de merge do `gh` nem opção de merge automático; o laço só roda o próprio script por item ou por `--lote` (`bin/forge-fechar:1334`). O único merge do script segue em `mesclar_direto`, preso ao head (`--match-head-commit`), depois de `checks_do_head_verdes 6` (`bin/forge-fechar:1793`, `:1802`), que exige todo check-run do head em completed/success (FECHAR-NUNCA-AUTO) e para no terminado fora dele. Sonda S1 abaixo.
- **Pareceres:** o filtro do laço (`forge-check pr` no head buscado, `bin/forge-fechar:1315`) é só pré-seleção; o item refaz o passo 1 (`forge-check pr` no sha conferido, head relido depois) e o merge sai preso a esse sha. Um PR que o filtro deixasse passar por engano ainda pararia no item.
- **Entrada do GitHub:** PR de fork fica fora pelo `isCrossRepository` (`bin/forge-fechar:1277`); só `melhoria/*` com `git check-ref-format --branch` (`:1312`, recusa `:`, espaço e controle, então o `pedido:branch` do lote e o `read -ra` não se partem); o pedido vem do frontmatter do parecer de review com `branch:` igual e passa por `^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$` (`:1285`). Todos os argumentos vão em array, sem `eval`.
- **Base:** só `origin/develop` (a main e o resto são recusados antes, `bin/forge-fechar:201-205`); o `--laco` recusa pedido, ref, lote, limpeza e cartões (`:173`).
- **Códigos:** CI da develop não verde depois de um grupo (5) para o laço (`:1338`); grupo que para (1) não mesclou nada daquele item e o laço segue.
- **Falsos de teste:** `FORGE_FECHAR_AGORA` e `FORGE_FECHAR_ITEM` só valem com `FORGE_FECHAR_TESTE=1` (`:231`); fora dele, o item é o próprio script.

Sonda (fora do bloco por não provar bloqueante): S1, script em arquivo, sobre as linhas adicionadas de `bin/forge-fechar`: chamadas de merge novas 0, opção de merge automático 0, delegação ao item 1; merge do `gh` no script inteiro 1 (o `mesclar_direto`).

Testes: `tests/test_fechar_laco.py` rodado neste head, 10 testes, OK (os de seleção cobrem vermelho e em conflito fora do merge, reprovado no `forge-check pr`, pedido ambíguo, fork de nome, branch fora de `melhoria/*`). A suíte inteira fica com o CI do PR #865, em andamento no head 8b056d4d quando este parecer foi escrito.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `git diff`, sonda local em arquivo, o teste do arquivo tocado e leitura dos checks do PR pelo `gh` (só leitura). Varreduras de segredo e de workflow não se aplicam (o diff não toca workflow nem configuração).
