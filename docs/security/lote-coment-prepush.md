---
tipo: revisao-seguranca
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: 1c1d68de42a42eae7f354cb173b1496f441e165e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: lote-coment-prepush

Revalidação por delta (volta 2) do lote COMENTARIOS-PREPUSH (pedido LOTE-COMENT-PREPUSH-REV, E2.1) sobre `70ba6c6..1c1d68d`, pela decisão B do dono de 2026-10-27 08:33 (regra fechada no README e asserção estrutural no lugar do teste de termos soltos). Parecer anterior: `9f56376` (aprovado, head `70ba6c6`).

## Gatilhos
Controles do Forge: o texto descreve o filtro do pre-push (`.githooks/pre-push`, `bin/forge-testes`). Conferido por `git diff --name-only 70ba6c6..1c1d68d` que, fora dos pareceres (`docs/reviews/`, `docs/security/`, `docs/qa/`), só mudaram `README.md` e `tests/test_forge.py`; `git diff -U0 70ba6c6..1c1d68d -- .githooks bin scripts` sai vazio. O comportamento do hook e do filtro é o da base; sem sonda. O teste alterado (`tests/test_forge.py:303`) só lê o README e faz `re.split` sobre uma linha, sem rede, subprocesso nem escrita.

Conferência do texto contra o hook da branch (`README.md:68` contra `.githooks/pre-push:210-283`):
- Afetados: o README restringe os afetados a uma só ref de `melhoria/*`, árvore limpa, HEAD igual ao commit enviado, `origin/develop` presente, todo caminho com regra no mapa e sem tocar `bin/forge-testes`, `tests/config.json` ou `.githooks/`. Cada condição existe em `dirigido` (`.githooks/pre-push:251-267`). O hook exige ainda que `bin/forge-testes` seja arquivo regular (`:255`), que o commit enviado não seja remoção (`:253-254`) e que o `--listar` responda "dirigido" (`:266-267`); o README não cita esses casos um a um, mas "qualquer outro envio roda a suíte inteira" os cobre, e o hook é a fonte declarada (`so_parecer` e `dirigido`). Os três casos do A2 anterior (mais de uma ref, HEAD diferente, árvore suja) agora são condição dos afetados.
- Só parecer: branch já existente, árvore limpa, HEAD igual, árvore remota com prova verde, sem apagar nem renomear, sem `_*`, sem `ameacas/` nem `aceites/`, só os quatro diretórios: cada um em `so_parecer` (`:212-232`). O hook ainda exige uma só ref (`:212`) e o arquivo de prova regular e do próprio usuário (`:218`), mais estritos que o texto. "Fora dessas condições o envio segue a regra de cima" bate com a ordem `so_parecer` → `dirigido` → suíte inteira (`:270-283`).
- Direção: em nenhum caso o README promete controle que o hook não aplica; onde diferem, o hook é o mais estrito e roda mais testes do que o texto indica, sem abrir passagem. O README não descreve menos controle do que o hook aplica em nada que mude o comportamento.

Delta dos achados de `9f56376`: A2 (mais de uma ref, HEAD diferente e árvore suja descritos como afetados) resolvido em `README.md:68`, coberto pela asserção de `tests/test_forge.py:303-317` (as quatro condições na frase dos afetados e as frases antigas proibidas). A1 (`.githooks/pre-push:236` cita 2026-10-23) segue aberto: o hook não está no delta, e o cartão é outro.

## Achados
- A1 (recomendado) .githooks/pre-push:236 · comentário ainda cita "EST-M8 (decisão do dono, 2026-10-23: A)"; sem caminho de ataque (comentário); corrigir no cartão COMENTARIOS-PREPUSH restante, que já toca o hook

## Detalhe dos achados
- A1 (informativa). Evidência: `.githooks/pre-push:236`. Caminho de ataque: nenhum, é comentário. Correção mínima: citar M8 de 2026-10-24. Esforço P. Dono: `tech-lead`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e do hook, `git diff`, e os testes do item (`python3 -m unittest tests.test_forge.PrePushSoOsAfetados tests.test_testes_tocados.NaoEPortao`, 10 testes, OK). Lacuna: `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH; o delta é só texto e teste de texto, sem segredo nem workflow, e o CI do PR repete a bateria.
