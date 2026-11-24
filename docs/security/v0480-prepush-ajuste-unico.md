---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-prepush-ajuste-unico
commit: 61997e21f1b1b2164fa943cef707b7c634148ef4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E4.9), PR #871, revalidação por delta do ajuste único do pre-push

Volta por delta. A rodada anterior (E4.4, aprovado em 13063422, parecer no commit 775bd3fb) fica no git e não é recopiada; o veredito dela se mantém.

## Gatilhos
Gatilhos: controle de envio (pre-push, por patch para o dono), teste que sai (catraca R-CONFORMIDADE), afrouxa-regra autorizado.

## Delta lido (082f1f9e a 61997e21)
- Dois merges da develop (6a1ffa85 e 61997e21) trazem #866, #869 e #868 (D7), todos já na develop (`bbbe2d88` é ancestral de `origin/develop`). O que eles mudam em `.githooks/`, `hooks/` e `.github/` vem da develop: `git diff --quiet bbbe2d88 61997e21 -- .githooks hooks .github` vazio, e esse conteúdo tem os pareceres dos PRs de origem.
- Diff efetivo do PR, antes (`a27eab7e..082f1f9e`) e depois (`bbbe2d88..61997e21`): os mesmos 23 arquivos e o mesmo +641/-616. A única linha que difere é contexto, não do PR: o `"test_criterios"` que o D7 pôs na tupla `FORGE_CHECK` de `bin/forge-testes`; o resto são índices de blob e números de linha dos hunks.
- Resolução do conflito (`git show --remerge-diff 61997e21`, `bin/forge-testes:159`): entra `test_criterios` (da develop) e continua fora `test_prepush_lote_pp1` (deste PR). É a união correta. `tests/test_criterios.py` existe no head e `tests/test_prepush_lote_pp1.py` não; não sobra referência ao módulo removido em `bin/` nem em `tests/`, só a menção em prosa de `tests/test_prepush_unico.py:8`.
- Classificação: **neutro**. Nada no delta aperta nem afrouxa. A tupla só decide quais testes rodam juntos com o forge-check; o teste do D7 continua rodando e nenhum teste da catraca muda além dos que a rodada anterior já registrou como saída autorizada.

## Detalhe dos achados
Sem achado. Verificação no head 61997e21:
- `python3 -m unittest tests.test_prepush_unico tests.test_pre_push_d2 tests.test_pre_push_patch tests.test_testes_tocados tests.test_criterios`: 260 testes, OK (1 pulado, que não é deste PR). `git apply --check patches/prepush-unico.patch`: aplica.
- CI: no 61997e21, catraca, instalação, verificações longas, passos e "árvore já provada na develop" estão verdes. As partes da suíte foram canceladas no 61997e21 e no 5a3e16de porque os pareceres de review e de QA (41169bd2) chegaram em seguida. Esses envios só tocam `docs/reviews/` e `docs/qa/`, e a árvore de código continua a do 61997e21. A suíte completa roda no último envio de parecer (este). A bateria de pareceres está vermelha à espera dos pareceres, como esperado.

## Riscos aceitos e ferramentas
O risco aceito segue o da rodada anterior: saem o teste e os mutantes das duas partes fora do ajuste (DECISÃO DO DONO 2026-11-24 17:08, pedido v0478). O delta não traz risco novo. Faltaram no PATH: gitleaks, shellcheck e zizmor (não instalo; o CI roda o shellcheck). O delta não tem segredo nem workflow próprio do PR.
