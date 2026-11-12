---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: 0a0a7c808607535ddfe5e2eaf715a9340d7f8b8b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v0457 (E23.53, melhoria/escopo-ponto no 0a0a7c80)

Revalidação por delta (E23.53, volta E23.52), por instância que não fez a entrega. Delta lido: `forge-check parecer delta docs/reviews/escopo-ponto.md`, intervalo 73e4848c3d431b8ac2e99beff0d0b63f2d054284..0a0a7c808607535ddfe5e2eaf715a9340d7f8b8b, no domínio bin/forge-check, changelog.d/escopo-ponto.md, tests/mutantes/v0457-escopo-ponto-{3,5}.json, tests/test_selo_e_entrega.py. Testes dos arquivos tocados, um módulo por vez: `test_selo_e_entrega` 73 OK; `test_conf_escopo` 16 OK.

## Achados
- A6 (recomendado) bin/forge-check:2351 · veredito_trocado faz um `git show` por arquivo da pasta em cada versão; com as subpastas (`ls-tree -r`) e o `--full-history` desta volta, o número de versões e de arquivos só cresce; filtrar antes com `git grep -l <commit> <sha> -- <pasta>` ou `cat-file --batch`
- A7 (recomendado) bin/forge-check:2336 · o parâmetro `nome` de veredito_trocado ficou sem uso (a pasta agora vem de `PASTA_E_REGRA[tipo]`); tirar da assinatura e das chamadas (bin/forge-check:2372 e os testes)

## Revalidação dos achados anteriores
- Segurança A7 conferido sem achado de review: o `rev-list` da pasta usa `--full-history` (bin/forge-check:2343); os dois testes do merge de ramo lateral cobrem as duas ordens de pais (o commit do revisor como primeiro pai e como segundo, com fast-forward depois), e M34 os aponta.
- Segurança A8 conferido sem achado de review: a pasta vem de `PASTA_E_REGRA[tipo][0]` (bin/forge-check:2342) e o `ls-tree -r` (bin/forge-check:2347) desce às subpastas; o `tipo` chega do único chamador já com `tipo` não vazio e é chave de PASTA_E_REGRA; há teste da subpasta com o reprovado apagado e M35. M20 e M22 acompanharam a assinatura nova e o `--full-history` (AR-12).
- Specs de mutantes (AR-12): os 35 `de` de tests/mutantes/v0457-escopo-ponto*.json casam uma vez só com o bin/forge-check do head. Os escopo-ponto.mutante*.log em ~/.forge-contrib/wt são da manhã (o último às 11:27); "M1 a M35 mortos, cobertura rc 0" é declaração do autor e fica com o QA.
- A6 segue recomendado; o forge-check pr que não detecta parecer forjado segue como cartão da versão seguinte (rodada anterior).

## Tamanho (M14)
673 linhas de código e teste desde o Base-sha 8b5a44d5. O PR precisa trazer `teto: excedido, 673 linhas, <motivo>`; o motivo (consertos da mesma conferência em três voltas, volume nos testes dos ramos negativos) basta.

## Parecer
Aprovado: o delta fecha A7 e A8 da segurança com teste e mutante e não traz defeito provado. A6 e A7 do review são recomendados (custo e limpeza). O mérito das âncoras fica com o security-engineer; a mutação, com o QA.
