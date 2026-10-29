---
tipo: review
contrato: 1
pedido: t6t3-mensagem
branch: melhoria/t6t3-mensagem
commit: 0c2ef9ca9453736aecefad78a48c284dc599025e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Code review: mensagem ao conferente lida do brief e mensagem do modo entrega (T6T3-MENSAGEM, E1, E2, E4 e E5)

Escopo: pedido T6T3-MENSAGEM-REV, E1.1 (`R-REVIEW`). Rodada 1, diff lido inteiro: `git diff d14a7133eb608f3b02298931e76ddc8ccfe55c20...0c2ef9ca9453736aecefad78a48c284dc599025e` (5 commits, `f52c12d` a `0c2ef9c`). O E3 (rodada -REV numa mensagem) ficou para o pedido T6T3-RODADA (decisão técnica de 2026-10-29 11:53) e não é cobrado aqui. Segurança (E2.1, `docs/security/t6t3-mensagem.md`, aprovado com 3 recomendações) e QA (E3.1) rodam em paralelo; não os refaço.

## Achados
- A1 (bloqueante) bin/forge-check:4611 · `--entrega` tira o `Desde:` só das linhas `conferida` e ignora a base fixada pelo dono mais recente; o `forge-check entrega` só aceita a mais recente das duas (linha 74, `desde_valido`) e o conferente reprova a entrega certa. Use `bases_do_pedido(...)[-1]` e teste o caso
- A2 (recomendado) agents/conferente.md:70 · o bloco de entrada do modo entrega ainda mostra `Arquivo:` relativo e Worktree, Branch, Base, Base-sha e Desde numa linha; a mensagem gerada traz o caminho absoluto e um campo por linha. Alinhe o modelo à saída do comando

## Parecer
**Reprovado**, por A1.

A1, defeito de comportamento provado. Sonda em raiz sintética (`$TMPDIR/tech-lead-t6t3-mensagem/sonda_dono.py`, sobre o `Cenario` do teste novo, pedido com linha `DECISÃO DO DONO`): Histórico com `entrega conferida aaaa…` e depois `base do delta fixada pelo dono dddd…` dá `rc 0` e `Desde: aaaa…`; só com a linha do dono, a mensagem sai sem `Desde:`. O `agents/conferente.md` manda usar a última `conferida` ou, se mais recente, a base do dono, e o `forge-check entrega` (`bin/forge-check:1027-1030`, `desde_valido`) responde `escopo: --desde sem conferência anterior` para o sha mais antigo. Como o `agents/jarvis.md` agora manda enviar a saída inteira e sem editar, o Jarvis não tem como corrigir à mão: a entrega certa sai `não cumpriu` (primeiro caso) ou o delta vira a branch inteira, perdendo a base que o dono fixou (segundo caso). Correção: `Desde:` = último item de `bases_do_pedido` (as duas origens; a função já exige a `DECISÃO DO DONO` para a do dono), e um teste com a linha do dono depois da `conferida` e outro só com a do dono. O texto do jarvis.md ("o sha40 da última linha `conferida`") acompanha.

Lido e sem defeito:
- E1: a etapa vem da linha `Etapa:` do cabeçalho do brief (`ETAPA_DO_CABECALHO`, só antes da primeira seção); `--etapa` diferente sai rc 2 com a etapa certa; igual passa; brief sem `Etapa:` mantém o comportamento antigo. O `Arquivo:` do modo brief já sai absoluto (sonda: `Arquivo: /tmp/.../docs/briefs/pedido-sintetico-dev-exemplo-1.md`).
- E2: Branch, Base, Base-sha e Etapa do cabeçalho do brief; `--worktree` absoluto e existente, passado por `recusa_do_campo`; `--anterior`, `--ref` e `--parecer` recusados; hash do mesmo buffer impresso. As recomendações de segurança (A1 a A3 de `docs/security/t6t3-mensagem.md`) ficam com o security-engineer; não as repito.
- E4: `agents/jarvis.md` e `agents/conferente.md` descrevem a etapa do brief e a mensagem de entrega (fora o modelo de A2).
- E5: teste novo `tests/test_mensagem_conferente.py` (5 casos) e 11 mutantes em `tests/mutantes/t6t3-mensagem.json`; `bin/forge-testes` e `tests/test_testes_tocados.py:61` são consequência do módulo novo (decisão técnica de 2026-10-29 11:53). Fragmento `changelog.d/t6t3-mensagem.md` presente.

Ferramentas: testes do item `python3 -m unittest tests.test_mensagem_conferente tests.test_testes_tocados` → `Ran 86 tests ... OK` (rodado aqui, carga 2,51). Mutação: do autor e do QA (V2); não refeita.

Teto (M14): `git diff --numstat --no-renames d14a713...0c2ef9c` nos arquivos que contam (`bin/forge-check` 35+3, `bin/forge-testes` 1+1, `tests/test_mensagem_conferente.py` 65+0, `tests/test_testes_tocados.py` 1+1) = 107 linhas, dentro de 400 e do teto de 150 do lote; sem `hooks/` nem `PROTEGIDOS`.

Commits: 5, Conventional Commits em português, um por item do brief. PA-7 (`docs/engineering/achados-recorrentes.md`, AR-1 a AR-9) conferido: nenhuma classe repetida; A1 é classe nova neste pedido, sem linha AR.
