---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-versao-com-20
commit: 2e6da2d5b9a7cf5d9a7a35bb7319b4b23a28b894
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 versão com 20 itens (#928, E36.12; volta 2 por delta, b19c7f53..2e6da2d5)

Delta lido por `forge-check parecer delta`: uma linha em `tests/config.json:849`. A chave de `invariantes_motivo_trecho` de `templates/projeto/CLAUDE.md` passa ao texto do invariante novo (linha 656, "a versão fecha quando a branch de integração soma 20 itens integrados, sem versão por dia") com o porquê novo (A2 da segurança). `grep`: a chave é idêntica ao invariante e ao texto de `templates/projeto/CLAUDE.md`; "até 2 por dia" não resta em `tests/config.json`.

- ci: 2e6da2d5b9a7cf5d9a7a35bb7319b4b23a28b894 verde (`gh pr checks 928`, head conferido por `gh pr view`: suíte 3.12 e 3.14 partes 1 a 5, passos, verificações longas, instalação e teto de pulados verdes; só `bateria`, `bateria (pareceres)` e `catraca` esperam os pareceres)

## Revalidação do achado anterior
- A3 (recomendado, volta 1): resolvido. O invariante novo tem motivo próprio; a chave velha saiu.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Invariante do modelo de projeto tem motivo com a chave do texto atual | `tests.test_forge -k invarian -k motivo` (4 testes, sob flock da trava) | chave sem trecho correspondente | passou |
| Demais critérios das voltas anteriores | sem mudança no delta | n/a | mantidos |

Não rerrodei a suíte: CI do head lido (G3). Linha só de metadado de teste: sem mutante aplicável.
