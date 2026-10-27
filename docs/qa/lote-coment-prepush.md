---
tipo: qa
contrato: 1
pedido: lote-coment-prepush
branch: melhoria/lote-coment-prepush
commit: 70ba6c614bdaa0f2dae1c3aff051ba53a2b97f43
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: lote-coment-prepush

Pedido LOTE-COMENT-PREPUSH-REV (E3.1). Só texto: README (Suíte do Forge) e docstring de `bin/forge-testes`; nenhum comportamento muda. Base 739b0b083d2baacefdf4f7482b2b2ac31ed8e02c, head 70ba6c6 (volta 1; o parecer anterior era sobre bcdb3b9).

## Achados
- A1 (recomendado) .githooks/pre-push:236 · o comentário do hook ainda diz "decisão do dono, 2026-10-23: A" (a vigente é a M8 de 2026-10-24); fora do escopo do lote (tocar o hook faria o pre-push cair na suíte inteira), fica para lote próprio (era o A2 da rodada anterior; o A1 anterior, ameacas/ e aceites/, está fechado: o README agora os cita)

## Critério → teste → resultado
Sem especificação de UX nem `CA-n`; as obrigações são as do escopo E1 do pedido e os achados da volta 0.

| Obrigação | Teste | Resultado | Fronteira protegida |
|---|---|---|---|
| E1: README cita os casos de suíte inteira (`bin/forge-testes`, `tests/config.json`, `.githooks/`) e o caminho só de parecer | `tests.test_forge.PrePushSoOsAfetados.test_readme_cita_os_casos_da_suite_inteira_e_o_caminho_so_de_parecer` | passa no head; falha na base | n/a |
| E1 + A1 anterior: README lista árvore suja, mais de uma ref, HEAD diferente, ref nova, prova ausente, `ameacas/`, `aceites/`, sem `origin/develop`, e diz que em `melhoria/*` segue a regra acima | `...PrePushSoOsAfetados.test_readme_lista_todos_os_casos_da_suite_inteira_do_so_parecer` | passa no head; falha na base | limite do caminho curto (arquivo fora dos quatro diretórios, modelo, ameacas/aceites) |
| E1: docstring cita M8, 2026-10-24, "substitui" | `tests.test_testes_tocados.NaoEPortao.test_docstring_cita_a_decisao_m8_de_2026_10_24` | passa no head; falha na base | n/a |
| Corte 1 da ACELERA-RODADA: docstring não manda review e QA rodarem a suíte inteira | `...NaoEPortao.test_docstring_nao_manda_review_e_qa_rodarem_a_suite_inteira` | passa no head; falha na base | n/a |
| Só texto, nenhum comportamento muda | diff (`.githooks/` intacto) + `test_forge` e `test_testes_tocados` inteiros | 512 testes OK | n/a |

## Conferência do README contra o hook (frase a frase, `.githooks/pre-push` no head, sem diff no hook)
- "branch fora de `melhoria/*`": `dirigido` exige `refs/heads/melhoria/*` (252). Confere.
- "caminho sem regra no mapa" e "falha de leitura do plano": só vale o plano que começa por `forge-testes: dirigido (` (266-267). Confere.
- "diff que toca `bin/forge-testes`, `tests/config.json` ou `.githooks/`": linha 265. Confere.
- "push com mais de uma ref" (`so_parecer` 214, `dirigido` 251), "ref que não é branch" (215/252), "ref nova" (221-222, só o `so_parecer` a recusa), "árvore suja" (218/257), "HEAD diferente do commit enviado" (217/256), "prova ausente" (219 e a prova `.verde`): confere.
- "mexe em qualquer arquivo fora desses quatro diretórios, em modelo `_*`, em `ameacas/` ou `aceites/`": linhas 229-231. Confere.
- "em `melhoria/*` esse envio segue a regra acima": a ordem é `so_parecer` → `dirigido` → suíte inteira (270-277); falhando o caminho curto, `dirigido` decide, e ele não olha o sha remoto (ref nova vai para o dirigido). Confere. "sem `origin/develop` ou falha de leitura do plano vai para a suíte inteira": 259 e 266-268. Confere.
- Sem ref e só remoção: 140-155. Confere. O README não descreve caso que o pre-push não faça.

## Vermelho antes do verde
`python3 bin/forge-testes --vermelho 739b0b083d2baacefdf4f7482b2b2ac31ed8e02c --modulos test_forge,test_testes_tocados` (rc 0), trecho:
```
vermelho: base=739b0b083d2b head=70ba6c614bda módulos=test_forge,test_testes_tocados (restrito por --modulos)
tests.test_forge.PrePushSoOsAfetados.test_readme_cita_os_casos_da_suite_inteira_e_o_caminho_so_de_parecer · H=ok · B=falha · prova (asserção)
tests.test_forge.PrePushSoOsAfetados.test_readme_lista_todos_os_casos_da_suite_inteira_do_so_parecer · H=ok · B=falha · prova (asserção)
tests.test_testes_tocados.NaoEPortao.test_docstring_cita_a_decisao_m8_de_2026_10_24 · H=ok · B=falha · prova (asserção)
tests.test_testes_tocados.NaoEPortao.test_docstring_nao_manda_review_e_qa_rodarem_a_suite_inteira · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=508; prova (asserção)=4
```

## Execução
`python3 -m unittest tests.test_forge tests.test_testes_tocados` no head: Ran 512 tests, OK. Suíte completa e CI não rodados aqui (pre-push e CI do PR cobrem). Mutação: não se aplica (só docstring em `bin/`, nenhuma linha de guarda mudada).

## Parecer
Aprovado. Zero bugs; uma recomendação que não devolve.
