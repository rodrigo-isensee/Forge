---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-prepush-patch
commit: ccb7a0c3663dd98c3eae57186ea9612c9b21cc83
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 prepush-patch (E2.327)

Item: patch `docs/devops/pp1-pre-push.patch` (três consertos do `.githooks/pre-push`, a aplicar pelo dono) e `tests/test_pre_push_patch.py`. O hook em vigor não muda neste head (diff: patch, teste e fragmento de changelog). Regras: `R-QA`, `R-CONFORMIDADE`.

## Achados
- A0 (bloqueante) docs/devops/pp1-pre-push.patch:41 · R-QA: o filtro só decide se roda; o forge-mutante julga todo Python do diff. Com hooks/_comum.py (só comentário) e condição mudada em tests/catraca.py o envio leve barra (reproduzido); a catraca do CI exclui testes (catraca.py:842).
- A1 (recomendado) .githooks/pre-push:386 · PREPUSH-LEVE-COBERTURA-CATRACA: o teste só exerce `hooks/*`; reduzir a lista a `hooks/*` (bin, scripts, templates, catraca, neutralidade) sobrevive. Some um caso com `bin/*.py`.
- A3 (recomendado) docs/devops/pp1-pre-push.patch:31 · saída 2 do filtro (catraca não carrega) sem teste; trocar `except Exception` por outra classe sobrevive. Só vira aviso, o CI pega. Resolvidos no head 5016852d: A0, A1, A2.
- A2 (recomendado) .githooks/pre-push:384 · a lista do patch é subconjunto da classe C do `forge-check` (sem apoios, pipeline); código de controle fora dela só é pego no CI. Não afrouxa nada; só registre o limite.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.321: patch só toca o pre-push, aplica limpo, sintaxe e modo executável | PatchAplica | só um arquivo no diff; `bash -n`; bit x | passou |
| PRE-PUSH-TEXTO-TRAVA-FD: lê o fd 9, não o caminho trocado | TextoDaTravaPorFd (3 testes) | caminho desviado por link; sem fd (vazio, rc 0); 200 bytes e sem controle | passou; original falha, remendado passa |
| FILA-INTERVALO-ZERO: 0, 00, 000 recusados | IntervaloDaFila (2 testes) | zero e zeros à esquerda; `1m`, `-1`, vazio; 1 e 60 passam | passou |
| PREPUSH-LEVE-COBERTURA-CATRACA: condição mudada em Python de controle sem mutante reprova | CoberturaDaCatraca (2 testes) | com condição (rc 1); sem condição e fora do controle (rc 0) | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pre_push_patch` no head: Ran 8 tests, OK.
- Patch aplicado numa cópia do head (`git apply` OK, `bash -n` OK) e os 12 módulos ligados ao hook rodados nela (trava, fila, leve, afetados, refs, já no remoto, só docs, segredo, parecer, agente morto, ocupação, patch): Ran 281 tests, OK (skipped=13, todos do sandbox: chown e /proc de outro namespace). Aplicar o patch não quebra teste existente.
- Commit e envio do dono: o commit que aplica o patch mexe em `.githooks/pre-push` (shell, fora da lista de Python de controle). Simulado numa cópia com `origin/develop`: `pre-push: checagens baratas ok em 2s (1 arquivos)`, plano leve, rc=0. O envio do dono passa pelo hook alterado; a trava e a fila seguem iguais (a espera do `exec 9>>` lê o mesmo inode pelo `/proc/self/fd/9`).
- Vermelho antes do verde: `bin/forge-testes --vermelho 1b88640e` estourou o prazo duas vezes (170 s e 560 s, rc=124): sem veredito, não conta como vermelho. Prova substituta: cada subteste roda o hook original (sem patch) e exige o comportamento antigo (caminho lido, `0` aceito, rc 0 sem cobertura) e o remendado com o conserto.
- Mutação à mão no hook remendado (7 mutantes, `test_pre_push_patch`): mortos 5 (fd volta ao caminho, `-gt 0` relaxado, cobertura desligada, rc da cobertura, falha não marcada); sobreviveram 2: remover `[ -e /proc/self/fd/9 ] || return 0` (equivalente: sem o fd, `head` falha calado e o texto sai vazio) e reduzir a lista de controle (A1). `forge-mutante` com spec não se aplica: o hook em vigor não muda neste pedido.
- Reprovação: simulação numa cópia com o patch, diff com comentário em `hooks/_comum.py` e `if not not` em `tests/catraca.py`: `forge-mutante --cobertura` sai `sem mutante · tests/catraca.py:78` e o envio sai rc=1 ("o CI reprova igual"), mas `fc.TESTE.search("tests/catraca.py")` é verdadeiro e a catraca o exclui. Falso bloqueio do envio do dono (mesmo achado do review A1; vale filtrar a saída pela lista).
- `forge-check docs`: rc=0. PA-7 (`achados-recorrentes.md`): conferidos AR-1 (lista de mutantes, aqui A1), AR-5 (o patch usa `python3 -I`), AR-3 (sem lista negativa nova), AR-6, AR-7, AR-8: sem recorrência nova.
- Suíte inteira: CI do PR (check-run `bateria` do mesmo sha), não rodada aqui.

## Revalidação por delta (head 5016852d, base do delta 805a0a10)
`forge-check parecer delta` listou `bin/forge-mutante` (só docstring), o fragmento de changelog e `tests/test_pre_push_patch.py`; o patch mudou (docs/).
- A0 (resolvido): o patch filtra a saída do `forge-mutante --cobertura` por `motivo_de_controle` e `TESTE` da catraca. Testes novos: comentário em `hooks/_comum.py` mais condição em `tests/catraca.py` passa (rc 0); falta em `hooks/h.py` mais a de `tests/catraca.py` reprova só pela primeira.
- A1 (resolvido): o caso de `bin/x.py` reprova (`sem mutante · bin/x.py`); a lista fixa por prefixo saiu do patch.
- A2 (resolvido): a lista é a própria da catraca, não mais um subconjunto.
- `python3 -m unittest tests.test_pre_push_patch`: Ran 12 tests, OK.
- Mutação no filtro (4 à mão, copia de `git archive`): sem `TESTE` morto (2 falhas); `motivo_de_controle` trocado por `True` morto (1); saída sempre 0 morta (3); `except` trocado sobrevive (A3).
- `forge-check docs`: rc=0. PA-7 conferido: AR-1 (lista de mutantes, coberta pelo caso de `bin/`) sem recorrência nova.
- Suíte inteira: CI do PR (check-run `bateria` do mesmo sha), não rodada aqui.

## Revalidação por delta (head 49aa9ef9, Revisar-sha 8079c5d4, base do delta 5016852d)
`forge-check parecer delta` listou só `bin/forge-mutante` (opção `--conferir --todas`, AR-12), que veio da `develop` pelo merge 3a309e34 (E2.438), não do item. O patch, o teste do item e o hook em vigor não mudaram desde 5016852d.
- `python3 -m unittest tests.test_pre_push_patch`: Ran 12 tests, OK.
- `python3 -m unittest tests.test_forge_mutante` (arquivo tocado pelo merge): Ran 124 tests, OK.
- A3 (recomendado) segue aberto, sem mudança; sem bloqueante. Suíte inteira: CI do PR (check-run `bateria` do mesmo sha), não rodada aqui. PA-7 conferido: AR-1 e AR-12 sem recorrência nova neste item.

## Revalidação por delta (head 563518d1, Revisar-sha ccb7a0c3, base do delta 8079c5d4)
`forge-check parecer delta` listou `bin/forge-testes` (o MAPA liga `docs/devops/pp1-pre-push.patch` e `hooks/.*` ao `test_pre_push_patch`) e `tests/test_testes_tocados.py` (caso novo do mapa; o ambiente do teste tira o `GIT_*` herdado). O patch, o teste do patch e o hook em vigor não mudaram. Entre ccb7a0c3 e 563518d1 só muda o parecer do review (aprovado).
- `python3 -m unittest tests.test_testes_tocados tests.test_pre_push_patch` (sem `-I`): Ran 174 tests, OK (skipped=1, `/proc` de outro namespace no sandbox).
- Caso novo do mapa: `docs/devops/pp1-pre-push.patch` e `hooks/_comum.py` planejam `dirigido` com `test_pre_push_patch`; o teste cai se a linha do MAPA sair.
- A3 (recomendado) segue aberto, sem mudança; sem bloqueante. Suíte inteira: CI do PR (check-run `bateria` do mesmo sha), não rodada aqui. PA-7 conferido: AR-1 sem recorrência nova neste item.
