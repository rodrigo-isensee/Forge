---
tipo: review
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 68f100685208dfccefde80f81e43ac5eb6aff224
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-fechar2

Base `b6eb84fed86e3b5289f3950b33d43a86f34343c2`, head `68f100685208dfccefde80f81e43ac5eb6aff224`. Revalidação 2, por delta sobre o parecer `2206568` (head `0315561`): volta 1 (`403bdc1`, `36731f2`) e o complemento (`68f1006`).

## Achados
- A3 (recomendado) bin/forge-fechar:523 · `mapfile` é o primeiro uso de recurso do bash 4 no repositório; o script já depende de `sort -z` e `comm -z` do GNU, então não é regressão prática, mas vale uma linha no comentário do cabeçalho (fora da volta por decisão técnica de 2026-10-26 17:13; segue informativo)

## Revalidação por delta
- Delta lido (`forge-check delta --parecer docs/reviews/lote-fechar2.md`, intervalo `0315561..68f1006`): `bin/forge-fechar`:136-137 e :141; `changelog.d/lote-fechar2.md`:4; `tests/mutantes/lote-fechar2-2.json`:1-26; `tests/mutantes/lote-fechar2.json`:9-10 e :36-86; `tests/test_fechar.py`:594; `tests/test_fechar_base_andou.py`:12-16, :21-24, :27-29, :49-50 e :156-217.
- Já lido no parecer `2206568`, sem mudança no delta: o resto do `remoto_exato`, os quatro pontos de uso (:462, :475, :514, :600), `conferir_base` e `.github/workflows/ci.yml` (o parecer de devops `204abdd` segue valendo para a linha do CI).
- A1 (mensagem do passo 2 com ls-remote falho): fechado. `test_ls_remote_da_branch_que_falha_para_no_passo_2_com_a_mensagem_da_leitura` faz o git falso sair 128 só para `refs/heads/melhoria/x` e afirma a mensagem da leitura, a ausência da mensagem de branch ausente e nenhum PR criado; o mutante M6 (`|| :` no :600) morre.
- A2 (filtro `printf` em tests/test_fechar.py:594): fechado. O filtro saiu e o teste segue verde com uma única chamada, a do ajudante (`Ran 1 test` / `OK`).
- Coluna 1 como sha (recomendado da segurança `2dc5cb2`): o `awk` usa `length($1) == 40 || length($1) == 64` com `^[0-9a-f]+$`, em vez de `{n}`, que o mawk não aceita. Com a linha casada e a coluna 1 inválida, o `exit` vai ao `END` com `ruim = 1` e o ajudante devolve rc 1, que os quatro pontos de uso já tratam como leitura que falhou; sem linha casada, rc 0 e sha vazio, como antes. Conferi na mão em mawk e gawk: sha de 40 imprime e rc 0; `abc` e 40 `z` dão rc 1 sem imprimir; entrada vazia dá rc 0 e nada.
- Testes novos de `tests/test_fechar_base_andou.py` exercitam as rotas dos mutantes: o criss-cross gera dois pontos de partida (a asserção do `merge-base --all` prova isso) e, com um só na contagem, o resultado é 2 commits em vez de 1 (M4), qualquer que seja a ordem da lista; o `comm` falso falha só com o marcador e, sem ele, delega ao `comm` de verdade tirando a primeira entrada do PATH, que o `setUp` põe na frente (M5); `diff_falha_em` derruba só o diff cujo último argumento é o sha da base ou o da branch, então cada `die` de :527 e :528 é provado sozinho (M1 e M2 da segunda spec); os três lixos da coluna 1 separam o tamanho (M7) do hexadecimal (M8).

## Ferramentas (citadas, não refeitas à mão)
- `bin/forge-mutante tests/mutantes/lote-fechar2.json`: M1 a M8 `morreu`, rc=0. `bin/forge-mutante tests/mutantes/lote-fechar2-2.json`: M1 (:527) e M2 (:528) `morreu`, rc=0. Os trechos `de` casam uma vez só no arquivo.
- `python3 -m unittest tests.test_fechar_base_andou`: `Ran 16 tests in 6.315s` / `OK`.
- `shellcheck bin/forge-fechar`: rc=0, sem aviso.
- Teto M14: 164 linhas de código e teste (`ci.yml` 2, `bin/forge-fechar` 32, `tests/test_fechar.py` 52, `tests/test_fechar_base_andou.py` 78); specs de mutantes, changelog e pareceres ficam fora. Sem `hooks/` e sem caminho protegido.
- Segurança e QA: pareceres próprios (E2.1, E3.1), que não refaço aqui.

## Parecer
Aprovado. A1 e A2 fecharam, a validação da coluna 1 transforma lixo em leitura que falhou sem mudar o caso da branch ausente, e cada guarda apontada pela QA (A1 do parecer `1473646`) tem agora um mutante que morre com um teste que exercita a rota. O A3 continua como recomendação e não devolve a entrega.
