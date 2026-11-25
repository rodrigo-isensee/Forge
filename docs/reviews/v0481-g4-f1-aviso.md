---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: 3682aebaa39bbb2607e45db5d699cc5e7293a65b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E7.12, #885, G4 F1: modo aviso por grupo, só infra; classe C), revalidação por delta

Delta lido (`forge-check parecer delta docs/reviews/v0481-g4-f1-aviso.md`): intervalo `d92b3a07..3682aeba`, no domínio `hooks/conformidade.py`, `tests/test_hooks.py`, `tests/mutantes/v0481-g4-f1-aviso.json`, `tests/mutantes/v0481-g4-f1-aviso-2.json`, `docs/hooks.md` e `changelog.d/v0481-g4-f1-aviso.md`. Os pareceres de QA e segurança do intervalo não são do meu domínio. Parecer anterior: reprovado em `d92b3a07` (E7.8) por A1.

## Conferência do delta
- **A1 (FIFO) resolvido.** `hooks/conformidade.py:1526-1532`: o `open` agora usa `O_NONBLOCK`, só grava se `S_ISREG(fstat)` e fecha o fd no `finally`, como pedi. Em `barrar` (`:1585-1590`), o texto da recusa é montado antes, o registro vem depois e o `PrazoVencido` (BaseException, `hooks/_comum.py:2829`, que o `except Exception` do registro não pega) é engolido só ali, seguido do `bloquear`. A recusa já não depende da gravação, nem por travamento nem por prazo. Defesa em duas camadas: o FIFO não prende, e o que ainda prender não troca a decisão.
- **A2 (git no caminho da recusa) resolvido.** `:1517-1522`: sem `hook._run`, a pasta sai de `diretorio_comum` (só disco, `hooks/_comum.py:153`), sem `copia_principal`. Se `comum` for None, `comum / "forge"` lança TypeError, que o `except Exception` absorve: sem registro, mesma decisão.
- **Caminho do aviso** (`:1581-1584`): o registro fica sem o `except PrazoVencido`. Hoje nenhum grupo está em `avisar` e esse caminho libera de qualquer forma, então nada muda na decisão. Ver A3 para a F4.
- **Testes:** `python3 -m unittest tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro`: 11 testes, OK (1,6 s). A `RecusaComFifoNoRegistro` roda o hook de verdade (`producao=True`) nas duas sessões, com os três comandos, e confere o código 2 e a regra original. Os testes de FIFO usam um alarme próprio (`Travou`, BaseException), e por isso não prendem a suíte.
- **Mutantes (V2):** `bin/forge-mutante --processos 1` nas duas specs, em `3682aeba`: M1 a M16 morreram. Os mutantes M3 a M6 e M9, redeclarados para as linhas novas, também morreram. `bin/forge-mutante --cobertura --base d92b3a07`: as linhas de guarda novas (1518, 1520 e 1529) estão cobertas por M14, M15 e M12, e a 1527 por M9 e M11.
- **Guardas do diff:** `if run is None`, a condição da cópia principal, `if not run.is_dir()`, `S_ISREG`, `except PrazoVencido` e o `if` do texto simples têm um mutante cada e um teste do ramo de falha. Nenhum teste lê o texto da fonte.
- **Tamanho (H1):** o delta tem cerca de 25 linhas de código, e o item continua dentro do teto.
- **Suíte inteira:** fica no CI do #885, run 45543065244 no head `3682aeba`, com as partes da suíte em andamento quando este parecer foi escrito. Não rerrodei.
- **Doc:** `docs/hooks.md` ganhou o item "Modo por grupo", com a decisão antes da gravação, o `O_NONBLOCK`, o arquivo regular e a medida lendo só `fonte: conformidade`, o que fecha a parte de `docs/hooks.md` do A4.

## Achados
- A3 (recomendado) hooks/conformidade.py:1583 · o aviso vai ao stderr com saída 0, que o Claude Code não mostra ao agente; e o registro do aviso (:1582) fica sem o except PrazoVencido. Resolver os dois na F4, antes de um grupo ir a avisar.
- A4 (recomendado) docs/propostas/g4-fatias.md:36 · a definição de recusa falsa ainda conta toda linha com barrado e alvo nulo, inclusive a do vigia, sem fonte. O docs/hooks.md já filtra fonte=conformidade; alinhe a proposta e o comando de medida a esse filtro.
- A5 (recomendado) tests/test_hooks.py:4368 · a RecusaComFifoNoRegistro mede o gasto mas não o confere. Sem o O_NONBLOCK, a recusa sai certa só depois do prazo de 3 s e o teste passa; só o M11, no teste unitário, pega o caso. Afirmar gasto abaixo de 1 s cobre o hook real.

## Sondas
- S1 · sessão do Forge (CLAUDE_PROJECT_DIR e cwd num clone com .claude-plugin), FIFO em .forge/run/comandos.jsonl, `git push origin feature/x:main` · espera: código 2, R-MAIN · obtido: código 2 em 0,2 s, R-MAIN (na base d92b3a07, a mesma sonda: código 0, liberado)
- S2 · a mesma sessão e FIFO, `git push --force origin feature/x` · espera: código 2, R-VERIFY · obtido: código 2 em 0,1 s, R-VERIFY (na base d92b3a07: código 0)
- S3 · a mesma sessão e FIFO, `git commit --no-verify -m x` · espera: código 2, R-VERIFY · obtido: código 2 em 0,1 s, R-VERIFY
- S4 · sessão do projeto (.forge/versao), FIFO, os três comandos · espera: código 2 com a regra original · obtido: código 2 em 0,1 s, R-MAIN, R-VERIFY, R-VERIFY (na base d92b3a07: R-CONFORMIDADE, erro interno, nos dois push)
- S5 · as duas sessões, sem FIFO, os três comandos · espera: código 2 e uma linha por recusa · obtido: código 2 e 3 linhas no comandos.jsonl, com fonte, grupo e alvo

## Parecer
**Aprovado.** O A1 bloqueante está corrigido e provado pelo hook real nas duas sessões (S1 a S4). O A2 também foi resolvido. Os mutantes M11 a M16 morrem. A3, A4 e A5 são recomendados e viram cartão depois do merge. O merge espera o CI verde do #885 no head `3682aeba`.
