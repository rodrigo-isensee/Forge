---
tipo: revisao-seguranca
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: 70ba6c614bdaa0f2dae1c3aff051ba53a2b97f43
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: lote-coment-prepush

Revalidação por delta (volta 1) do lote COMENTARIOS-PREPUSH (pedido LOTE-COMENT-PREPUSH-REV, E2.1) sobre `bcdb3b9..70ba6c6`, com o diff total `739b0b0...70ba6c6` relido no que toca controle do Forge. Parecer anterior: `0861257` (aprovado, head `bcdb3b9`).

## Gatilhos
Controles do Forge: o texto descreve o filtro do pre-push (`.githooks/pre-push`, `bin/forge-testes`). Conferido por `git diff -U0 bcdb3b9..70ba6c6 -- bin/forge-testes` que o script mudou só nas linhas 27 e 28, dentro da docstring do módulo (que fecha na linha 30); `.githooks/` e `scripts/` não estão no diff `739b0b0..70ba6c6`. O comportamento do filtro é o da base; sem sonda. Os dois testes novos (`tests/test_forge.py:303`, `tests/test_testes_tocados.py:432`) só leem texto (README e `ast.get_docstring`), sem rede, subprocesso nem escrita.

Conferência do texto contra o hook da branch: `README.md:68` agora lista, para o caminho só de parecer, todas as saídas de `so_parecer` (`.githooks/pre-push:210-235`): mais de uma ref, ref que não é branch, ref nova, árvore suja, HEAD diferente do commit enviado, prova ausente, arquivo fora dos quatro diretórios, modelo `_*`, `docs/security/ameacas/` e `docs/security/aceites/` (linha 229). A frase "em `melhoria/*` esse envio segue a regra acima" bate com a ordem `so_parecer` → `dirigido` → suíte inteira (`.githooks/pre-push:270-283`), e "sem `origin/develop`" com `.githooks/pre-push:259-260`. O README não descreve menos controle do que o hook aplica. A docstring de `bin/forge-testes:25-29` tira a instrução de review e QA rodarem a suíte inteira, conforme o corte 1 da decisão do dono de 2026-10-24, e mantém a suíte inteira no CI de todo PR.

Delta dos achados de `0861257`: Recomendação 1 (ameacas/ e aceites/ ausentes no README) resolvida em `README.md:68`. Recomendação 2 (`.githooks/pre-push:236` cita 2026-10-23) segue aberta, fora do lote por decisão técnica do Jarvis (07:51), e vira A1 abaixo.

## Achados
- A1 (recomendado) .githooks/pre-push:236 · comentário ainda cita "EST-M8 (decisão do dono, 2026-10-23: A)"; sem caminho de ataque (comentário); corrigir no cartão COMENTARIOS-PREPUSH restante, que já toca o hook

## Detalhe dos achados
- A1 (informativa). Evidência: `.githooks/pre-push:236`. Caminho de ataque: nenhum, é comentário. Correção mínima: citar M8 de 2026-10-24. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e do hook, `git diff -U0`, e os testes do item (`python3 -m unittest tests.test_forge.PrePushSoOsAfetados tests.test_testes_tocados.NaoEPortao`, 10 testes, OK). Lacuna: `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH; o delta é só texto e teste de texto, sem segredo nem workflow, e o CI do PR repete a bateria.
