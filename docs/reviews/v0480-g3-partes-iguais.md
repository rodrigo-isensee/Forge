---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g3-partes-iguais
commit: 790f114d38117b7da7232f9b7b94f98c945d03aa
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E102.9, revalidação da segunda volta do reequilíbrio das partes da suíte do CI)

Base 2d73a35e, head aprovado anterior 4c0b3842, head 790f114d. Classe T; este review é o único portão de código.

## Delta lido
`forge-check parecer delta docs/reviews/v0480-g3-partes-iguais.md`, intervalo 4c0b3842..790f114d, no domínio: `changelog.d/v0480-g3-partes-iguais.md`, `tests/test_hooks.py`. Nada fora disso relido.

## O que foi conferido
- A1 do QA resolvido: o corte do T1 é uma função só, `corpus_da_fatia(k)` (`tests/test_hooks.py:2682`), chamada pelas fatias (`verificar_t1_da_fatia`) e pelo teste de cobertura; mudar o corte quebra a cobertura.
- A2 do QA resolvido: `test_fatias_travadas_aos_metodos` conta os métodos `test_fixtures_fatia_*` e `test_t1_fatia_*` contra `FATIAS_DE_FIXTURES` e `FATIAS_DO_T1`. Os prefixos não pegam `test_fixtures_as_fatias_cobrem_todas` nem `test_t1_as_fatias_cobrem_todo_o_corpus`.
- Rodados (`env -i`, `python3 -I`): `test_fatias_travadas_aos_metodos` OK e `test_t1_as_fatias_cobrem_todo_o_corpus` OK.
- Mutantes, numa cópia em `$TMPDIR`: `FATIAS_DO_T1 = 5` derruba `test_fatias_travadas_aos_metodos` (FAILED, failures=1); o corte `[k::FATIAS_DO_T1 + 1]` em `corpus_da_fatia` derruba `test_t1_as_fatias_cobrem_todo_o_corpus` (FAILED, failures=1).
- Changelog: uma linha nova no mesmo fragmento, sem editar o `CHANGELOG.md`.
- A3 do parecer anterior (pesos das fatias) segue como cartão; o delta não toca `tests/pesos-d4.json`.
- Suíte inteira: só no CI do PR (`R-REVIEW`); a branch ainda não tem PR nem run, então não há CI para citar.

## Parecer
Aprovado. O corte do T1 tem uma fonte só e as constantes de fatias ficaram presas ao número de métodos; os dois testes novos falham com os mutantes.
