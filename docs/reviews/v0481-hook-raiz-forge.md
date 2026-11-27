---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: baffa052cf425f0bc0eaed636e681c52b299b372
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E37.3, HOOK-NAO-PROTEGE-RAIZ-DO-FORGE, PR #930)

1ª rodada completa do head `baffa052`, contra a base `6edd59d2`. Diff: 19 linhas de código em `hooks/conformidade.py` (dentro do teto H1, um comportamento só), 19 fixtures `raiz-forge-*`, `test_fixtures_da_raiz_do_forge`, 4 mutantes, `docs/hooks.md` e o fragmento do changelog.

## Achados
- A1 (bloqueante) tests/hooks/conformidade/estadoclone-rm-git-bloqueia.json:23 · CI vermelho (test_hooks.py:913, fatia 1): `rm -rf .git` no clone agora cai antes na guarda nova (`.git` contém `.git/hooks/`) com o motivo da entrada `.git`, e a fixture espera o de `.git/forge/`. Recusa segue; ajuste a fixture ou a ordem, com o motivo no commit.
- A2 (bloqueante) docs/hooks-fixtures.md:136 · CI vermelho (test_indice_fixtures.py:31, :42 e :157): o índice não lista o prefixo novo `raiz-*`; rode `scripts/indice-fixtures.py` e commite o índice gerado.
- A3 (recomendado) hooks/conformidade.py:4317 · a pasta-mãe só casa com rel diferente de `.`: `rm -rf .` na raiz (ou o caminho absoluto da raiz) apaga `.githooks/` e o devcontainer.json e passa (rc 0). O projeto tem a mesma lacuna (controle rc 0), então não é regressão; cartão para os dois.

## Sondas

## Parecer
**Reprovado**, só pelo CI vermelho do head (A1 e A2), que vai na volta única (E37.5). A lógica está correta e enxuta.

- **Escopo (item 1):** faz o que o E37.1 pede. A guarda entra no `barrar` do `GuardaDaProva`, então só recusa o que o projeto já recusaria (a leitura segue livre por construção). A recusa vale quando o alvo resolvido fica na raiz da sessão ou na cópia principal, e a cópia de `wt/` segue livre. `scripts/` fica fora: o `postStartCommand` da develop roda o script de um clone raso da `main`, não o da raiz (fixture `raiz-forge-sonda-s1-scripts-libera`).
- **Legibilidade e docs (itens 3 e 2):** constante `EM_VIGOR_NA_RAIZ` com o cartão, docstring do módulo e `docs/hooks.md` atualizados, com o limite do alvo opaco declarado. Fragmento `changelog.d/` presente.
- **Testes e guardas (itens 7 e 4 do papel):** as 4 guardas mudadas têm mutante declarado. `bin/forge-mutante --processos 1 tests/mutantes/v0481-hook-raiz-forge.json`: RF1, RF2, RF3 e RF4 morreram. `--cobertura --base 6edd59d2`: as 3 condições do diff aparecem como cobertas. O teste afirma um mínimo de 7 fixtures que liberam e 12 que barram, e as fixtures exercitam comportamento, sem ler a fonte.
- **Sondas do revisor:** escritas pelo Write numa cópia própria, fora do commit, e rodadas pelo `test_fixtures_da_raiz_do_forge`. Na raiz da sessão do Forge, `mv .githooks velho`, `sed -i` no devcontainer.json, `cd .githooks && echo x > pre-push`, `ln -sf /bin/true .githooks/pre-push` e `rm -rf <raiz>/.devcontainer <raiz>/.githooks` (rodado de outra pasta) deram todos rc 2. `rm -rf .` deu rc 0, e a mesma entrada num projeto também deu rc 0 (A3, não bloqueia).
- **CI (`gh pr checks 930`, head baffa052):** em vermelho estão a suíte 3.12 e a 3.14, partes 1/5 (A1) e 2/5 (A2). As partes 3 a 5, `instalação`, `bateria (passos)` e `bateria (verificações longas)` estão verdes. Sem CI verde não há a linha `- ci:` e o parecer não aprova.
- **Commits (item 9):** um commit, Conventional Commits em português, com o cartão e a etapa.
