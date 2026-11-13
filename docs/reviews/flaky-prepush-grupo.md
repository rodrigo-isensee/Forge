---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/flaky-prepush-grupo
commit: 989d49f5661d93c37dfff8813a905ba97490cd6c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v046 (E26.5, flaky do pre-push, grupo da etapa)

Diff lido: `c340c322..905edbbb` (`tests/test_prepush_so_docs.py` +14 −1, `changelog.d/flaky-prepush-grupo.md`). Testes do arquivo tocado: `python3 -m unittest tests.test_prepush_so_docs` → `Ran 62 tests ... OK (skipped=9)`; os 4 de `GrupoDaEtapa` são pulados aqui (`/proc` de outro namespace), então a prova abaixo foi feita com uma sonda que usa só PIDs lidos do `/proc`.

## Achados
- A1 (bloqueante, resolvido em 989d49f5) tests/test_prepush_so_docs.py:315 · vigia aceita o irmão: lanca() faz `sleep 60 &` e depois exec do hook, então o irmão é filho `sleep` do PID do hook desde antes da etapa; a espera passa na hora, sem o hook no laço. Exclua o PID de `self.le("irmao")` na condição

## Sondas
- S1 · bash -c "sleep 6 >/dev/null 2>&1 & exec python3 -c 'import time; time.sleep(5)'" (lançamento de lanca(), hook sem laço) e vigia(pid do hook no /proc, -1) do 905edbbb · espera: False · obtido: True (filho sleep 13 do hook 12)

## Parecer
Reprovado. O objetivo da troca está certo: o estado que importa é o hook já ter passado das linhas 148-149 do `rodar_etapa` (`alvo` calculado), e o `sleep 1` do laço da linha 157 é o sinal certo disso; o prazo de 30 s com `assertTrue` falha alto se o estado não chega, e as asserções antigas ficaram iguais, então o teste não perdeu força pelo lado da asserção.

O defeito está na condição de vigia (A1): `GrupoDaEtapa.lanca()` (linha 281) roda `sleep 60 & ... ; exec .githooks/pre-push`, e o `sleep 60` do irmão fica com o pai igual ao PID do hook depois do `exec`. Ele tem nome `sleep`, não é a etapa e seu pai é o hook: `vigia` devolve `True` assim que o irmão existe, antes até da etapa rodar (S1). A espera nova vira no-op e, sem o `time.sleep(1)` antigo, o SIGTERM sai logo depois de a etapa gravar o arquivo `etapa`, ainda com o hook podendo estar no `ps` da linha 148; a janela da corrida original fica maior, não menor.

Sugestão (correção é do autor): passar o PID do irmão para a vigia e exigi-lo fora da condição (`pid not in (etapa, irmao)`), ou exigir o filho `sleep` nascido depois da etapa (starttime maior que o dela). Vale uma sonda no CI que prove `vigia` falsa logo após `lanca()` com a etapa ainda bloqueada.

Conferido sem achado: o parse do `/proc/<pid>/stat` (nome entre o primeiro `(` e o último `)`, pai no campo 2 do resto) está certo; o `sleep` de fundo da etapa (`sleep 60 & exec sleep 60`) tem pai na etapa e não confunde a vigia; o `sleep` da fila (linha 287) acaba antes da etapa nascer. Não é classe já listada em `docs/engineering/achados-recorrentes.md`.

## Revalidação (E26.16, delta 905edbbb..989d49f5)
Delta lido com `forge-check parecer delta docs/reviews/flaky-prepush-grupo.md`: só `tests/test_prepush_so_docs.py` (+6 −5). `vigia(hook, etapa, irmao)` passa a exigir `pid not in (etapa, irmao)`; `interrompe` lê `irmao` do arquivo antes de esperar e reusa o valor no `assertIn` final. O `irmao` é gravado por `lanca()` antes do `exec`, então `le("irmao")` não corre. A1 resolvido: o único `sleep` filho do hook que sobra é o do laço de vigia (linha 157 do hook), que é o estado pedido.

Sonda S1 reexecutada: com o irmão excluído, a vigia fica falsa sem laço (era True com o 905edbbb). Neste sandbox o `/proc` e o `ps` são virtualizados (o PID real não aparece), então a sonda não rodou aqui; a conclusão vem da leitura da condição e a prova do teste fica com o CI. `python3 -I -m unittest discover -s tests -p test_prepush_so_docs.py` → `Ran 62 tests in 80.242s, OK (skipped=9)` (os de `GrupoDaEtapa` pulam aqui).

Sem achado novo. Recomendado (não bloqueia): a sonda no CI sugerida (vigia falsa logo após `lanca()` com a etapa bloqueada) não foi adicionada; o commit 989d49f5 cobre a causa, não o teste da vigia.

Parecer: aprovado no head 989d49f5.
