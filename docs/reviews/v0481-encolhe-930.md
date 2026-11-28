---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-encolhe-930
commit: 27641d2acf103093952590e8c9f6a23461d2864d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E46.2, PR #936, encolher o #930)

1ª rodada completa, revisor (não o autor). Base `8855671d`, head revisado `27641d2a` (3 commits: d112b138, cda492f2, 27641d2a).

- ci: 27641d2acf103093952590e8c9f6a23461d2864d verde

## O que foi conferido
- **Escopo (item 1):** o diff faz o que a E46.1 e a decisão técnica de 2026-11-27 09:03 pedem, nem mais: saem `destino_opaco`, `checar_texto`, `colada_em_vigor`, `ref_inteira`, `NOMES_EM_VIGOR` e o ramo `MOTIVO_EM_VIGOR in o_que` do `barrar`; o erro interno que cita a entrada passa a fechar só sem `command` (Write, Edit, MultiEdit, NotebookEdit). Ficam `na_raiz_em_vigor`, `caminho_barrado` e o caminho literal do Bash (19 fixtures `-bloqueia`). O A18 (denyWrite versionado) não entra aqui, como decidido.
- **Cobertura pelo ambiente:** nesta estação, `/proc/self/mountinfo` mostra `ro` em `.githooks`, `.git/hooks`, `.devcontainer`, `.devcontainer.json` e `.claude-plugin` da raiz, como as S21-S25 de `docs/security/v0481-hook-raiz-forge.md`, que o `docs/hooks.md` cita.
- **Código morto:** nenhum resto. `glob_casa`, `palavra_juntada`, `valores_da_palavra`, `textos_do_valor`, `fim_do_opaco` e `juntar_continuacoes` seguem usados em outros pontos; `MOTIVO_EM_VIGOR` segue em `caminho_barrado`; `EM_VIGOR_NO_TEXTO` segue no erro interno.
- **Erro interno:** `entrada.get` já era chamado antes no mesmo `except`; o novo `not entrada.get("command")` não abre exceção nova.
- **Referências soltas:** `git grep` dos nomes das fixtures e das specs apagadas não acha nada fora do histórico.
- **Tamanho (H1):** só remoção de código de controle (−66 em `hooks/conformidade.py`); dentro do teto.
- **Afrouxa:** título com `[afrouxa-regra]` e rótulo `afrouxa-regra` no PR; a `catraca` está verde no head.
- **Commits (item 9):** três, Conventional Commits em português, cada um coerente; fragmento `changelog.d/v0481-encolhe-930.md` troca o do #930, que ainda não saiu em release.
- **Testes afetados e mutantes (rodados por mim no head):** `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` OK (29 liberam, 19 bloqueiam). `forge-mutante --base 8855671d tests/mutantes/v0481-hook-raiz-forge-3.json`: RX1, RX2 e RX3 morreram (hooks/conformidade.py:4582). `--ids RF1` em `v0481-hook-raiz-forge.json`: morreu (hooks/conformidade.py:4315). `--conferir --base`: trechos no lugar. `--cobertura --base`: a única guarda nova ou mudada (4582) está coberta por RX1-RX3; o resto é linha apagada e spec removida, que é o próprio afrouxamento, aceito pela catraca com o rótulo.

## Achados
- A1 (recomendado) tests/test_hooks.py:2932 · as fixtures de grafia que ficaram como `-libera` (variavel-de-for/read-scripts, review-s1..s4, colada-por-aspas, tmpdir, variavel-*-libera) passam agora sem guarda a exercer, e a mensagem do assert ainda as descreve como cobertura; cartão para apagá-las ou reescrever a mensagem.
- A2 (recomendado) .claude/settings.json:23 · o `denyWrite` versionado ainda não lista as cinco entradas da raiz; na estação sem a configuração local, a grafia do Bash fica sem guarda (limite escrito em docs/hooks.md:69). É o A18, já com o dono: só registro.

## Parecer
Aprovado. O encolhimento remove a guarda por grafia do Bash que o sandbox do SO cobre, mantém a guarda de Write/Edit/MultiEdit e do caminho literal, e o fechamento em erro interno fica restrito às ferramentas que não passam pelo sandbox. Mutantes da linha mudada mortos, teste afetado verde, CI do head verde fora `bateria`, `bateria (pareceres)` e `catraca` (esta, verde também). Os dois achados são recomendados e viram cartão depois do merge.
