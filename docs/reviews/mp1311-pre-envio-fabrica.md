---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-fabrica
commit: f30ac8d2f3edb92ef9b6b0bd81299c1b6b746ce0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: mp1311-pre-envio-fabrica

## Achados
- A1 (recomendado) tests/test_pre_envio_brief.py:131 · o teste de `--texto` não combina cobre 5 das 9 opções barradas em bin/forge-testes:792; `--vermelho`, `--modulos` e `--prazo` não têm caso, e tirar um desses termos do `or` não derruba nenhum mutante. Acrescente os três ao laço.
- A2 (recomendado) bin/forge-check:8283 · `TESTES_DE_TEXTO` está duplicada em bin/forge-check e bin/forge-testes; o teste `test_a_lista_do_brief_e_a_do_modo_de_texto` as mantém iguais, então a duplicação é consciente (o teste proíbe o forge-check citar o forge-testes). Sem ação agora.

## Sondas

## Parecer
Aprovado, head f30ac8d2 (classe C). Atende ao E1.17 e à DECISÃO DO DONO de 13/11 17:31: o brief de autor (`codigo` e `pr`) traz a PQ da descrição do PR (catraca `pr-texto`) e a PQ de texto sempre; a PQ dos testes afetados só no `codigo` com caminho de código no Entregar; parecer fica sem elas; fora do Forge nada disso é cobrado. Os briefs de parecer exigem `gh pr checks <n>` quando há PR e, sem PR, dizem que a suíte fica para o CI. `forge-testes --texto` roda os cinco alvos num `unittest` só e devolve o rc.

Rodado: `tests.test_pre_envio_brief` e `tests.test_testes_tocados` (161 testes, OK, 1 pulado por /proc do sandbox); `bin/forge-testes --texto` (179 testes, rc=0). Mutação: `bin/forge-mutante` nas duas specs, 10 de 10 mortos (M1 a M7 e M10; M8 e M9). Guardas do diff cobertas, um mutante por linha. `shellcheck` não se aplica (Python). Suíte inteira: CI do PR; sem PR ainda. Tamanho: 204 linhas de código e teste (bin 63, teste 141), acima das 150; o PR precisa levar `teto: excedido, 204 linhas, <motivo>` (comportamento único: pré-envio do brief e comando de texto). O parecer de segurança está em docs/security/mp1311-pre-envio-fabrica.md e não foi refeito.
