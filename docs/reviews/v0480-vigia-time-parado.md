---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-time-parado
commit: dc0af82caa3d7e6be2497ce8e7a51447b87e384a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0480-vigia-time-parado

Etapa E105.12, revalidação (H3, R-REVIEW) do parecer da E105.7 (head b13b7016, aprovado) depois do merge da `develop` (a1cb5786, com a emenda da ADR 0003 do #788). Delta lido: `forge-check parecer delta docs/reviews/v0480-vigia-time-parado.md`, intervalo `b13b7016..dc0af82c`, escopo sem o que veio da base; no domínio só `tests/pesos-d4.json`. Fora do delta nada foi relido. `git diff a1cb5786 dc0af82c -- tests/pesos-d4.json` é uma linha (`"test_vigia_parado": 0.1`): o arquivo é o da `develop` mais o peso do teste do item, JSON válido. Sem mudança em `hooks/`, `tests/test_vigia_parado.py`, nos mutantes do item nem em `docs/hooks.md` desde b13b7016.

## Achados
- A1 (recomendado) tests/test_vigia_parado.py:8 · `import subprocess` sem uso (vem da E105.7); tire-o junto do cartão do A4 anterior.
- A2 (recomendado) docs/adr/0003-hooks-deterministicos-e-silenciosos.md:91 · a emenda, agora na base, põe a mudança do laço de `tests/test_hooks.py` (830-837) e as fixtures do item 7 "no PR do vigia"; esta branch não as tem (A4 anterior, cartão). Faça aqui ou ajuste a emenda para o cartão.

## Parecer
Aprovado no head dc0af82c.

Condição de integração da E105.7 cumprida: a emenda da ADR 0003 (item 7) entrou na `develop` (a1cb5786, ancestral do head), e o código e o doc do item têm âncora.

Provas (head dc0af82c; a suíte inteira fica no CI do PR):
- `forge-check parecer delta`: no domínio só `tests/pesos-d4.json`.
- `git diff a1cb5786 dc0af82c -- tests/pesos-d4.json`: `+  "test_vigia_parado": 0.1,`.
- `python3 -I -c "import json;json.load(open('tests/pesos-d4.json'))"`: ok.
- `git merge-base --is-ancestor a1cb5786 dc0af82c`: verdadeiro.
