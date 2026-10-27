---
tipo: revisao-seguranca
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: bcdb3b9cd07aae4b8d3efd8af274888cd77807f1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: lote-coment-prepush

Revisão do lote COMENTARIOS-PREPUSH (pedido LOTE-COMENT-PREPUSH-REV, E2.1) sobre `739b0b0...bcdb3b9`: README (Suíte do Forge), docstring de `bin/forge-testes`, dois testes de texto e o fragmento do changelog.

## Gatilhos
Controles do Forge: o texto descreve o filtro do pre-push (`.githooks/pre-push`, `bin/forge-testes`). Conferido por `git diff -U0` que `bin/forge-testes` mudou só nas linhas 25 a 27, dentro da docstring do módulo (que fecha na linha 29); nenhuma linha executável do script nem do `.githooks/pre-push` está no diff, então o comportamento do filtro é o mesmo da base e não houve sonda. Os dois testes novos (`tests/test_forge.py:296`, `tests/test_testes_tocados.py:426`) só leem texto (README e `ast.get_docstring`), sem rede, subprocesso nem escrita.

Conferência do texto contra o código da branch: os casos que o README lista para a suíte inteira batem com `.githooks/pre-push:255-267` (ferramenta ausente ou link, diff em `bin/forge-testes`, `tests/config.json` ou `.githooks/`, plano não dirigido) e o caminho só de parecer bate com `so_parecer` (`.githooks/pre-push:210-234`), com a omissão anotada em prosa abaixo. O README não promete menos controle do que o hook aplica.

## Achados

## Detalhe dos achados
Recomendações, sem bloqueio (nenhum defeito de comportamento, requisito ou risco de segurança provado):

- Recomendação 1 (informativa). `README.md:68` lista como queda na suíte inteira do caminho só de parecer "qualquer outro arquivo, modelo `_*`, ref nova ou prova ausente", mas não cita `docs/security/ameacas/` e `docs/security/aceites/`, que `.githooks/pre-push:229` também manda para a suíte inteira (nem mais de uma ref, árvore suja e deleção, `.githooks/pre-push:212-226`). Caminho de ataque: nenhum; o hook é mais estrito do que o texto, o que só pode surpreender quem lê, não abrir passagem. Correção mínima: acrescentar "`docs/security/ameacas/` e `aceites/`" à lista. Esforço P. Dono: `tech-lead`.
- Recomendação 2 (informativa, fora do escopo do lote). `.githooks/pre-push:236` ainda abre com "EST-M8 (decisão do dono, 2026-10-23: A)", o mesmo descompasso que este lote corrigiu na docstring. Sem caminho de ataque (comentário). Correção mínima: citar M8 de 2026-10-24 numa próxima entrega que já toque o hook (tocar `.githooks/` faz o push rodar a suíte inteira). Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff e do hook, `git diff -U0`, e os testes do item (`python3 -m unittest tests.test_forge.PrePushSoOsAfetados tests.test_testes_tocados.NaoEPortao`, 8 testes, OK). Lacuna: `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH; o diff é só texto, sem segredo nem workflow, e o CI do PR repete a bateria.
