---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/suite-tempo-vivo
commit: 076dcc809c9a21f7fab45c4786a03a67a33ebf27
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Code review: tempo de cada unidade ao vivo e resumo no sinal (suite-paralela, E23.23)

Escopo: pedido v0457, E23.24 (`R-REVIEW`), classe C (`forge-check pr`: sensível da catraca, `scripts/suite-paralela.py`). Li o diff inteiro, `git diff 8b5a44d5..5c067124`: um commit, 3 arquivos (`scripts/suite-paralela.py` 61+3, `tests/test_suite_paralela.py` 58+0, o fragmento). O `5e6ce60b` que veio depois é só o parecer de segurança (`docs/security/suite-tempo-vivo.md`), fora do meu escopo; o código no head da branch é o revisado.

## Revalidação por delta (E23.30, 076dcc80)
Delta lido: `forge-check parecer delta docs/reviews/suite-tempo-vivo.md`, intervalo `5c067124..076dcc80`, no domínio `scripts/suite-paralela.py`, `tests/mutantes/v0457-suite-tempo-vivo.json` e `tests/test_suite_paralela.py` (commits `fb58dd04` e `076dcc80`, volta E23.27). Revisor sem participação na entrega. Os pareceres de QA e segurança no intervalo e o `a693aaf4` (segurança, E23.31) ficam fora do meu domínio.

- **A1 resolvido.** As 5 guardas apontadas viraram mutantes mortos na spec nova: 532 → M1 (`not completo`, hoje 533), 538 → M2, 540 → M3, 564 → M4 (hoje 572), 572 → M5 (hoje 580); mais M6 (flush), M7 (`except OSError`) e M8 (posição por linha). `bin/forge-mutante` da spec em 076dcc80: M1 a M8 `morreu`. `--cobertura --base 8b5a44d5` sem nenhuma linha `sem mutante`. O ramo da linha parcial tem teste de comportamento (`TemposAoVivoLogica.test_linha_parcial_nao_abre_unidade_nem_avanca_a_posicao`: sem `\n` não abre a unidade nem anda a posição; completada, abre).
- **M7 vale.** Morreu por erro: sob `except ZeroDivisionError` o `BrokenPipeError` do stderr falso escapa do `informar` e o teste dá erro; o teste existe para provar que "nenhum OSError escapa", então o erro é a falha que a guarda evita, não um acidente do teste.
- **A2 a A4 aplicados.** `informar` com `try/except OSError` nas duas impressões (548–551); `tempos.close()` no `finally` (312); a linha `fim` reaproveita `duracoes[nome]` (309). O resumo do sinal passou para depois do `encerrar` (775–776): com stderr quebrado nenhum filho fica vivo, e o `informar` já não deixa o erro escapar.
- **Posição por linha** (543): avança depois de tratar cada linha; um sinal no meio do laço não perde nem repete linha (M8 e `test_posicao_avanca_por_linha_tratada`).
- **Teste instável:** `termina(p)` lê o resto pelos próprios objetos de arquivo, onde o `readline` do `le_ate` deixou o buffer; o `communicate` lia o descritor e perdia o que já estava no buffer. Correção certa para a causa descrita; os pipes fecham no `finally` (076dcc80) e o `threading.Timer` de 30 s mata o filho em vez de pendurar.
- **Testes dos arquivos tocados:** `TemposAoVivoLogica` (5) mais `Brinquedo.test_sigterm_encerra_o_grupo_de_cada_processo`, `test_linha_por_modulo_sai_antes_do_fim` e `test_sigterm_deixa_o_resumo_de_quem_rodava`: `Ran 8 tests … OK`. A classe nova não roda subprocesso (AR-4 e AR-5 não se aplicam); a spec bate com o head (AR-12).
- **Teto M14:** `git diff --numstat --no-renames 8b5a44d5...076dcc80` dá 72 em `scripts/` e 179 em `tests/*.py`, 251 linhas, acima de 150: o corpo do PR precisa de `teto: excedido, 251 linhas, <motivo>` (o motivo é a exigência da classe C desta volta: spec e testes de guarda). Um comportamento só.
- **AR:** a classe de A1 (AR-1, AR-2) voltou neste pedido; a linha em `docs/engineering/achados-recorrentes.md` fica fora deste commit, que o brief limita ao parecer.

## Achados
- A1 (bloqueante) scripts/suite-paralela.py:532 · resolvido em fb58dd04 (M1 a M5 mortos) · classe C sem spec de mutantes: `forge-mutante --cobertura` lista 5 guardas novas sem mutante (532 `not completo`, 538, 540, 564, 572) e não há `tests/mutantes/v0457-suite-tempo-vivo.json`; falta também teste do ramo de linha parcial (532). Classe AR-1/AR-2
- A2 (recomendado) scripts/suite-paralela.py:542 · resolvido em fb58dd04 · o `print` informativo no stderr pode levantar BrokenPipeError/EIO e derrubar o orquestrador no meio do `esperar` (antes só imprimia no fim); sugestão: `try/except OSError` em volta das duas linhas de `TemposAoVivo` (542 e 557)
- A3 (recomendado) scripts/suite-paralela.py:300 · resolvido em fb58dd04 · o arquivo `.tempos` do filho é aberto e nunca fechado; sugestão: fechar no `finally` junto do `stopTestRun`
- A4 (recomendado) scripts/suite-paralela.py:309 · resolvido em fb58dd04 · a duração é medida duas vezes (`duracoes[nome]` e a linha `fim`); sugestão: gravar `duracoes[nome]` para o log e o resumo final darem o mesmo número
- A5 (recomendado) tests/test_suite_paralela.py:933 · `termina` lê o stdout inteiro antes do stderr; stderr acima de 64 KiB trava até o Timer de 30 s matar o filho (falha, não pendura). Saída do brinquedo é pequena; se crescer, ler o stderr numa thread

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
**Aprovado** no `076dcc80` (E23.30): o A1 está resolvido com M1 a M8 mortos e cobertura sem guarda descoberta; A2 a A4 aplicados; o A5 é recomendação e não devolve a entrega. Pendência do PR: a linha `teto: excedido` no corpo.

Parecer anterior, no `5c067124`: **Reprovado** no `5c067124`, só pelo A1. O comportamento está certo: a linha por unidade sai no stderr com flush, o resumo de quem rodava sai no sinal, e veredito, ordem, stdout e código de saída não mudam. Falta o que a classe C exige para guardas novas: a spec `tests/mutantes/v0457-suite-tempo-vivo.json` com um mutante por linha (532, 538, 540, 564, 572) e um teste do ramo de linha parcial (`not completo`, por exemplo um `.tempos` com `inicio\tx\t1` sem `\n` que não pode abrir a unidade). A2 a A4 são recomendações e não devolvem a entrega; o A2 sai barato no mesmo commit.
