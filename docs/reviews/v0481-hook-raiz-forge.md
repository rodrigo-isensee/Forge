---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 3c1bd3823c82f5383b9df5e289bf7889d4774e97
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E37.23, HOOK-NAO-PROTEGE-RAIZ-DO-FORGE, PR #930, volta 5)

Esta é a revalidação por delta (H3) do head `3c1bd382`, sobre o parecer reprovado de `1644a83f`. O critério é o mesmo das rodadas anteriores, sem `critério mudou:`.

## Achados
- A1 (recomendado) hooks/conformidade.py:4339 · vem da 1ª rodada e fica fora do delta: `rm -rf .` na raiz passa (rc 0), como no projeto. Não é regressão; vira cartão para os dois.

## Sondas
- S1 · `for f in a b; do printf x > $f.log; done`, cwd numa cópia `wt/x` · espera: rc 0 · obtido: rc 0 (fixture `raiz-forge-review-s1-colada-log-wt-libera`)
- S2 · a mesma linha com cwd na raiz da sessão · espera: rc 0 · obtido: rc 0 (`raiz-forge-review-s2-colada-log-raiz-libera`)
- S3 · `printf x > ${TMPDIR}x/y`, cwd em `wt/x` · espera: rc 0 · obtido: rc 0 (`raiz-forge-review-s3-tmpdir-colado-wt-libera`)
- S4 · `for n in 1 2; do printf x > saida-$n.txt; done`, cwd em `wt/x` · espera: rc 0 · obtido: rc 0 (`raiz-forge-review-s4-saida-n-wt-libera`)

## Parecer
**Aprovado.** O A2 da volta 4 está resolvido, e o delta não abre bloqueante novo.

- **Delta lido** (`forge-check parecer delta docs/reviews/v0481-hook-raiz-forge.md`, intervalo `1644a83f..3c1bd382`):
  - `hooks/conformidade.py`: `NOMES_EM_VIGOR`, `ref_inteira` e `colada_em_vigor` (:4178-4198), o uso em :4381-4383 e a docstring.
  - As fixtures S13, S14 e S15, as quatro sondas do review, a colada por aspas sem entrada e o `$TMPDIR` entre aspas.
  - Os mutantes: RD12 a RD16 são novos (`-5.json`), e RD4 e RD11 foram reancorados (`-3.json` e `-4.json`).
  - Os pisos em `tests/test_hooks.py:2930-2931`, que agora são 27 liberam e 40 recusas.
  - `docs/hooks.md:69`.
- **A2 resolvido:**
  - O componente só recusa quando, lido como curinga, casa uma entrada de `EM_VIGOR_NA_RAIZ`. Por isso `*.log`, `saida-*.txt` e `*x` passam, e `*s` e `*ooks` recusam.
  - A docs agora descreve esse alcance e dá os exemplos livres.
  - A mensagem de recusa volta a ser verdadeira.
- **As quatro sondas rodadas de novo:** viraram fixtures `-libera`, e comparei os comandos e o cwd com os de S1 a S4: são os mesmos. Todas passam em `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge`, rodado sob `trava-teste-a.lock` (OK, 13 s).
- **Sondas extras temporárias** (fixtures removidas, nada commitado), todas com o valor de `$(cat l)` e cwd na raiz:
  - Recusam como deveriam: `$d\s/pre-push`, `"${d}"s/pre-push`, `${d}ooks/pre-push` e `$d'n'/plugin.json`.
  - Passam como deveriam: `"$f".log` e `"out$n"/y`.
  - Não achei desvio.
- **Mutantes:** rodei `bin/forge-mutante` em `3c1bd382`, sob a trava.
  - `-5.json`: RD12 a RD16 morreram (:4192, :4194, :4197, :4382 e :4183).
  - `-3.json` e `-4.json`: RD1 a RD11 morreram, inclusive os reancorados RD4 e RD11.
  - Cada linha de guarda nova tem o seu mutante.
- **Leitura:**
  - `ref_inteira` monta a regex com `nome` vindo de `\w+`, sem risco de injeção na regex.
  - O laço sobre os prefixos é linear no tamanho do nome.
  - A docstring explica a leitura do `$ds`.
- **Tamanho (H1):** o delta tem 25 linhas de código.
- **Commits (item 9):** `f20c312a` (fix) e `3c1bd382` (test) seguem Conventional Commits em português, com a etapa.
- **CI (`gh pr checks 930` no `3c1bd382`):**
  - Verdes: a suíte 3.12 (partes 1 a 5), `teto de pulados (python 3.12)`, `instalação (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)` e `árvore já provada na develop`.
  - Ficam de fora `bateria`, `bateria (pareceres)` e `catraca`.
- ci: 3c1bd3823c82f5383b9df5e289bf7889d4774e97 verde
