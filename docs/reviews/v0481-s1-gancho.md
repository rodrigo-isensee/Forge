---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-gancho
commit: e4b6bc4a8417bdb90338f24687c99219b19142fe
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E20.27, #920, hook estado, merge da develop)

Revalidação por delta (H3, `R-REVIEW`) do #920, `5d558642..e4b6bc4a`: o merge da `develop` (`346a7860`, com o #921 do `ordens_teto`) sobre o head aprovado. Conflito resolvido em `hooks/hooks.json` (campo `description`) e `bin/forge-testes` (linhas do `MAPA`).

## Escopo conferido
- Delta lido: `forge-check parecer delta docs/reviews/v0481-s1-gancho.md`, escopo sem o que veio da base; no domínio só `bin/forge-testes`, `docs/adr/0003-hooks-deterministicos-e-silenciosos.md`, `docs/hooks-fixtures.md`, `docs/indice-forge.md`, `hooks/hooks.json` e `tests/pesos-d4.json`.
- Revisado não mudou: o patch da branch antes do merge (`git diff 3c833f3f 5d558642`) e depois (`git diff 346a7860 e4b6bc4a`) têm as mesmas linhas `+/-`, salvo a linha `description` de `hooks/hooks.json`, que é a resolução do conflito.
- `git show --cc e4b6bc4a`: a `description` junta o texto do `ordens_teto` (develop) e o do `estado` (branch); no `MAPA` de `bin/forge-testes` ficam as duas linhas lado a lado, `hooks/(decisao\.py|estado\.py|hooks\.json)` e `hooks/(ordens|ordens_teto)\.py`; `tests/pesos-d4.json` traz `test_hook_estado` e `test_hook_ordens_teto`.
- Os dois hooks seguem registrados: `hooks/hooks.json:59` (`ordens_teto.py`, PreToolUse) e `hooks/hooks.json:368` (`estado.py`, UserPromptSubmit); o JSON é válido (`json.tool`).
- Tamanho (H1): nenhuma linha de código nova além da resolução.

## Verificações
- ci: e4b6bc4a8417bdb90338f24687c99219b19142fe verde
  - `gh pr checks 920`, runs 45917071630 (CI) e 45917071689 (Catraca), ambos com `headSha` `e4b6bc4a`: suíte 3.12 e 3.14 (partes 1 a 5), instalação, passos, verificações longas, teto de pulados, árvore provada e `catraca` verdes; só `bateria` e `bateria (pareceres)` falham, à espera do parecer no head (anotação: `Process completed with exit code 1`, sem outra causa).
- Testes dos arquivos do conflito (com `flock`): `python3 -m unittest tests.test_hook_estado tests.test_hook_ordens_teto tests.test_hook_decisao tests.test_testes_tocados`: `Ran 246 tests ... OK (skipped=1)`.
- Mutantes: nenhuma guarda nova no delta; os do pedido seguem os da volta anterior.
- Shell: nenhum arquivo de shell no delta.

## Parecer
Aprovado. O merge só traz a `develop` e resolve os dois conflitos mantendo os dois hooks (`ordens_teto` e `estado`) na descrição, no registro e no mapa de testes; o patch revisado não mudou. Os recomendados A1 e A2 da volta anterior seguem para cartão depois do merge.
