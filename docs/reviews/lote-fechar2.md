---
tipo: review
contrato: 1
pedido: lote-fechar2
branch: melhoria/lote-fechar2
commit: a35a18171fd920286e73c511dfe5c5d0cfb897f6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: lote-fechar2

Base `b6eb84fed86e3b5289f3950b33d43a86f34343c2`, head `a35a18171fd920286e73c511dfe5c5d0cfb897f6`. Revalidação 5, por delta sobre o parecer `30bd51b` (head `5c6684d`): voltas 4 e 5 (`a356288`, `a35a181`), SC2015 do shellcheck do CI.

## Achados
- A3 (recomendado) bin/forge-fechar:523 · `mapfile` é o primeiro uso de recurso do bash 4 no repositório; o script já depende de `sort -z` e `comm -z` do GNU, então não é regressão prática, mas vale uma linha no comentário do cabeçalho (fora da volta por decisão técnica de 2026-10-26 17:13; segue informativo)
- A4 (recomendado) bin/forge-fechar:526 · com dois pontos de partida, o laço junta os diffs de cada lado antes de cruzar: no criss-cross, arquivos iguais nos dois lados saem como em comum e o 2b para (falha segura); cruzar por ponto de partida resolveria, em cartão próprio

## Revalidação por delta
- Delta lido (`forge-check delta --parecer docs/reviews/lote-fechar2.md`, intervalo `5c6684d..a35a181`): `bin/forge-fechar`:80, :177, :337 e :750; `tests/test_fechar.py`:613-630; `tests/mutantes/lote-fechar2-4.json`:1-46; `changelog.d/lote-fechar2.md`:5. Os outros arquivos do intervalo são pareceres.
- Já lido nos pareceres `f10ec5b`, `308158f` e `30bd51b`, sem mudança no delta: o resto de `bin/forge-fechar` (inclusive :520-540), o resto de `tests/test_fechar.py`, `tests/test_fechar_base_andou.py`, as specs `lote-fechar2.json`, `-2.json` e `-3.json` e `.github/workflows/ci.yml`.
- As quatro reescritas (`A && B || C` → `if ! { A && B; }; then C; fi`) têm o mesmo comportamento em cada ramo: A e B verdadeiros, C não roda nas duas formas; A ou B falso, C roda nas duas. C é `die` (:80, :177, :750, sai com erro) ou `continue` (:337, dentro do laço dos checks, mesmo laço). Com `set -euo pipefail` (:35), a falha de A ou B não dispara o errexit em nenhuma das formas (lista `&&` e condição de `if`). Nenhuma das quatro tinha C capaz de devolver falso que mudasse o fluxo.
- `test_fechar_sem_a_e_b_ou_c_solto`: troca o texto entre aspas por `""`, colapsa grupos internos (`$(...)`, `(...)`, `{ ...; }`, `[[ ... ]]`, `[ ... ]`) até ponto fixo e acusa `&&` seguido de `||` no que resta. Sonda própria (13 casos): pega a forma solta com `[`, `[[` e comando simples; não acusa grupo `{ A && B; } || C` (:82), `if ! { ...; }`, atribuição `x="$(a && b)" || die` e sem aspas (:180), subshell `(cd && ...) || die` (:187), texto entre aspas simples ou duplas, `[[ a && b || c ]]` e `$(( ))`. Linhas da fonte com `&&` e `||` hoje: :82, :141 (awk entre aspas simples), :180 e :187, todas descartadas com razão. Ponto conservador: `a && b; c || d` na mesma linha também é acusado (não existe na fonte; falha para o lado seguro, sem achado).

## Ferramentas (citadas, não refeitas à mão)
- `bin/forge-mutante tests/mutantes/lote-fechar2-4.json` (rev `a35a18171fd9`): S1 :337, S2 :80, S3 :177, S4 :750, todos `morreu`, rc=0.
- `python3 -m unittest tests.test_fechar`: `Ran 87 tests in 44.421s` / `OK`.
- `shellcheck bin/forge-fechar` (local 0.11.0): rc=0, sem aviso. O SC2015 do 0.9 do runner fica com o CI do PR e com o teste de fonte acima.
- Teto M14: 238 linhas de código e teste (`ci.yml` 2, `bin/forge-fechar` 40, `tests/test_fechar.py` 70, `tests/test_fechar_base_andou.py` 126); specs de mutantes, changelog e pareceres ficam fora. Sem `hooks/` e sem caminho protegido.
- `docs/engineering/achados-recorrentes.md` (PA-7): lista vazia, nada a conferir.
- Segurança, QA e devops: pareceres próprios (E2.1, E3.1, E4.1), que não refaço aqui.

## Parecer
Aprovado. As quatro linhas reescritas mantêm o comportamento de cada ramo, o teste de fonte pega a forma solta sem falso positivo em grupo, atribuição e subshell, e S1 a S4 morrem. A3 e A4 seguem recomendações e não devolvem a entrega.
