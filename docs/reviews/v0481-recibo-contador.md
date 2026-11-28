---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-recibo-contador
commit: 15759fded5e6f6a78cd9992ef0e62098eaded9fa
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E20.20, #921, RECIBO-CONTADOR-PELO-HOOK item 4: hook `ordens_teto`), volta 1 por delta

Delta lido: `forge-check parecer delta docs/reviews/v0481-recibo-contador.md`, `git diff a1b62cab..15759fde` (5 commits do autor: b7758954, 3114f982, 595a5326, b52ae343, 15759fde). Código: `hooks/ordens_teto.py` (+25, -6) e `bin/forge-testes` (+1, -1); o item fica em cerca de 120 linhas, dentro do H1, um comportamento. Fora do delta, nada relido.

## Leitura
- **A1 (meu, a1b62cab):** resolvido. `Base.setUpClass` carrega o `bin/forge-check` pelo `_comum.forge_check()` com o mesmo Python e as mesmas opções do hook (`-s -E`, ambiente limpo), antes de qualquer caso; `ErroInterno` prova a linha `ordens_teto IsADirectoryError` no erros.log. O `test_hook_ordens_teto` entra no mapa `FORGE_CHECK` do `bin/forge-testes`, que aquece o forge-check no lote. No executor oficial, em cópia limpa, M1, M6 e M10 morrem agora.
- **A2 (meu):** resolvido. M16 (`if False:` na guarda `__main__`) declarado e morto; a catraca do head está verde.
- **A2 da segurança (Criacao):** o `trocar` separa as três guardas; trecho vazio sobre texto vazio devolve o `new_string`, como a ferramenta cria o arquivo; sobre texto não vazio, `None` (a ferramenta falha). `depois` trata o arquivo ausente (`lexists`) como texto vazio. MultiEdit que cria e segue somando é contado em sequência. Testes cobrem ausente, vazio e MultiEdit.
- **A3 da segurança (AcimaDoTeto):** `nao_cresce` compara linhas e caracteres pela mesma `escapadas` e só é chamada acima do teto (curto-circuito); `tamanho` tira a conta duplicada da mensagem. Arquivo que não se lê dá `False` e a recusa segue. Os quatro casos (encurta, cresce, mesmas linhas com mais caracteres, mais linhas com menos caracteres) têm par recusa e passa.
- **A4 da segurança (NoForge):** clone do Forge de mentira com a casa temporária; a fonte é `~/.forge-contrib/docs/ordens/` e o arquivo de projeto dentro do clone não conta.
- **Mutantes:** M3 e M8 reapontados para o teste que de fato os mata depois da separação das guardas; M15 ajustado ao `or` novo; M17 a M23 cobrem cada guarda nova, um por linha, na `-3.json`.
- **Registros:** ADR 0003 (item 3 da emenda) e o fragmento do changelog descrevem a criação pelo Edit e a gravação que não cresce. Commits em Conventional Commits com o pedido e a etapa.

## Verificações
- Rodados aqui no 15759fde (log em `~/.forge-contrib/_tl314-v0481-E20.20-mut.log`): `python3 -m unittest tests.test_hook_ordens_teto` (23 testes, OK); `bin/forge-mutante --processos 1` nas três specs (23 de 23 morreram); `bin/forge-mutante --cobertura --base 707fea56` (22 guardas cobertas, nenhuma sem mutante; não cobertos só `hooks/hooks.json` e `tests/pesos-d4.json`, sem guarda).
- CI do 15759fde (run 45891106581 e catraca 45891172795): suíte 3.12 e 3.14 (partes 1 a 5), bateria (passos), bateria (verificações longas), bateria (python 3.14), instalação, teto de pulados, árvore já provada na develop e catraca verdes. Falham só `bateria (pareceres)` e `bateria`, que esperam os pareceres.
- ci: 15759fded5e6f6a78cd9992ef0e62098eaded9fa verde

## Parecer
Aprovado. Os dois achados da 1.ª rodada estão resolvidos (aquecimento do forge-check com prova do erros.log e mutante da guarda `__main__`), e os ajustes pedidos pela segurança (criação pelo Edit, gravação que não cresce acima do teto e a fonte do Forge) são pequenos, coerentes com a ADR 0003 emendada e cobertos por teste e mutante em cada guarda.
