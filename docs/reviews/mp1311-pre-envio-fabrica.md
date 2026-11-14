---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-fabrica
commit: 48bf85e84376c7be335f50742b2afebaa4875769
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: mp1311-pre-envio-fabrica

## Achados
- A2 (recomendado) bin/forge-check:8283 · `TESTES_DE_TEXTO` está duplicada em bin/forge-check e bin/forge-testes; o teste `test_a_lista_do_brief_e_a_do_modo_de_texto` as mantém iguais, então a duplicação é consciente (o teste proíbe o forge-check citar o forge-testes). Sem ação agora.
- A3 (bloqueante) tests/mutantes/mp1311-pre-envio-fabrica-2.json:26 · o id M10 já existe em tests/mutantes/mp1311-pre-envio-fabrica.json:76; o forge-mutante recusa as duas specs do pedido juntas (rc=2, 'id de mutante repetido entre as specs: M10', nada roda), contra o contrato de bin/forge-mutante:7. Renumere (ex.: M13).

## Sondas
- S1 · bin/forge-mutante tests/mutantes/mp1311-pre-envio-fabrica.json tests/mutantes/mp1311-pre-envio-fabrica-2.json · espera: os 13 mutantes rodam · obtido: rc=2, spec inválida, id de mutante repetido entre as specs: M10

## Parecer
Reprovado, head 48bf85e8 (classe C), revalidação por delta. Delta lido (`forge-check parecer delta`, rc=0): f30ac8d2..48bf85e8, no domínio só tests/mutantes/mp1311-pre-envio-fabrica-2.json e tests/test_pre_envio_brief.py.

A1 da rodada anterior está resolvido: o laço de `test_texto_nao_combina_com_outra_opcao` cobre `--vermelho`, `--modulos` e `--prazo` e confere a mensagem da guarda do `--texto` (não outra recusa do parser); o teste do `--texto` falha por asserção, não por erro, sem a opção. Os mutantes M10 a M12 novos casam uma vez cada em bin/forge-testes:792-793 e morrem: `bin/forge-mutante tests/mutantes/mp1311-pre-envio-fabrica-2.json` deu M8 a M12 mortos, rc=0. `bin/forge-mutante --cobertura --base befd4cca` rc=0. `tests.test_pre_envio_brief` com ambiente limpo: 11 testes, OK.

Bloqueia o A3: o novo M10 da spec 2 colide com o M10 da spec 1, e o conjunto do pedido fica inválido (S1). A correção é trocar o id na spec 2; não muda código. A2 segue recomendado, sem ação.

CI do PR 554 no head 48bf85e8: suíte (3 partes), passos, verificações longas e instalação verdes; `catraca` falha por R-CONFORMIDADE (bin/forge-check tocado, falta o rótulo `afrouxa-regra` do dono) e `bateria (pareceres)` falha por parecer pendente, ambos fora do código. Tamanho: o delta não muda o teto já registrado (o PR precisa de `teto: excedido`). Parecer de segurança em docs/security/mp1311-pre-envio-fabrica.md, não refeito.
