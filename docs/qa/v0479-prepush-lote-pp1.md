---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-prepush-lote-pp1
commit: ce1dc90c2fd20b2a6049b11ac8b9afdcecfbede2
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: lote PP1 do pre-push (proposta de diff, E94.4)

Entrega: `docs/propostas/prepush-lote-pp1.md` (diff para `.githooks/pre-push`, que só o dono aplica), `tests/test_prepush_lote_pp1.py`, 5 specs de mutantes. Nada foi gravado em `.githooks`; o patch foi aplicado só em cópias em `$TMPDIR`. Sem suíte local (a bateria é o check-run `bateria` do CI do PR).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice das fixtures e pulos novos reprovam no envio leve | `IndiceEPulos` (11) | corpus tocado x fora; pulo só citado; erro de sintaxe; catraca ilegível | passou |
| Cobertura da catraca reprova só controle sem teste | `CoberturaDaCatraca` (8) | saída 2, formato fora, link no `forge-check`, condição em teste | passou |
| Texto da trava lido do fd 9 | `TextoDaTravaPorFd` (3) | sem descritor, 200 bytes, caminho trocado | passou |
| Intervalo 0 recusado, base 10 | `IntervaloDaFila` (4) | `0`, `00`, `08`, `09`, inválido | passou |
| Lista vazia ou ilegível avisa | `ListaVazia` (6) | sem sort, sem mktemp, sort com erro, sem base | passou |
| Patch só toca o hook e aplica | `PatchAplica` (1) | arquivos do diff, `bash -n`, modo executável | passou |

## Cenários e resultado real
- Os 33 testes de `tests/test_prepush_lote_pp1.py` passam no head (`python3 -I -m unittest discover -s tests -p test_prepush_lote_pp1.py`: `Ran 33 tests ... OK`). `tests/test_reval_delta.py` (tocado): 10 OK.
- Vermelho antes do verde (`bin/forge-testes --vermelho fb3b670b --modulos test_prepush_lote_pp1`): `vermelho: base=fb3b670b784a head=51648bfe12a0`, revertidos à base `bin/forge-testes`, fragmento, proposta e pesos; `contagem: prova (API ausente)=33`, rc 0. Ressalva: o vermelho da base é por ausência da proposta (o teste a lê), e não por falha de comportamento sobre o hook antigo; o comportamento antigo aparece nas sondas S1 a S8 da seção 5 da proposta e nos testes que comparam com o original.
- Mutantes, uma chamada por pedido (as 5 specs têm `pedido` distinto; a chamada única sai rc 2): specs `v0479-prepush-lote-pp1.json` (M1-M8), `-2` (M9-M16), `-3` (M17-M24), `-4` (M25-M32), `-5` (M33-M36): 36 de 36 `morreu`, rc 0 nas cinco, nenhum sobrevivente, nenhum equivalente.
- Skip: nenhum teste do arquivo é pulado. As ocorrências de `skip` são texto de fixture do próprio teste (código que o hook deve barrar), sem decorador nem `skipTest` ativo.
- Envio leve, medida minha (clone em `$TMPDIR`, `origin/develop`=fb3b670b, hook chamado direto, 3 rodadas): só texto, antes 398 a 411 ms, depois 405 a 472 ms; Python de controle e teste, antes 605 a 686 ms, depois 918 a 1063 ms. O pior caso fica em cerca de 1,1 s, abaixo do critério de reversão da proposta (3 s); sem teste local nenhum.

## Revalidação no head ce1dc90c (delta 51648bfe..ce1dc90c)
- Delta (`forge-check parecer delta`): `bin/forge-testes` (+1 regra no MAPA para `bin/forge-mutante`), `tests/test_prepush_lote_pp1.py` (caminho literal `bin/forge-mutante`, sem a constante `MUTANTE`), `tests/test_testes_tocados.py` (2 testes), fragmento do changelog. O hook e a proposta não mudaram.
- Os testes mudados provam o mesmo: `test_prepush_lote_pp1` 33 OK; `test_testes_tocados` 196 OK; `test_pre_push_patch` 12 OK. Em `test_testes_tocados`, `bin/forge-mutante` saiu da lista "sem regra no mapa" (agora tem regra) e a asserção da regra passou a esperar `test_pre_push_patch` e `test_prepush_lote_pp1`; o brinquedo de renomeação cria os três módulos que a regra cita e espera a lista exata ordenada. Cada um falha se a regra mudar.
- Skip: nenhum novo no delta (sem `skip` nem `expectedFailure` nas linhas adicionadas dos testes). O `skipped=1` de `test_testes_tocados` já existe na base (nada no diff o toca).
- Mutantes das 5 specs do item rodados de novo: 8, 8, 8, 8 e 4 `morreu`, nenhum sobrevivente, rc 0 em todas.
