---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: b3312958a3c27f9c13a94853647bc357a59ca27b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E1.6 (revalidação da volta E1.5, guardas da conformidade no clone)

Escopo lido: só o delta de `forge-check parecer delta` (b0ffec81..b3312958): changelog.d, docs/hooks.md, hooks/agentes.py, hooks/conformidade.py, 6 specs de mutantes, tests/test_conformidade_verde.py. Fora do domínio, nada relido.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1063 · `alvos_do_tar` só lê `f` e `C` com o valor na palavra seguinte; o valor colado (`-C.git/forge/run`, `-cf.git/forge/run/agentes.json`), que o GNU tar aceita (S3), passa com rc 0 (S1, S2) e reabre o A2 da segurança. Tome o resto da palavra após `f`/`C` como valor e ponha os dois casos no teste.

## Sondas
- S1 · `tar -xf docs/a.tar -C.git/forge/run` (jarvis, clone temporário) · espera: rc 2 · obtido: rc 0
- S2 · `tar -cf.git/forge/run/agentes.json docs` (jarvis) · espera: rc 2 · obtido: rc 0
- S3 · GNU tar real: `tar -cfa.tar src && tar -xfa.tar -Cdst` · espera: recusa da forma colada · obtido: cria a.tar e extrai em dst/src/f
- S4 · controle: `tar -x -fdocs/a.tar -C .git/forge`, `tar -C .git/forge -xf docs/a.tar`, `--dir=.git/forge`, `chmod -R 000 .git`, `chmod --reference=docs .git/forge/run`, `find .git/forge/run -execdir rm {} ;` · espera: rc 2 · obtido: rc 2

## Revalidação dos achados anteriores
- A1 (meu, docs/hooks.md:73): fechado; o parágrafo diz a guarda no clone para todo papel, o config da raiz e os atos por opção.
- A2 (meu, tests/test_conformidade_verde.py:311): fechado; `chmod 000 .git/forge/run/agentes.json` entrou na lista e o comentário cobre J1 a J15.
- A1 da segurança (teto da worktree): fechado no código; `pasta_da_config` lê o config da raiz da sessão quando as duas são clones do Forge, e `ConfigDaWorktreeNoClone` prova teto, piso, ritmo e peso. O `lancar` usa `hook.config()` pelo cache que o `ler_config` do `principal` enche (M11 guarda a chamada).
- A2 da segurança (find, tar, chmod): find e chmod fechados; tar aberto pela forma colada (A1 acima).

## Verificação
- Testes do delta: `python3 -m unittest tests.test_conformidade_verde.EstadoDoAgentesNoClone tests.test_conformidade_verde.ConfigDoTetoNoClone tests.test_conformidade_verde.ConfigDaWorktreeNoClone`: 16 testes, OK.
- Mutantes: `bin/forge-mutante --processos 1` nas specs -3 a -6 (M15 a M45) e na v047-hook-estado-ilegivel-2: 39 de 39 morreram. `--cobertura --base b0ffec81`: toda condição mudada coberta; `--conferir`: M3, M6 e M7 da z075 com trecho duplicado em hooks/agentes.py, já na develop 4182a6b9, fora deste item.
- Tamanho (H1): 106 linhas a mais em hooks/ no delta, somadas às cerca de 48 da E1.2; perto do teto de 150, sem PR para conferir a linha `teto:`.
- Suíte inteira: não rodada (brief: sem suíte local); sem PR, CI do head não citável.

## Parecer
Reprovado: um bloqueante, A1, com defeito provado (S1 a S3). A guarda nova do tar deixa passar a forma de opção curta com valor colado. O resto da volta fecha os quatro achados, com teste de comportamento e mutante morto por guarda. A correção é local em `alvos_do_tar`; a revalidação lê só o delta.
