---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-sessao-por-pedido
commit: ec886a821cc5a901f9c8282b607fc618c4377076
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-sessao-por-pedido

Etapa E2.328 do pedido v047 (FILA-13 T-5, entrega E2.318). Parecer completo: não havia parecer anterior. Diff `1b88640e...ec886a82`: `docs/economia-de-tokens.md` 1+1, `tests/test_sessao_por_pedido.py` 29+0, `changelog.d/v047-sessao-por-pedido.md` 2+0; 30 linhas de código e teste, dentro do teto M14, um comportamento só (marco da regra 9).

## Achados
- A1 (recomendado) docs/economia-de-tokens.md:14 · "T-5" cita um ID de estudo que não existe neste repositório (a decisão de 2026-10-16 está no estudo de tokens do operador, fora do Forge); o leitor da fábrica não chega à fonte. Sugestão: dizer "uma sessão por pedido" sem o ID ou citar a fonte versionada.

## Sondas

## Parecer
Aprovado. A regra 9 ganha o marco "fim do pedido com a retrospectiva gravada", como pede o E2.318 e a decisão do dono de 16/11 (FILA-13 só T-5); a decisão de origem da T-5 tem a data citada (2026-10-16, conferida no estudo de tokens). A medida por pedido usa um comando que existe (`forge-check transcricao custo --pedido ID`, usage de `bin/forge-check`:10) e coincide com a da regra 12; o critério de volta do marco é observável (decisão reaberta ou pergunta repetida ao dono), como pede `R-DECISAO`. Nada de guarda no diff (só texto): sem mutante a declarar. O teste lê a regra pela âncora (`tests/apoio_regra_id.py`), não a frase inteira, e cobre marco, medida e volta. `python3 -m unittest tests.test_sessao_por_pedido`: 3 testes, OK. Suíte inteira: fica no CI do PR. Não há `docs/engineering/praticas.md` no Forge; checklist da skill lido. Nenhuma classe repetida de `docs/engineering/achados-recorrentes.md`: sem linha AR nova. Fragmento de changelog presente.
