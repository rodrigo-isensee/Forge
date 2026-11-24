---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0480-d3-teste-enfraquecido
commit: 23026d32d43b1139c5eac2bf3529a8bd2b47ff2b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 E2.6 (D3, catraca recusa teste afrouxado; PR #867), revalidação por delta

Delta revisado: `8daa1611..23026d32` (`forge-check parecer delta`: "revalida: sim (desatualizado: tests/test_catraca.py mudou depois do parecer)"). Código: só `tests/test_catraca.py` +1/-1 (`assert 1` por `assert self` em `test_d` de `test_acrescimos_ajudante_e_arquivo_fora_de_tests_passam`); o resto do delta são os pareceres de QA, segurança e review da rodada anterior, sem código. H1: dentro do teto.

## Ferramenta (citada, sem refazer)
- CI do PR (#867) na leitura: `catraca` vermelha só por `R-CONFORMIDADE: mudança em tests/catraca.py` (rótulo do dono); `bateria (pareceres)` vermelha pela falta dos pareceres no head; suíte em andamento, o merge espera o verde.
- Mutação do delta rodada aqui: `bin/forge-mutante --processos 1 tests/mutantes/v0480-d3-teste-enfraquecido-2.json` no head 23026d32: 8 mutantes, todos mortos (D3B1 a D3B8), incluindo D3B1 (`tests/catraca.py:750`) e D3B5 (`tests/catraca.py:709`), os sobreviventes do A1 do QA.
- Testes do item: `python3 -m unittest tests.test_catraca.TestesAfrouxados tests.test_catraca.TestesNoCi`: 41 testes, OK.

## Leitura
- A1 do QA corrigido: `assert 1` é asserção só de constantes (`_vacua`) e deixou de contar depois do delta anterior, então `test_d` não exercitava mais o caminho de acréscimo com asserção; `assert self` tem nome e conta, o que devolve ao teste o poder de matar D3B1 e D3B5. A intenção do caso (teste novo acrescentado passa) segue a mesma.
- O A1 recomendado da rodada anterior (`msg=` contado como argumento em `_so_constantes`) não é tocado por este delta e segue como cartão depois do merge.

## Parecer
Aprovado no head 23026d32: a troca é mínima, mata os dois mutantes sobreviventes da spec -2 e não quebra os testes do item.
