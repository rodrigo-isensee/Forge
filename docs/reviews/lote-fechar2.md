---
tipo: review
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: 7c926e42a3a6b333c46bf4967dadac9e18724f5b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-26
---
# Review: lote-fechar2

Base `b6eb84fed86e3b5289f3950b33d43a86f34343c2`, head `7c926e42a3a6b333c46bf4967dadac9e18724f5b`. Revalidação 3, por delta sobre o parecer `f10ec5b` (head `68f1006`): volta 2 (`926b390`, `7c926e4`), pela DECISÃO DO DONO 2026-10-26 19:34 "B". Só testes e specs mudaram.

## Achados
- A3 (recomendado) bin/forge-fechar:523 · `mapfile` é o primeiro uso de recurso do bash 4 no repositório; o script já depende de `sort -z` e `comm -z` do GNU, então não é regressão prática, mas vale uma linha no comentário do cabeçalho (fora da volta por decisão técnica de 2026-10-26 17:13; segue informativo)
- A4 (recomendado) bin/forge-fechar:526 · com dois pontos de partida, o laço junta os diffs de cada lado antes de cruzar: no criss-cross do teste novo, `so_b` e `so_c`, iguais nos dois lados, saem como em comum e o 2b para (falha segura); cruzar por ponto de partida resolveria, em cartão próprio

## Revalidação por delta
- Delta lido (`forge-check delta --parecer docs/reviews/lote-fechar2.md`, intervalo `68f1006..7c926e4`): `tests/mutantes/lote-fechar2-2.json`:24-53; `tests/test_fechar_base_andou.py`:157-159, :161-163, :167-169 e :186-193. Os outros arquivos do intervalo são pareceres (`docs/qa/`, `docs/reviews/`).
- Já lido no parecer `f10ec5b`, sem mudança no delta: `bin/forge-fechar` inteiro (nenhuma linha de código mudou), `tests/test_fechar.py`, a primeira spec `tests/mutantes/lote-fechar2.json`, `.github/workflows/ci.yml` (o parecer de devops `204abdd` segue valendo).
- Teste criss-cross exercita o laço de :526 de verdade: com `arquivos=True`, B (lado da branch) grava `so_b` e C (lado da base) grava `so_c`; o helper afirma que `merge-base --all` devolve {B, C}. Com mb=B, os dois diffs trazem só `so_c`; com mb=C, só `so_b`. O laço inteiro lista os dois; o mutante M3 (`lista_mb[0]`) lista só um, e a asserção exige a lista `["  so_b", "  so_c"]` exata, então ele morre qualquer que seja a ordem do `merge-base --all`. O teste também afirma rc 1 e nenhuma criação nem merge de PR. O caso sem arquivos (`test_varios_pontos_de_partida_entram_todos_na_contagem_da_base`) segue igual.
- Mutantes novos apontam as linhas certas: M3 em :526 (`for mb in "${lista_mb[@]}"; do`), M4 em :533 (`if [ -s "$tmp2b/comuns" ]; then` → `if false`) e M5 em :536 (o `die` do arquivo em comum → `:`); cada trecho `de` casa uma vez só no arquivo (`grep -cF` = 1). M4 e M5 são mortos por `test_c5_base_que_andou_com_arquivo_em_comum_para_antes_do_pr`, que afirma rc 1 e a lista `["  b"]`: M4 pula a lista e o `die` (rc 0), M5 lista e segue (rc 0).
- Com a volta 2, as guardas de :525-537 têm mutante: :526 (M3 da 2.ª spec), :527 e :528 (M1, M2 da 2.ª spec), :529-531 (o cruzamento, M5 da 1.ª spec), :533 (M4), :536 (M5) e :538 (contagem, M4 da 1.ª spec); :525 só inicializa os arquivos.

## Ferramentas (citadas, não refeitas à mão)
- `bin/forge-mutante tests/mutantes/lote-fechar2-2.json` (rev `7c926e42a3a6`): M1 :527, M2 :528, M3 :526, M4 :533, M5 :536, todos `morreu`, rc=0.
- `python3 -m unittest tests.test_fechar_base_andou`: `Ran 17 tests in 9.224s` / `OK`.
- `shellcheck bin/forge-fechar`: rc=0, sem aviso.
- Teto M14: 179 linhas de código e teste (`ci.yml` 2, `bin/forge-fechar` 32, `tests/test_fechar.py` 52, `tests/test_fechar_base_andou.py` 93); specs de mutantes, changelog e pareceres ficam fora. Sem `hooks/` e sem caminho protegido.
- `docs/engineering/achados-recorrentes.md` (PA-7): lista vazia, nada a conferir.
- Segurança e QA: pareceres próprios (E2.1, E3.1), que não refaço aqui.

## Parecer
Aprovado. O teste criss-cross separa os dois pontos de partida por arquivo e mata o mutante do laço em qualquer ordem, e os mutantes M4 e M5 da segunda spec caem nas linhas :533 e :536 com o teste que exercita a rota. A3 e A4 são recomendações e não devolvem a entrega.
