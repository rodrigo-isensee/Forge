---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/teste-heredocs-orcamento-estavel
commit: a97ea358e0bde9f726e6eb1f41f0849e7fdaa23e
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-04
---
# QA: teste-heredocs-orcamento-estavel

## Achados
- A1 (bloqueante) tests/test_hooks.py:1872 · 2 de 5 rodadas falharam sob carga: o hook recusa por prazo de parede (e23-01), então medir CPU não basta; a forma `python3 - a{i}` (2,0 a 2,2 s) fica perto do teto de 3 s.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orçamento estável sob carga | test_muitos_heredocs_recusam_dentro_do_orcamento x5 | razão 3 contra controle de 1000 e metade do timeout | falhou (3 OK, 2 falhas) |
| Mutante quadrático reprovado | e23-mutante.sh | quadrático | passou (morreu; rc=0) |

## Cenários e resultado real
- Módulos curtos: test_fechar_corrida_rotulo (7), test_fechar_orfao (18), test_hooks_volta_propriedades (9): OK.
- Estabilidade (load ~6,7): rodadas 1 e 4 FAIL, 2, 3 e 5 OK; 38 a 51 s cada; CPU 1,1 a 2,2 s, controles 0,4 a 0,8 s (razão máx. ~2,9).
- Mutante: falhou em duas formas (sh -s, python3 - a{i}), rc=0.
- test_hooks inteiro: 71 testes, OK (1 skip pré-existente), 924 s, rodado junto das outras medições.
