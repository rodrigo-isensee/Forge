---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: a4d1287031926560dc2742f125b5456cccaa149a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 prazo-forge (#888, classe C)

Escopo: diff `5fb8e328..a4d12870` lido: `hooks/_comum.py` (`recusa_no_prazo`, `prazo_vencido` com vigia próprio de 0,5 s), `hooks/conformidade.py` (`ARQUIVO_ESPECIAL`, `especial_no_git`), 6 fixtures `fifo-*`, `tests/test_hooks.py`, `tests/test_hooks_volta_propriedades.py`, `tests/mutantes/v0481-prazo-forge.json`. Não há parecer anterior da branch. Clone: `/root/.forge-contrib/wt/v0481-prazo-forge-qa` (clone comum: a worktree não pôde ser criada no sandbox).

## Achados
- A1 (recomendado) hooks/_comum.py:2877 · Sonda: sem marcador, PreToolUse, sessão não vigiada e registro lento (0,8 s > 0,5 s) após o prazo de 3 s: recusa rc 2 (0 s: libera). Antes liberava; só ocorre com a máquina já lenta. Cartão: separar o estouro do registro da decisão da sessão.
- A2 (recomendado) hooks/conformidade.py:132 · `python3 -c "import os;os.mkfifo('.git/f')"` libera nas duas sessões (igual à base; fora de mkfifo/mknod). O FIFO no .git por outro escritor segue só no corte de prazo.
- A3 (recomendado) hooks/conformidade.py:1776 · `mkfifo $TMPDIR/p` (alvo opaco, fora do .git) agora recusa nas duas sessões: fricção legítima, pelo desenho (alvo opaco). Vale a nota na mensagem ou no doc.

## Critério → teste → resultado
O pedido não tem `CA-n`; as obrigações vêm do brief (E7.25) e da medida do pedido.
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Prazo vencido na sessão do Forge recusa a linha marcada (R-CONFORMIDADE), com a causa | `test_sessao_do_forge_recusa_so_a_linha_marcada` | marcado True/None recusa, False e sem marcador não; PostToolUse libera; fora do Forge decide a sessão | passou |
| FIFO no commondir e no gitdir de worktree: push na main, `--force`, `--no-verify` recusam, Forge e projeto, hook real | `test_fifo_no_commondir_e_no_gitdir_recusa_nas_duas_sessoes` (16 casos, raiz na worktree e na principal) | FIFO no lugar de `commondir`/`gitdir` | passou |
| Registro e sessão sob vigia de 0,5 s; o que não termina recusa | `test_sessao_que_nao_se_decide_recusa`; `SondaS1ComRelogioFalso`, `VigiaAgentesPesado` (armados `[prazo, 0, 0,5, 0]`) | PrazoVencido e OSError | passou |
| mkfifo/mknod com alvo no .git recusam nas duas sessões | `test_fixtures_fifo` (6 fixtures, mínimo 6 afirmado) | .git, curinga, opaco, `cd .git`, fora do .git libera | passou |

## Cenários e resultado real
- Rodado só o item: `python3 -m unittest tests.test_hooks.PrazoVencidoNaSessaoDoForge tests.test_hooks.SondaS1ComRelogioFalso tests.test_hooks_volta_propriedades.VigiaAgentesPesado`: `Ran 9 tests in 13.172s OK` (a suíte inteira roda no CI do PR; não citado aqui o `.verde` local).
- Vermelho antes do verde (cópia em `$TMPDIR` com `hooks/_comum.py` e `hooks/conformidade.py` da base e os testes do head): `PrazoVencidoNaSessaoDoForge`: `Ran 4 tests, FAILED (failures=18, errors=2)`; os quatro testes novos caem na base (FIFO, fixtures, marcado True/None, sessão que não se decide). Obs.: `forge-testes --vermelho` foi iniciado sem módulo e roda tudo; não usado como prova.
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-prazo-forge.json --processos 2`: M1 a M8 `morreu` (M4 por erro do teste declarado, que passa sem o mutante); nenhum sobrevivente. `--cobertura --base 5fb8e328...`: as 6 linhas de guarda mudadas (`_comum.py` 2860, 2875, 2879, 2882; `conformidade.py` 1776, 2511) têm mutante declarado; nenhuma sem cobertura.
- Hook real, 19 linhas nas duas sessões (sondas em arquivo, base × head, só o código de saída): na base todas as linhas `mkfifo`/`mknod` com .git, curinga, `cd .git`, `command`, `env`, caminho absoluto, `--mode`, `--`, `-Z` e opaco saíam 0; no head saem 2 com R-CONFORMIDADE. Push na main (`git -C . push origin feature/x:main`, R-MAIN), `--force` e `--no-verify` (R-VERIFY) recusam igual nos dois. `mkfifo /tmp/x` e `mkfifo build/pipe` liberam. Diff base × head: só trocas 0 → 2; nada que barrava deixou de barrar.
- Vigia de 0,5 s sob carga: a sonda com registro simulado de 0,8 s mostra recusa indevida (A1) só onde a sessão não vigia e a linha não tem marcador, e só com o prazo de 3 s já vencido; nas sessões vigiadas já recusava. Falha fechada pela ADR 0003; por isso recomendado, não bloqueante.
- Sem acessibilidade nem E2E (hook de linha de comando).
