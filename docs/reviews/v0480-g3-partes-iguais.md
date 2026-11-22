---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-g3-partes-iguais
commit: 4c0b3842edfc6916e013bc5fcef7f749a094493f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E102.5, revalidação do reequilíbrio das partes da suíte do CI)

Base 2d73a35e, head aprovado anterior: nenhum (8979faa4 reprovado), head 4c0b3842. Classe T; este review é o único portão de código.

## Delta lido
`forge-check parecer delta docs/reviews/v0480-g3-partes-iguais.md`, intervalo 8979faa4..4c0b3842, no domínio: `changelog.d/v0480-g3-partes-iguais.md`, `tests/pesos-d4.json`, `tests/test_hooks.py`. Nada fora disso relido.

## Achados
- A3 (recomendado) tests/pesos-d4.json:138 · As 4 fatias de test_fixtures somam 211 s e as do T1 157 s, cerca de metade dos 416 s e 337 s da unidade inteira em segundos reais (224 e 181 / 0,5377): a medida das fatias parece de outra fonte. Não fura o teto (maior fatia 54,5 s); regravar no próximo --medir do CI. Cartão.

## O que foi conferido
- A1 resolvido: a escala saiu. Os pesos das chaves antigas são os de 8979faa4 divididos por 0,5377 (test_catraca 88,3 para 164,2; test_atualizar 53,0 para 98,6); a soma vai de 3004 (base) a 4984. Maior unidade: `test_hooks` (resto do módulo), 195,2 s, abaixo dos 225 s. `test_fixtures` e o T1 viraram 4 métodos cada, com chave própria.
- A2 resolvido junto: pesos em segundos, a mesma unidade que `gravar_pesos`/`--medir` gravam.
- Fatias: `fixtures_da_fatia` (`i % 4`) e `corpus[k::4]` repartem sem sobra nem repetição, e cada fatia afirma que não está vazia; as asserções por caso são as mesmas. O piso do T1 por fatia é o teto de 500·V/4, cuja soma nunca é menor que o piso do teste inteiro. `verificar_*` não começa por `test`, então não é coletado duas vezes.
- Chaves removidas da base: só as duas dos testes que deixaram de existir. As classes de `test_selo_e_entrega` têm chave própria e o resto do módulo fica em 0,0 (`planejar`, `scripts/suite-paralela.py:178`, só cria unidade com teste). O diff não toca `scripts/` nem `.github/`.
- Rodados (ambiente limpo, `python3 -I`): `test_pesos_teto` 2 OK, `test_suite_partes` 49 OK, `test_pesos_do_ci` 16 OK; `test_fixtures_as_fatias_cobrem_todas`, `test_t1_as_fatias_cobrem_todo_o_corpus`, `test_fixtures_fatia_2` e as 4 fatias do T1 OK. As fatias 1 e 3 ficaram verdes, com subtestes pulados pelo sandbox (pid). A fatia 4 falhou num caso só, `pesado/mesma-sessao-libera`, por `TimeoutExpired` de 120 s do hook `pesado` neste sandbox; o mesmo caso falha igual em `test_fixtures_do_v0442`, que o diff não toca: é do ambiente, não da divisão. Decide o CI.
- Suíte inteira: só no CI do PR (`R-REVIEW`); não rerrodada aqui.

## Parecer
Aprovado. A1 e A2 foram resolvidos: os pesos voltaram a segundos reais e as duas unidades acima do teto foram divididas sem perder caso nem asserção, com teste de cobertura da união. A3 vira cartão depois do merge.
