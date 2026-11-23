---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 3e653044fb25104f5a56198d03da6d22602c0a50
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 E90.15 (SIEG-G1 G1.2a, `forge-check autorizacao gravar`, volta E90.14)

Revalidação por delta do parecer aprovado bafa19a2 (head 9f833cd6). Li o `forge-check parecer delta`: `revalida: sim`, `bin/forge_autorizacao.py` mudou depois do parecer. Intervalo `175ee8df..3e653044`, 5 arquivos, 16+/16-: `bin/forge_autorizacao.py`, `changelog.d/v0479-sieg-g1-gravar.md`, `docs/adr/0018-autorizacao-do-dono-gravada.md`, `tests/mutantes/v0479-sieg-g1-gravar-8.json` e `tests/test_autorizacao_gravar.py`.

## Conferido
- **Decisão 3a do dono (23/11 16:53):** o delta desfaz só o ajuste de pontuação do A2 do review 44b4a481. `bin/forge_autorizacao.py:319` volta a `(?![\w.])` nos dois alvos, idêntico ao de antes do A2 (`d7c1a53b:bin/forge_autorizacao.py:311`). Nenhuma outra linha de código mudou; o item só aperta: "pr 5." e "0.47.3." voltam a nascer pendentes.
- **Teste:** `test_ponto_final_logo_depois_do_alvo_deixa_pendente` espera `pendente` nos três casos ("PR 5.", "0.47.3.", "pr 5.1"); é teste de comportamento pelo `gravar`, não leitura da fonte.
- **Mutantes:** M58 e M59 (`-8.json`) invertidos para o sentido novo (o mutante reintroduz o `(?!\w|\.\w)`). `bin/forge-mutante --processos 1 --ids M58,M59` em 3e653044: os dois morreram em `:319`.
- **Docs:** ADR 0018 (`:56-57`) registra que o ponto final depois do alvo segue pendente pela decisão 3a; o fragmento do changelog perde a frase do A2. Nenhuma referência restante ao teste antigo nem ao trecho desfeito no domínio do item (o `(?!\w|\.\w)` de `tests/mutantes/v047-jargao-medida-3.json` é de `hooks/meta.py`, fora do item).
- **Testes:** `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao`: 49 testes, OK. A suíte inteira roda no CI.
- **Tamanho (H1):** 1 linha de código; dentro do teto.
- **A1 anterior (recomendado, travessão e aspas curvas):** fora deste delta; segue como cartão depois do merge.

## Parecer
Aprovado (`R-REVIEW`). O delta cumpre a Decisão 3a: só desfaz o A2, com teste do ramo pendente e os dois mutantes mortos.
