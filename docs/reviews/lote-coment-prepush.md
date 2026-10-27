---
tipo: review
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: bcdb3b9cd07aae4b8d3efd8af274888cd77807f1
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: lote-coment-prepush (COMENTARIOS-PREPUSH, pedido LOTE-COMENT-PREPUSH-REV, E1.1)

Escopo: `739b0b0...bcdb3b9`, um commit (bcdb3b9), cinco arquivos: README.md, bin/forge-testes (só docstring), changelog.d/lote-coment-prepush.md, tests/test_forge.py, tests/test_testes_tocados.py. Primeira rodada (sem delta). Referência de comportamento: `.githooks/pre-push` da develop 739b0b0, igual no head (`git diff --quiet 739b0b0 bcdb3b9 -- .githooks/`).

## Garantido por ferramenta
- `python3 -m unittest tests.test_forge.PrePushSoOsAfetados tests.test_testes_tocados.NaoEPortao` em bcdb3b9: `Ran 8 tests`, `OK`.
- Os mesmos dois arquivos de teste sobre a árvore de 739b0b0 (worktree em `$TMPDIR`): `FAILED (failures=4)`; caem os subtestes `tests/config.json`, `só acrescenta pareceres` e `docs/reviews/` do teste do README e o teste da docstring. Os subtestes `bin/forge-testes` e `.githooks/` passam já na base (ver A3).
- `python3 -I bin/forge-testes --listar docs/reviews/x.md README.md`: `forge-testes: dirigido (...)` (base do A2).
- Teto M14: `git diff --numstat --no-renames 739b0b0...bcdb3b9` dá 19 linhas de código e teste (`bin/forge-testes` 3+3, `tests/test_forge.py` 7, `tests/test_testes_tocados.py` 6). Dentro do teto, sem `hooks/` nem `PROTEGIDOS`.
- Suíte completa não rodada (brief: só os testes do item); fica no CI do PR. `docs/engineering/praticas.md` não existe no Forge; checklist da skill por leitura. Achados recorrentes (PA-7): lista vazia.

## Achados
- A1 (bloqueante) README.md:68 · requisito (E1: "cita todos os casos"): a lista de quem cai na suíte inteira omite árvore suja, push de mais de uma ref, HEAD diferente do commit enviado e falta de origin/develop (pre-push:251-259); o QA 002a6f3 A1, que o cartão cita, pede árvore suja e mais de uma ref
- A2 (bloqueante) README.md:68 · requisito (alinhar ao pre-push), texto falso: "outro arquivo, modelo _*, ref nova ou prova ausente cai na suíte inteira"; em melhoria/* o so_parecer falho cai no elif dirigido (pre-push:270-273) e roda só os afetados; dizer que segue a regra acima; omite ameacas/ e aceites/
- A3 (recomendado) tests/test_forge.py:299 · os subtestes `bin/forge-testes` e `.githooks/` passam na base (o parágrafo já citava o script e `.githooks/pre-push --status`); cobrar `tests/config.json ou` junto de `.githooks/` ou outro termo que só o caso novo traz
- A4 (recomendado) bin/forge-testes:27 · a docstring segue dizendo que review e QA rodam a suíte inteira, contra o corte 1 da ACELERA-RODADA (autor e revisores rodam só os testes do item; a suíte inteira fica no pre-push e no CI) e o A2 do review 61b82c2; alinhar na mesma volta

## Parecer
Reprovado. A docstring cita a M8 de 2026-10-24 e diz que ela substitui a de 2026-10-23, conforme a decisão do dono; o caso novo do auto-julgamento (`bin/forge-testes`, `tests/config.json`, `.githooks/`, pre-push:265) e a falha do plano (pre-push:266-268) estão certos no README. Dois pontos do README não batem com o hook, e o cartão existe justamente para isso:

- A1 · README.md:68 · a frase "caem na suíte inteira:" lê como lista fechada, mas o `dirigido()` também devolve 1 com mais de uma ref (251), com HEAD diferente do sha enviado (256), com árvore suja ou com arquivo novo não rastreado (257) e sem `refs/remotes/origin/develop` (259). Sugestão: acrescentar "push de mais de uma ref, árvore suja ou HEAD diferente do enviado e falta da base `origin/develop`", ou trocar a lista por "qualquer coisa fora de um envio simples de uma `melhoria/*` com a árvore limpa e o plano dirigido, como". Classe: requisito. Bloqueia.
- A2 · README.md:68 · a ordem do hook é `if so_parecer` → `elif dirigido` → suíte inteira (270-277). Quando o caminho só de parecer falha (outro arquivo, ref nova, prova ausente, modelo `_*`) numa `melhoria/*` cujo diff contra a base só tem caminhos com regra, quem roda é o dirigido, e não a suíte inteira: `forge-testes --listar docs/reviews/x.md README.md` dá `dirigido`, e o `dirigido()` não olha o sha remoto, então a ref nova também vai para ele. O texto também deixa de fora `docs/security/ameacas/` e `docs/security/aceites/` (pre-push:229). Sugestão: "qualquer outro arquivo, modelo `_*`, `docs/security/ameacas/` ou `aceites/`, ref nova ou prova ausente sai do caminho curto e segue a regra acima". Classe: requisito (o texto descreve um comportamento que o hook não tem). Bloqueia.
- A3 · tests/test_forge.py:299 · recomendado. O teste não fixa frase frágil (termos curtos, recorte do parágrafo pelo marcador em negrito), mas dois dos cinco termos já estavam no texto antigo e não cobram o caso novo.
- A4 · bin/forge-testes:27 · recomendado. A frase "Review, QA, o CI do PR e o caminho para a main rodam a suíte inteira" é anterior ao diff (só foi reorganizada), mas o review 61b82c2 A2 pediu o alinhamento aos cortes junto com a M8. O teste `test_docstring_cita_a_decisao_m8_de_2026_10_24` cobra `M8`, `2026-10-24` e `substitui` soltos, o que basta para a decisão.

Checklist: escopo sem nada a mais (só texto e os testes); `R-NEUTRO` sem termo novo; `R-CUSTO` nada pago; regras invioláveis preservadas; fragmento em `changelog.d/`; um commit em Conventional Commits em português. Segurança: só texto, parecer próprio já na branch (0861257). Devops: sem pipeline no diff.
