---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-oraculo-hermetico
commit: 7b2c4cbde05813f9b68efa53cbf39631870b5cc9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481, testes herméticos do oráculo (E27.7, volta 1)

Volta por delta sobre `2affeefe..7b2c4cbd` (`forge-check parecer delta`). No domínio: `tests/test_oraculo_sempre_atual.py`. Fora do domínio, lidos só porque fecham o A1: `tests/test_sempre_atual.py` (`ProcReal`) e `tests/sem_claude_ancestral.py`. Produção (`bin/`, `hooks/`, `scripts/`, `.github/`) não muda.

## Gatilhos
Gatilhos: nenhum de produção; o delta toca o oráculo da guarda que adia a atualização com Claude vivo (RD4, RD11), revisto por pedido do dono.

## Achados

## Sondas

## Detalhe dos achados
**A1 (rodada anterior, recomendado): resolvido.** `tests/test_sempre_atual.py:83-108` (`ProcReal`) lança um processo real de nome `claude` (link para o interpretador, sem dublê nem `skip`), chama `processos_de_interesse()` com o `PROC` de produção e afirma, sem variável de ambiente escolhendo o que testar: `proc_coerente() == nosso` (a verdade lida à parte, em `/proc/self`) e, no nosso namespace, `(duvida, detectado) == (False, True)`; fora dele, `duvida`. É a correção mínima pedida, com uma asserção a mais (a coerência). Mutantes, raciocinados sobre `bin/forge_sempre_atual.py:148-196`: `PROC=/proc-nao-existe` morre no CI (`nosso` verdadeiro, `proc_coerente()` falso, linha 103) e sobrevive no sandbox, onde `nosso` é falso (sonda abaixo, como previsto); `proc_coerente` sempre verdadeiro morre também no sandbox (linha 103); "sempre dúvida" e "nunca acha o claude" morrem no CI (linha 105). O oráculo roda com `--proc` e não lê o `PROC` de produção, então nenhum outro teste mascara o resultado.

**O que aperta.** (1) A integração com o procfs real (o `readlink` de `self`, o `comm` dado pelo nome do link no `exec`, o `cwd` mágico, o `st_uid`) volta a ter teste, agora próprio e não como efeito colateral do oráculo. (2) `tests/test_oraculo_sempre_atual.py:480-481`: o `vivo()` volta a afirmar que a árvore do teste tem o processo vivo, com `comm` e `cwd` certos e `poll()` nulo; um preparo quebrado deixa de passar como "sem claude" (falso verde da guarda). (3) `tests/sem_claude_ancestral.py:53-54`: `--proc` sem pasta e script sai com o uso em vez de `IndexError`.

**O neutro.** Produção não muda; nenhuma costura nova (o `ProcReal` usa o módulo como está, sem troca de atributo). O docstring do oráculo troca o "limite conhecido" pela indicação de onde está a prova do `/proc` real. O processo do teste é morto no `addCleanup` e a pasta temporária é apagada; o `sleep(60)` limita o resíduo se a limpeza falhar.

**O que afrouxa.** Nada no delta. Ressalva sem achado: a detecção positiva só é provada onde o `/proc` é do nosso namespace (o CI); no sandbox a prova é a dúvida, que é o comportamento de produção ali.

## Riscos aceitos e ferramentas
Sem risco aceito. Rodado aqui, na cópia em `7b2c4cbd`: `tests.test_sempre_atual.ProcReal`, OK (sandbox, ramo dúvida). Sonda do mutante `PROC=/proc-nao-existe` em `~/.forge-contrib/wt/_sec-v0481-proc-mutante.sh`: no sandbox, `nosso namespace: False` e o teste passa (sobrevive, como previsto; a morte é no CI). CI do head `7b2c4cbd` (PR 922): as 10 partes da suíte (3.12 e 3.14), a instalação, os passos, as verificações longas, a catraca e a árvore verdes, com `ProcReal` rodando no `/proc` do nosso namespace (o ramo que mata o mutante); vermelhos só `bateria (pareceres)` e o agregador `bateria`, pelo parecer de review `reprovado` anterior (R-REVIEW) e por este parecer desatualizado: portão que este parecer e o novo de review fecham, sem defeito de código. Ferramentas de varredura de segredo, SAST e workflow ausentes no PATH (lacuna); o delta não toca segredo, workflow nem dependência.
