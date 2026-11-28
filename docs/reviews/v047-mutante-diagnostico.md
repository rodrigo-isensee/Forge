---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-diagnostico
commit: bb8aac06413679d6db6564019c95cfe14c20dfe9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047, diagnósticos do forge-mutante e isenta pelo texto (E1.283, portão E1.295)

Escopo: `origin/develop..ef1fb25b` (develop em c5c3a449), 2 commits (424fd1a2, ef1fb25b), 12 arquivos. Quem revisa não fez a entrega. Comparei o diff com o item E1.283 do pedido v047: ISENTA-POR-TEXTO, recusa cedo com árvore suja e spec diferente da do commit, `por quê` no `--cobertura`, specs de pedidos diferentes com as chamadas prontas. Classe C (código de controle em `bin/`).

Veredito sobre `ef1fb25b`: **APROVADO**, com 2 recomendados.

## O que li
- `bin/forge-mutante`: `validar_specs` (agrupa por pedido e cita as chamadas com `shlex.quote`), `por_que_nao_cobre` extraída de `casa` (mesma regra de cobertura, agora com motivo; o teste de toque no nó só filtra o diagnóstico e não muda o veredito de `casa` fora da borda vazia), `cruza` sem `linha_base` (a apagada uma vez casa o trecho uma vez na fatia do nó e uma condição por isenta; a nova segue trecho único no arquivo), `specs_fora_do_commit` e a recusa antes de rodar.
- ISENTA-POR-TEXTO não afrouxa a contagem: cada isenta continua liberando no máximo uma condição apagada (`usadas`), a nova processa antes e marca a isenta, e a apagada repetida (2+) segue a forma do trecho único. `linha_base` passa a ser aceita e ignorada; o caso C-1/L7 (isenta com `linha_base` numa condição nova) perde o sentido, porque ela vira isenta comum, que já podia liberar a nova.
- Os 17 mutantes realinhados (pedido do item: olhar se algum afrouxou). M28, M29, M30, M60, M1, M4, C1, C2, C3, C5 e IL15 descrevem a mesma mutação semântica na forma nova (`==` virou `!=` com o ramo invertido, ou só o nome `inicio` virou `onde[0]`). IL2, IL4, IL5, IL11 e IL12 miram as guardas que substituíram as da linha; IL1 ficou mais grosso (`True or` derruba os três termos), mas IL2 e IL3/MD4 cobrem os termos um a um. Nenhum afrouxou.
- Guardas novas com um mutante por linha (MD1 a MD20) e a isenta da guarda dividida (MD1 + MD5) com motivo verificável.

## Ferramentas (citadas, não refeitas como leitura)
- Autor (pedido v047, registro de 23:21): `test_forge_mutante` 115 OK; MD1 a MD20 mortos. Sem PR, sem CI ainda: o CI do PR decide a suíte.
- Rodado aqui: os 7 testes novos ou mudados, `Ran 7 tests ... OK`; mutantes IL11 (teste trocado), IL1, M30, IL15 e MD12 numa spec fora do repositório, os 5 `morreu`; `forge-mutante --cobertura --base c5c3a449` rc 0, 18 `coberta`, 1 `isenta · bin/forge-mutante:527(base)`.

## Achados
- A1 (recomendado) bin/forge-mutante:612 · o walrus `motivo :=` na compreensão reatribui o `motivo` da função (escopo do PEP 572); hoje inofensivo, pois o próximo uso o recalcula, mas é armadilha de leitura: troque o nome (ex.: `porque`).
- A2 (recomendado) bin/forge-mutante:1 · 213 linhas de código e teste (119 em bin, 94 em tests) e quatro comportamentos no lote: o corpo do PR traz `teto: excedido, 213 linhas, <motivo>` (M14).

## Sondas

## Revalidação no head bb8aac06 (delta lido, 2026-11-16)
Delta (`forge-check parecer delta`, de ef1fb25b a bb8aac06): o grosso veio da develop (merge 1747d8d7, fora do domínio); o delta próprio é o commit bb8aac06, só `tests/mutantes/guarda-sem-mutante-4.json`: M31 e M32 passam de `inicio` para `onde[0]`, a forma atual da fonte em `bin/forge-mutante`. O `para` e os testes não mudaram, logo a mutação é a mesma e nada afrouxou. Cada `de` aparece uma vez em `bin/forge-mutante`; `ini - inicio` não existe mais. `bin/forge-mutante --conferir --todas` não aponta nenhuma linha de `guarda-sem-mutante-4.json`; `python3 -m unittest tests.test_forge_mutante`: Ran 127 tests, OK. A1 e A2 seguem recomendados. Sem achado novo.

## Parecer
Aprovado. O diff faz o que o E1.283 pede, sem sobra: a isenta sobrevive à base deslocada (teste com 9 linhas novas antes e `linha_base` 99 ignorada), a árvore suja com spec diferente ou ausente no commit sai 2 antes de rodar e a limpa segue rodando com `--rev` antigo, o `por quê` sai só para mutante que toca o nó e os pedidos diferentes saem com uma chamada por pedido, caminho com espaço citado. Os mutantes antigos realinhados mantêm a força. A1 e A2 são recomendados (`R-REVIEW`) e não devolvem.
