---
tipo: review
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 5c6684ddd222f18cd82c055f0602e23340720d98
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: lote-fechar2

Base `b6eb84fed86e3b5289f3950b33d43a86f34343c2`, head `5c6684ddd222f18cd82c055f0602e23340720d98`. Revalidação 4, por delta sobre o parecer `308158f` (head `7c926e4`): volta 3 (`fde6b54`, `5c6684d`), pela DECISÃO DO DONO 2026-10-27 07:49 "B". Só testes e specs mudaram.

## Achados
- A3 (recomendado) bin/forge-fechar:523 · `mapfile` é o primeiro uso de recurso do bash 4 no repositório; o script já depende de `sort -z` e `comm -z` do GNU, então não é regressão prática, mas vale uma linha no comentário do cabeçalho (fora da volta por decisão técnica de 2026-10-26 17:13; segue informativo)
- A4 (recomendado) bin/forge-fechar:526 · com dois pontos de partida, o laço junta os diffs de cada lado antes de cruzar: no criss-cross, arquivos iguais nos dois lados saem como em comum e o 2b para (falha segura); cruzar por ponto de partida resolveria, em cartão próprio

## Revalidação por delta
- Delta lido (`forge-check delta --parecer docs/reviews/lote-fechar2.md`, intervalo `7c926e4..5c6684d`): `tests/mutantes/lote-fechar2-2.json`:54-86; `tests/mutantes/lote-fechar2-3.json`:1-27; `tests/test_fechar_base_andou.py`:17-21, :30-32, :59-60 e :243-265. Os outros arquivos do intervalo são pareceres (`docs/qa/`, `docs/reviews/`, `docs/security/`).
- Já lido nos pareceres `f10ec5b` e `308158f`, sem mudança no delta: `bin/forge-fechar` inteiro (nenhuma linha de código mudou), `tests/test_fechar.py`, a primeira spec `tests/mutantes/lote-fechar2.json`, o resto de `tests/test_fechar_base_andou.py` e `.github/workflows/ci.yml` (o parecer de devops `204abdd` segue valendo).
- Sort falso (`SORT_FALSO`, :17-21): segue o padrão do `COMM_FALSO` (primeiro no PATH, repassa ao sort real tirando a primeira entrada); só falha quando `$ESTADO/sort_falha_em` existe e o último argumento termina em `/a` (lista da base) ou `/b` (lista da branch), então os outros testes da classe não mudam. Um teste de cada lado da cadeia de :530, os dois com arquivo em comum (`b`), afirmam rc 1, a mensagem "não consegui cruzar as listas de arquivos", a ausência de "sem arquivo em comum" e nenhuma criação nem merge de PR.
- Os mutantes Y1, Y2 e Y4 morrem pela rota certa: Y2 e Y4 (`;` depois do sort `a`) fazem o comm rodar com `a.s` vazio e seguir como "sem arquivo em comum", o teste do lado `a` pega; Y1 (`;` antes do comm) com o sort `b` falho roda o comm sobre `b.s` vazio e segue, o teste do lado `b` pega (com o sort `a` falho, o comm acha `b.s` ausente e o `die` ainda vale, por isso a spec lista os dois testes).
- Rev-list falso (:30-32) e `test_contagem_de_commits_da_base_que_falha_para_no_passo_2b`: base que andou sem arquivo em comum, `rev-list --count` falho; afirma rc 1, a mensagem da contagem e nenhum PR. Mata o M1 da 3.ª spec (`|| die` → `|| :` em :538).
- Varredura de :520-540 (linhas mudadas em relação à base: :523, :526, :530-532 e :538): :523 M2 da 3.ª spec (só o primeiro merge-base no `mapfile`); :526 M3 da 2.ª; :527 e :528 M1 e M2 da 2.ª; :530 Y1, Y2, Y4; :531 M5 da 1.ª (`die` → `:`); :533 M4 da 2.ª; :536 M5 da 2.ª; :538 M4 da 1.ª (contagem) e M1 da 3.ª (`die`); :532 é só o `fi`. Cada trecho `de` das três specs casa uma vez só no arquivo (conferido por script, contagem 1 em todos).

## Ferramentas (citadas, não refeitas à mão)
- `bin/forge-mutante tests/mutantes/lote-fechar2-2.json` (rev `5c6684ddd222`): M1 :527, M2 :528, M3 :526, M4 :533, M5 :536, Y1 :530, Y2 :530, Y4 :530, todos `morreu`, rc=0.
- `bin/forge-mutante tests/mutantes/lote-fechar2-3.json` (rev `5c6684ddd222`): M1 :538, M2 :523, `morreu`, rc=0.
- `python3 -m unittest tests.test_fechar_base_andou`: `Ran 20 tests in 7.160s` / `OK`.
- `shellcheck bin/forge-fechar`: rc=0, sem aviso.
- Teto M14: 212 linhas de código e teste (`ci.yml` 2, `bin/forge-fechar` 32, `tests/test_fechar.py` 52, `tests/test_fechar_base_andou.py` 126); specs de mutantes, changelog e pareceres ficam fora. Sem `hooks/` e sem caminho protegido.
- `docs/engineering/achados-recorrentes.md` (PA-7): lista vazia, nada a conferir.
- Segurança e QA: pareceres próprios (E2.1, E3.1), que não refaço aqui.

## Parecer
Aprovado. O sort falso falha de cada lado da cadeia de :530 e mata Y1, Y2 e Y4; o rev-list falso mata o mutante da contagem de :538; toda linha mudada de :520 a :540 tem mutante morto. A3 e A4 seguem recomendações e não devolvem a entrega.
