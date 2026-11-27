---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: aa3472135b21f0539c3047d1e31fe6718a17bced
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E37.15, HOOK-NAO-PROTEGE-RAIZ-DO-FORGE, PR #930, volta 3)

Revalidação por delta (H3) do head `aa347213`, sobre o parecer reprovado de `e4998443` (A2 bloqueante, A3 recomendado). O critério é o mesmo das rodadas anteriores, sem `critério mudou:`.

## Achados
- A1 (recomendado) hooks/conformidade.py:4317 · vem da 1ª rodada e fica fora do delta: `rm -rf .` na raiz passa (rc 0), como no projeto. Não é regressão; vira cartão para os dois.

## Parecer
**Aprovado.** O A2 e o A3 estão fechados. O A1 segue recomendado e vira cartão depois do merge.

- **Delta lido** (`forge-check parecer delta docs/reviews/v0481-hook-raiz-forge.md`, intervalo `e4998443..aa347213`):
  - `hooks/conformidade.py:4355`: o ramo com resto e sem valor calculado passa de `textos_do_valor(caminho)[0]` para `[1]`, os textos largos, como o ramo do `.git`. A docstring foi atualizada.
  - As 4 fixtures novas: `raiz-forge-variavel-de-for-githooks-bloqueia`, `raiz-forge-variavel-de-read-githooks-bloqueia` (são as minhas S1 e S2 da volta 2), `raiz-forge-variavel-de-for-scripts-libera` e `raiz-forge-variavel-de-read-scripts-libera` (fora de entrada em vigor, livres).
  - `tests/mutantes/v0481-hook-raiz-forge-4.json`: o RD7 e o RD8 foram reancorados no texto novo, e o RD9 (`[1]` volta a `[0]`) é novo.
  - `tests/test_hooks.py:2930`: os mínimos passam a 21 e 34.
  - `docs/hooks.md:69`: diz que a variável de `for` e `read` conta a linha inteira, e que a falha fechada vale também na cópia de `wt/`.
  - Os pareceres de QA e segurança da volta 2.
- **A2 (fechado):** é exatamente a troca pedida. As duas sondas viraram fixtures `-bloqueia`, e o mutante RD9 as prova. A fixture `raiz-forge-variavel-com-resto-cita-githooks-libera` (`$TMPDIR`) segue verde, como a docs promete.
- **A3 (fechado):** o lote tem 55 fixtures, 21 que liberam e 34 que recusam (contei os JSON com a descrição `HOOK-NAO-PROTEGE-RAIZ-DO-FORGE (`). Os mínimos batem com o lote exato.
- **Tamanho (H1):** o delta tem 1 linha de código, e o item fica dentro do teto.
- **Guardas e mutantes (item 7):** a única linha de guarda mudada (4355) tem três mutantes.
  - Rodei `bin/forge-mutante --processos 1 tests/mutantes/v0481-hook-raiz-forge-4.json` em `aa347213`, sob `trava-teste-a.lock`: RD7, RD8 e RD9 morreram (rc 0).
  - Rodei `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` sob a mesma trava: OK.
- **Commits (item 9):** `aa347213` (fix) segue Conventional Commits em português, com o cartão e a etapa.
- **CI (check-runs do `aa347213`):** verdes a suíte 3.12 (partes 1 a 5), `teto de pulados (python 3.12)`, `instalação (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)` e `árvore já provada na develop`. Ficam de fora `bateria`, `bateria (pareceres)` e `catraca`. Os heads depois dele (`5a13627b`, `0d3a1bd7`) só mexem em `docs/security/` e `docs/qa/`.
- ci: aa3472135b21f0539c3047d1e31fe6718a17bced verde
