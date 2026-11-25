---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-perfil-fifo
commit: 517f80fd166ae8230ef6dd5af7991324975ead0e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E7.20, code review por delta do #886, de 8dfe968f a 517f80fd, classe C)

Escopo: revalidação pelo delta. `forge-check parecer delta docs/reviews/v0481-perfil-fifo.md`: intervalo `8dfe968f..517f80fd`, no domínio `changelog.d/v0481-perfil-fifo.md`, `hooks/_comum.py`, `tests/mutantes/v0481-perfil-fifo-2.json` e `tests/test_hooks.py`; `revalida: sim` (o parecer anterior, E7.16, era reprovado pelo A1). O delta é um commit (E7.19), com 12 linhas líquidas de código em `hooks/_comum.py` (`ler_marca_do_git` e o uso dela em `diretorio_comum`); o item segue dentro do teto H1 e com um comportamento só.

## O que foi conferido
- **A1 do review anterior (pulo novo):** o `@unittest.skipUnless(hasattr(os, "mkfifo"))` saiu da `RecusaComFifoNoPerfil`. Catraca do #886 no 517f80fd (job 138979586409): sem linha de pulos nem de enfraquecimento de `tests/test_hooks.py`; as duas linhas vermelhas são só o rótulo `afrouxa-regra` do dono para `hooks/_comum.py` e `hooks/conformidade.py`, que não é achado deste review. Resolvido.
- **A1 da segurança e A3 do review anterior (`.git` FIFO):** `ler_marca_do_git` abre com `O_NONBLOCK`, confere `S_ISREG` no `fstat` do mesmo descritor (sem corrida entre conferir e ler), lê até 4096 bytes (o `PATH_MAX` do Linux) e fecha no `finally`; o especial levanta `OSError` e o UTF-8 inválido, `UnicodeDecodeError` (um `ValueError`), os dois já tratados como `None` em `diretorio_comum`. Os outros chamadores (`hooks/agentes.py:768`, `hooks/_comum.py:197` e `2707`) só ficam mais estritos: marca que não é arquivo regular deixa de resolver, o mesmo desfecho do `.git` ilegível. `.git` em link simbólico para arquivo regular continua valendo (sem `O_NOFOLLOW`, como antes com `read_text`).
- **Sondas de novo (hook real, script fora do repositório, `sonda_v0481_e720.py` no scratchpad):** FIFO em `.forge/perfil`, sessões do Forge e do projeto: push na main, `--force`, as cadeias com `rebase`, `reset --hard` e `clean -fd` e `commit --no-verify` saem com 2 em 0,2 s pela regra certa (`R-MAIN`, `R-VERIFY`), igual ao 8dfe968f; no projeto, as cadeias com `reset --hard` e `clean -fd` seguem recusadas pelo prazo em 3,2 s (A2, já conhecido). FIFO no `.git` com perfil iniciante: no projeto, as seis recusam em 0,2 a 0,3 s com o texto simples (no 8dfe968f, 3,3 s e texto técnico: o A3 anterior fechou); no Forge, `R-CONFORMIDADE` em 0,2 s porque o `.git` não se resolve. Nada que a base recusa passa a liberar.
- **Mutantes:** `bin/forge-mutante tests/mutantes/v0481-perfil-fifo-2.json` no 517f80fd: M8 (`O_NONBLOCK`, `hooks/_comum.py:156`) e M9 (`S_ISREG`, `hooks/_comum.py:158`) morreram. Uma guarda mudada por mutante, cada uma com teste de comportamento do ramo de falha (FIFO vazio no `.git` da worktree; FIFO com o conteúdo certo no `gitdir`, que só o `S_ISREG` barra).
- **Testes:** `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil`: 7 testes, verdes em 1,6 s. O auxiliar `worktree()` tira a duplicação entre os três testes de worktree. Suíte do CI no 517f80fd: as 10 partes estavam pendentes na leitura; o merge espera o CI verde, sem rerrodar aqui.
- **Commit e changelog:** Conventional Commits em português, corpo com o motivo e a origem de cada correção; o fragmento ganhou a linha do `diretorio_comum`.

## Achados
- A2 (recomendado) hooks/_comum.py:2728 · `Hook.iniciante` (`perguntar`, escrita do perfil, meta.py:355) segue com `git rev-parse` e `read_text`: FIFO no perfil faz `reset --hard` e `clean -fd` no projeto esperarem 3,2 s e recusarem pelo prazo (sondado de novo no 517f80fd). Cartão: delegar a `perfil_iniciante`.
- A4 (recomendado) hooks/conformidade.py:1577 · o `com_trecho` roda fora do `try`: se o alarme vence ali, o `PrazoVencido` chega ao `prazo_vencido`, que libera na sessão do Forge. Janela curta e já existente, sem gatilho provado; montar o texto técnico dentro do `try` ou desarmar o vigia no `barrar`.

## Parecer
Aprovado no 517f80fd. O A1 (pulo novo) foi resolvido e a catraca não acusa mais pulo; o A3 (`.git` lido com `read_text`) foi fechado pelo `ler_marca_do_git`, com M8 e M9 mortos e as sondas sem espera nem troca de regra. A2 e A4 seguem recomendados e viram cartão depois do merge. Para integrar faltam o CI verde, os outros pareceres no head e o rótulo `afrouxa-regra` do dono.
