---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/suite-tempo-vivo
commit: 5c06712475d096d89f2cf27098fb6b12265ff5c5
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Code review: tempo de cada unidade ao vivo e resumo no sinal (suite-paralela, E23.23)

Escopo: pedido v0457, E23.24 (`R-REVIEW`), classe C (`forge-check pr`: sensível da catraca, `scripts/suite-paralela.py`). Li o diff inteiro, `git diff 8b5a44d5..5c067124`: um commit, 3 arquivos (`scripts/suite-paralela.py` 61+3, `tests/test_suite_paralela.py` 58+0, o fragmento). O `5e6ce60b` que veio depois é só o parecer de segurança (`docs/security/suite-tempo-vivo.md`), fora do meu escopo; o código no head da branch é o revisado.

## Achados
- A1 (bloqueante) scripts/suite-paralela.py:532 · classe C sem spec de mutantes: `forge-mutante --cobertura` lista 5 guardas novas sem mutante (532 `not completo`, 538, 540, 564, 572) e não há `tests/mutantes/v0457-suite-tempo-vivo.json`; falta também teste do ramo de linha parcial (532). Classe AR-1/AR-2
- A2 (recomendado) scripts/suite-paralela.py:542 · o `print` informativo no stderr pode levantar BrokenPipeError/EIO e derrubar o orquestrador no meio do `esperar` (antes só imprimia no fim); sugestão: `try/except OSError` em volta das duas linhas de `TemposAoVivo` (542 e 557)
- A3 (recomendado) scripts/suite-paralela.py:300 · o arquivo `.tempos` do filho é aberto e nunca fechado; sugestão: fechar no `finally` junto do `stopTestRun`
- A4 (recomendado) scripts/suite-paralela.py:309 · a duração é medida duas vezes (`duracoes[nome]` e a linha `fim`); sugestão: gravar `duracoes[nome]` para o log e o resumo final darem o mesmo número

## Sondas
- S1 · `bin/forge-mutante --cobertura --base 8b5a44d5ffd509c8c63d3e9f68dbef20071c7d3e` na worktree · espera: nenhuma linha `sem mutante` · obtido: 5 linhas `sem mutante` (suite-paralela.py:532, 538, 540, 564, 572)

## O que conferi
- **stdout e última linha:** o diff só acrescenta `print(..., file=sys.stderr)`; nenhum `print` de stdout mudou nem mudou de lugar. `FAILED (interrompida)` continua saindo depois do aviso de interrupção. O pre-push decide pelo código de saída (`"${suite[@]}" 9>&- >&2`, `rc`) e os jobs do CI rodam `python3 scripts/suite-paralela.py` pelo código; o `bin/forge-testes` usa `scripts/suite-partes.py`, que chama `sp.esperar(filhos, inicio)` sem `tempos` (padrão `None`), então nada muda lá. Os filhos do `suite-partes` passam a gravar `p<i>.saida.json.tempos` na pasta temporária, que é apagada com ela.
- **Caminho do sinal (sem órfão):** `imprimir_rodando()` roda antes do `encerrar(filhos)`, com os sinais já em `SIG_IGN`. Se a impressão falhar, o `encerrar` é pulado; sondei isso com o stderr do orquestrador fechado e SIGTERM: o pai sai com 120 e o filho de `test_b` morre mesmo assim, pelo `vigiar_pai` (`scripts/suite-paralela.py:275`, o filho mata o próprio grupo quando o pai some). Sem órfão; o risco que sobra é o A2.
- **Testes:** `python3 -m unittest` dos dois testes novos mais `test_sigterm_encerra_o_grupo_de_cada_processo` dá `Ran 3 tests … OK`. Os novos leem o stderr ao vivo, provam que a linha de `test_a` sai com a suíte rodando e que `rodando test_b` sai no SIGTERM sem `test_a`. A espera de 0,5 s no teste do sinal não decide nada (a regex aceita `0.0`, e `imprimir_rodando` relê o arquivo antes de imprimir). Sem leitura de texto da fonte; o ambiente vem do `Brinquedo` (AMBIENTE limpo, `CI` e `GITHUB_*` tirados).
- **Teto M14:** `git diff --numstat --no-renames 8b5a44d5...5c067124` dá 64 + 58 = 122 linhas de código e teste, abaixo de 150; um comportamento só.
- **Commit:** `feat(suite): …` em Conventional Commits, em português, com fragmento em `changelog.d/`.
- **Classe recorrente:** A1 é da classe AR-1 (lista de mutantes incompleta) e AR-2 (ramo de guarda sem teste); a linha AR fica para o QA ou para o PR seguinte, porque o brief limita este commit ao parecer.

## Parecer
**Reprovado** no `5c067124`, só pelo A1. O comportamento está certo: a linha por unidade sai no stderr com flush, o resumo de quem rodava sai no sinal, e veredito, ordem, stdout e código de saída não mudam. Falta o que a classe C exige para guardas novas: a spec `tests/mutantes/v0457-suite-tempo-vivo.json` com um mutante por linha (532, 538, 540, 564, 572) e um teste do ramo de linha parcial (`not completo`, por exemplo um `.tempos` com `inicio\tx\t1` sem `\n` que não pode abrir a unidade). A2 a A4 são recomendações e não devolvem a entrega; o A2 sai barato no mesmo commit.
