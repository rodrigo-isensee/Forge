---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-perfil-fifo
commit: 8dfe968f7cfc0c8240a62136b6af02a49bc6d3df
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E7.16, code review do #886, perfil sem FIFO no texto da recusa, classe C)

Escopo: `5fb8e328..8dfe968f` (1 commit), 35 linhas de código em `hooks/conformidade.py` (`perfil_iniciante` e `Guarda.barrar`), dentro do teto H1 e com um comportamento só; testes `RecusaComFifoNoPerfil`, fixture `trava-prazo-no-perfil-bloqueia-iniciante`, índice de fixtures, `tests/mutantes/v0481-perfil-fifo.json` (M1 a M7) e o fragmento em `changelog.d/`. Primeiro parecer da branch.

## O que foi conferido
- **Correção (lida e sondada):** `perfil_iniciante` acha a cópia principal por `diretorio_comum` (sem `git`), abre o `.forge/perfil` com `O_NONBLOCK|O_NOFOLLOW`, lê só arquivo regular e até 64 bytes; `barrar` engole só o `PrazoVencido` da escolha do texto e a recusa segue pelo `bloquear`. Os ramos de falha (ausente, especial, ilegível) passam à próxima cópia e terminam em experiente, como o `Hook.iniciante`.
- **Sonda FIFO em `.forge/perfil`** (hook real, `como_o_claude_code`, sessões do Forge e do projeto; script da sonda fora do repositório), comparada com a base `5fb8e328`:
  - sessão do Forge: na base, `git push origin feature/x:main`, `git push --force origin feature/x` e as cadeias `git rebase main && git push --force ...:main`, `git reset --hard HEAD~1 && git push ...:main`, `git clean -fd && git push --force ...` saem com 0 em 3,1 s (prazo vencido libera). No head, todas saem com 2 em 0,2 s, com `R-MAIN` ou `R-VERIFY`. `git commit --no-verify` recusa nos dois.
  - sessão do projeto: na base, push na main e `--force` recusam pelo prazo (`R-CONFORMIDADE`, 3,2 s); no head, com `R-MAIN` e `R-VERIFY` em 0,2 s. As cadeias com `git reset --hard` e `git clean -fd` seguem recusadas pelo prazo em 3,2 s (A2).
  - nenhuma linha que a base recusa passa a liberar no head: o item só aperta.
- **Mutantes:** `bin/forge-mutante tests/mutantes/v0481-perfil-fifo.json` no 8dfe968f: M1 a M7 morreram. As guardas mudadas (`if stat.S_ISREG`, `except PrazoVencido`, `if simples and ...`, o `comum.name == ".git"`, o `O_NONBLOCK`, a comparação com `iniciante` e o `texto or`) têm um mutante cada e teste de comportamento do ramo de falha.
- **Testes:** `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil`: 5 testes, verdes em 1,8 s. Suíte do CI do #886 no 8dfe968f: as 10 partes (3.12 e 3.14) verdes; vermelhos a `bateria (pareceres)` (falta o parecer, este) e a `catraca` (A1).
- **Pergunta do brief, o `Hook.iniciante` no `perguntar` e na guarda de escrita do perfil:** não precisa entrar neste item. Sondado com FIFO: na sessão do projeto (vigiada) o `perguntar` e a escrita do perfil esperam os 3 s e recusam pelo prazo, sem liberar nada; na sessão do Forge o `git reset --hard`, o `git clean -fd` e o `gh repo archive` decidem em 0,2 s, e a escrita no `.forge/perfil` espera e libera, o mesmo resultado do perfil experiente em arquivo regular (sonda com `experiente`: 0 em 0,2 s). É falha fechada ou o mesmo desfecho do experiente, sem afrouxar recusa; fica como cartão (A2).
- **Commit:** Conventional Commits em português, corpo com o motivo e a origem (A2 e S3 da segurança no #885). O corpo cita "mutantes M1 a M5"; o arquivo tem M1 a M7 (sem efeito no review).

## Achados
- A1 (bloqueante) tests/test_hooks.py:3610 · o `skipUnless(hasattr(os, "mkfifo"))` sobe os pulos de 38 para 39 e o módulo de controle de (604, 6, 0) para (613, 7, 0): a catraca do #886 fica vermelha por R-CONFORMIDADE. O CI é Linux e o mesmo módulo usa `os.mkfifo` sem pulo (4152): tire o decorador.
- A2 (recomendado) hooks/_comum.py:2716 · `Hook.iniciante` (`perguntar`, escrita do perfil, meta.py:355) segue com `git rev-parse` e `read_text`: FIFO no perfil faz `reset --hard`, `clean -fd`, `gh repo archive` e a escrita do perfil esperarem 3 s e recusarem pelo prazo no projeto. Cartão: delegar a `perfil_iniciante`.
- A3 (recomendado) hooks/_comum.py:165 · `diretorio_comum` lê o `.git` com `read_text`: com `.git` FIFO e perfil iniciante, o push na main no projeto espera 3,3 s e cai no texto técnico (a base dava o texto simples em 0,3 s). A recusa e a regra seguem certas; conferir se o `.git` é arquivo regular antes de ler.
- A4 (recomendado) hooks/conformidade.py:1577 · o `com_trecho` roda fora do `try`: se o alarme vence ali, o `PrazoVencido` ainda chega ao `prazo_vencido`, que libera na sessão do Forge. Janela curta e já existente, sem gatilho provado; montar o texto técnico dentro do `try`, ou desarmar o vigia ao entrar no `barrar`.

## Sondas
- S1 · CI do #886 no 8dfe968f, job catraca 138972112728 · espera: catraca sem pulo novo em tests/ · obtido: `skip/skipIf/skipUnless/expectedFailure em tests/ subiram de 38 para 39` e `tests/test_hooks.py enfraqueceu: (604, 6, 0) para (613, 7, 0)`, saída 1

## Parecer
Reprovado só pelo A1: a correção faz o que o pedido pede, as sondas mostram que push na main, `--force` e `--no-verify` com FIFO no perfil recusam pela regra certa e sem esperar nas duas sessões, e nada que a base barra passa a liberar. A1 (bloqueia): tirar o `@unittest.skipUnless` da linha 3610 de `tests/test_hooks.py`; a volta revalida pelo delta. A terceira linha vermelha da catraca (mudança em `hooks/conformidade.py`) é do rótulo `afrouxa-regra` do dono depois do último push e não é achado deste review. A2 a A4 viram cartão depois do merge.
