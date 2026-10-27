---
tipo: review
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: 70ba6c614bdaa0f2dae1c3aff051ba53a2b97f43
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: lote-coment-prepush (COMENTARIOS-PREPUSH, pedido LOTE-COMENT-PREPUSH-REV, E1.1, volta 1)

Revalidação por delta do parecer anterior (9dc6c43, head bcdb3b9). Referência de comportamento: `.githooks/pre-push` da develop 739b0b0, igual no head (`git diff --quiet 739b0b0 70ba6c6 -- .githooks/`).

## Delta lido
`bin/forge-check delta --parecer docs/reviews/lote-coment-prepush.md`, intervalo `bcdb3b9..70ba6c6`:
- `README.md`:68 (+1 -1)
- `bin/forge-testes`:27-28 (+2 -1)
- `tests/test_forge.py`:299 e 303-312 (+11 -1)
- `tests/test_testes_tocados.py`:432-437 (+6)

Já lido na rodada anterior, sem mudança no delta: o resto de `README.md`, a docstring de `bin/forge-testes` fora de 27-28, `changelog.d/lote-coment-prepush.md` e os testes da primeira rodada. Os pareceres de segurança (0861257) e QA (386ac94) entram no intervalo, mas não são deste review.

## Garantido por ferramenta
- `python3 -m unittest tests.test_forge.PrePushSoOsAfetados tests.test_testes_tocados.NaoEPortao` em 70ba6c6: `Ran 10 tests`, `OK`.
- A frase que o teste do A3 cobra agora (``diff que toca `bin/forge-testes`, `tests/config.json` ou `.githooks/` ``) aparece 0 vezes no README de 739b0b0: o teste cobra o caso novo.
- Teto M14: `git diff --numstat --no-renames 739b0b0...70ba6c6` dá 38 linhas de código e teste (`README.md` fica fora por ser `.md`; `bin/forge-testes` 4+3, `tests/test_forge.py` 17, `tests/test_testes_tocados.py` 12). Dentro do teto, sem `hooks/` nem `PROTEGIDOS`.
- Suíte completa não rodada (brief: só os testes do item); fica no pre-push e no CI do PR. `docs/engineering/praticas.md` não existe no Forge; checklist da skill por leitura. Achados recorrentes (PA-7): lista vazia.

## Achados
- A1 (bloqueante) README.md:68 · requisito, texto falso: diz que em `melhoria/*` mais de uma ref, árvore suja e HEAD diferente do enviado seguem o dirigido, mas o `dirigido()` os recusa (pre-push:251, 256, 257) e roda a suíte inteira
- A5 (recomendado) tests/test_forge.py:303 · o teste novo passa com o texto do A1: cobra os termos soltos e "segue a regra acima", mas não que mais de uma ref, árvore suja e HEAD diferente sigam para a suíte inteira também em `melhoria/*`

## Situação dos achados anteriores
- A1 · mantido (bloqueante), reescrito acima. Os casos que faltavam (árvore suja, mais de uma ref, HEAD diferente, sem `origin/develop`) agora estão no texto, mas três deles aparecem só como falha do caminho só de parecer, e a frase seguinte diz que em `melhoria/*` eles rodam só os afetados. Para quem lê, uma `melhoria/*` com a árvore suja roda só os afetados, e o hook roda tudo. Sugestão: "em `melhoria/*`, um envio de uma ref só, com a árvore limpa e o HEAD igual ao enviado (ref nova, prova ausente, outro arquivo, modelo `_*`, `ameacas/` ou `aceites/`), segue a regra acima; mais de uma ref, árvore suja, HEAD diferente, sem `origin/develop` ou falha de leitura do plano vai para a suíte inteira".
- A2 · fechado. Ref nova, prova ausente, outro arquivo, modelo `_*`, `docs/security/ameacas/` e `aceites/` em `melhoria/*` seguem o dirigido, como no hook (o `dirigido()` não olha o sha remoto nem o caminho só de parecer; pre-push:229, 270-273). A parte que ficou errada é a do A1.
- A3 · fechado. `tests/test_forge.py`:299 cobra a frase inteira do caso novo, ausente na base.
- A4 · fechado. `bin/forge-testes`:27-28 diz que o autor e os revisores rodam só os testes do item, e que a suíte inteira fica no pre-push e no CI, conforme o corte 1 da decisão ACELERA-RODADA. O teste em `tests/test_testes_tocados.py`:432 barra a frase antiga e cobra a nova.

## Parecer
Reprovado, por um bloqueante (A1), que é texto do README em desacordo com o hook. O cartão existe para alinhar esse texto. O resto do delta está certo: A2, A3 e A4 fechados. A5 é recomendado e não devolve sozinho, mas a correção do A1 cabe na mesma volta, com uma asserção de que, também em `melhoria/*`, mais de uma ref e árvore suja vão para a suíte inteira.

Checklist (delta): escopo sem nada a mais, só texto e os testes dele; `R-NEUTRO` sem termo novo; `R-CUSTO` nada pago; regras invioláveis preservadas; um commit em Conventional Commits em português. Segurança: só texto, com parecer próprio na branch (0861257). Devops: sem pipeline no diff.
