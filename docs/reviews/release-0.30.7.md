---
tipo: review
contrato: 1
pedido: release-0.30.7
branch: melhoria/release-0.30.7
commit: b1e11946c1e33df5f44823a27c10c28461c2d793
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: release-0.30.7

## Achados

## Parecer
Aprovado. Diff de 8 arquivos (2fdda20...b1e1194, um commit `chore(release): versão 0.30.7`), só release: sem código nem teste, fora do teto M14. Nada fora de `CHANGELOG.md`, `changelog.d/`, `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`.

- CHANGELOG: a seção `[0.30.7] - 2026-10-29` traz 5 entradas (2 Alterado: t6t3-mensagem, vel-p1p10; 3 Corrigido: hk3-parecer-texto, lote-0307-a, t1-conf-escopo), uma por fragmento que a develop 2fdda20 tinha em `changelog.d/`, cada linha idêntica à do fragmento (conferido com `grep -xF` linha a linha), sem perda nem duplicata; `[Não publicado]` fica vazio.
- `changelog.d/` sem os 5 fragmentos (a pasta deixa de existir; `bin/forge-changelog novo` a recria com `mkdir(exist_ok=True)`).
- Versão 0.30.7 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`; nenhuma referência a 0.30.6 em `.json`, `.py` ou `.sh` fora dos docs; numeração conforme a decisão do dono de 2026-10-24 ("C").
- Checagens citadas: `python3 -m unittest tests.test_changelog` OK (46 testes, 1 skip); `bin/forge-check docs` sem erro.
- PA-7 (`docs/engineering/achados-recorrentes.md`) conferido: nenhuma classe repetida neste pedido, sem linha AR nova.
- QA tem parecer próprio, em paralelo (`R-QA`).
