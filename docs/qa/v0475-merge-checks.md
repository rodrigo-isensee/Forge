---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: 9f497b0f140a450c578dae79e5ec00d88d3ff31c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0475-merge-checks (E3.45, parecer E3.72)

## Achados
- A1 (recomendado) bin/forge-check:1478 · `gh pr view` que falha (sem gh ou rede) devolve None e o `pr` aprova sem conferir os checks (falha aberta); coerente com o texto do item, mas sem aviso no stderr.

## Critério → teste → resultado
O item E3.45 não tem `CA-n`; os critérios saem do texto do item e do fragmento do changelog.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1: PR aberto, fora do rascunho, no head: check pendente, vermelho ou cancelado reprova com a lista | `tests/test_forge_check_pr.py` (23 testes) | bucket fora de pass/skipping; rascunho; outro head; `--previo` | passou |
| C2: exigido ausente ou fora de pass reprova (ruleset, proteção, pares do Forge só no Forge) | `test_forge_check_pr.py` | ausente; resposta de forma inesperada ou 404 não acrescenta | passou |
| C3: `forge-fechar` soma os exigidos do destino sem tirar os pares | `tests/test_forge_fechar.py` (5), mutantes M14 a M17 | ruleset ilegível; curinga `*` | passou |
| C4: mapa do `forge-testes` e tamanho | `test_testes_tocados.py` (162, 1 skip herdado), `test_forge_tamanho.py` (23) | módulo novo no mapa | passou |

## Cenários e resultado real
- Locais com TMPDIR: os quatro módulos acima, todos OK. A suíte inteira roda só no CI do PR; não há PR aberto nem check-run `bateria` deste sha, então não a cito.
- Vermelho antes do verde: não rodei `forge-testes --vermelho`; a prova é por mutação (19 mutantes mortos). Registro como limite.
- Mutação (`bin/forge-mutante`, 3 specs, `--processos 2`): M1 a M19 todos `morreu` (M5 morreu por erro do teste declarado sob o mutante, que passa sem ele).
- Cobertura (`--cobertura --base 3d8ad440`): toda condição Python mudada em bin/forge-check tem mutante; `spec editada · i4-checks-exigidos.json`; `não coberto: bin/forge-fechar` (shell; M14 a M17 cobrem à mão as linhas 522, 536, 537 e 1275).
- Sondei à mão a leitura que falha (gh ausente, `contexts` nulo): cai nos `except` sem erro.

## Bugs
Nenhum aberto.
