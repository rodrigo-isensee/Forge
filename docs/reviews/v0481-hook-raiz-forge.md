---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: e4998443f6eea0ef08c43dbbb9b35627f13582b0
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E37.11, HOOK-NAO-PROTEGE-RAIZ-DO-FORGE, PR #930, volta 2)

Revalidação por delta (H3) do head `e4998443`, sobre o parecer aprovado de `10c1b834`. O critério é o mesmo das rodadas anteriores, sem `critério mudou:`.

## Achados
- A1 (recomendado) hooks/conformidade.py:4317 · vem da 1ª rodada e fica fora do delta: `rm -rf .` na raiz passa (rc 0), como no projeto. Não é regressão; vira cartão para os dois.
- A2 (bloqueante) hooks/conformidade.py:4354 · o A9 fica aberto com resto: só os textos precisos contam, e a variável que nasce de `for` ou `read` passa na raiz (S1, S2), contra docs/hooks.md:69. O ramo do .git usa os largos ([1], linha 2063). Trocar `[0]` por `[1]` fecha S1 e S2, e as 51 fixtures continuam verdes.
- A3 (recomendado) tests/test_hooks.py:2930 · os mínimos seguem 17 e 28, e o lote tem agora 19 e 32. Suba-os para que as 6 fixtures novas não sumam em silêncio.

## Sondas
- S1 · fixture na raiz do Forge (cwd na raiz, devops-engineer): `for d in .githooks; do printf x > $d/pre-push; done` · espera: rc 2 · obtido: rc 0
- S2 · fixture na raiz do Forge (cwd na raiz, devops-engineer): `read d <<< .githooks; printf x > $d/pre-push` · espera: rc 2 · obtido: rc 0

## Parecer
**Reprovado** pelo A2. O delta fecha S7 e S8 da segurança e a substituição com resto, mas o caminho sem valor calculado usa um texto mais estreito que o do mesmo hook para o `.git`. Com isso, o pre-push da raiz ainda pode ser gravado numa chamada só.

- **Delta lido** (`forge-check parecer delta docs/reviews/v0481-hook-raiz-forge.md`, intervalo `10c1b834..e4998443`):
  - `hooks/conformidade.py`: `GuardaDaProva.destino_opaco` passa a usar `fim_do_opaco`, e o ramo sem valor usa `textos`.
  - As 6 fixtures novas: `raiz-forge-s7-*`, `raiz-forge-s8-*`, `raiz-forge-substituicao-com-resto-*`, `raiz-forge-variavel-sem-valor-com-resto-*`, `raiz-forge-wt-s7-*` e `raiz-forge-wt-s8-*`.
  - As specs `v0481-hook-raiz-forge-3.json` (RD1, RD2 e RD4 realinhados) e `-4.json` (RD7 e RD8).
  - `docs/hooks.md` e o fragmento do changelog.
- **A2, detalhe:**
  - `textos_do_valor` devolve `(precisos, largos)`. Os largos acrescentam a linha inteira só quando a variável nasce de outro jeito (`for`, `read`) ou de uma função da linha.
  - Com `[1]`, `printf x > $TMPDIR/y; cat .githooks/pre-push` segue livre, porque o `TMPDIR` não nasce na linha. A fixture `raiz-forge-variavel-com-resto-cita-githooks-libera` passa e mata o RD7.
  - Rodei a troca localmente com as duas sondas como fixtures: `test_fixtures_da_raiz_do_forge` deu OK. Depois reverti a troca e apaguei as sondas.
  - A correção é do autor. Peça S1 e S2 como fixtures `-bloqueia` e um mutante que volte `[1]` para `[0]`.
- **Escopo (item 1):** fora o A2, o delta faz o que o A9 pede (S7 e S8 recusam na raiz e são livres na cópia de `wt/`). Os docs descrevem o comportamento, e o limite da substituição com resto saiu da lista de limites, o que está correto.
- **Tamanho (H1):** o delta tem 3 linhas de código, e o item fica dentro do teto.
- **Guardas e mutantes (item 7):** cada linha de guarda mudada tem mutante.
  - `bin/forge-mutante --processos 1` na `-3` e na `-4`, sob a trava `trava-teste-a.lock`: RD1 a RD8, RX1 e RX2 morreram.
  - As fixtures exercitam o comportamento sem ler a fonte.
- **Commits (item 9):** `5d6583f8` (fix) e `e4998443` (test) seguem Conventional Commits em português, com o cartão e a etapa.
- **CI (check-runs do `e4998443`):** verdes a suíte 3.12 e a 3.14 (partes 1 a 5), `instalação`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `teto de pulados` e `árvore já provada na develop`. Ficam de fora `bateria`, `bateria (pareceres)` e `catraca`. O head do PR (`7a21fd2d`) só acrescenta o parecer do QA.
- ci: e4998443f6eea0ef08c43dbbb9b35627f13582b0 verde
