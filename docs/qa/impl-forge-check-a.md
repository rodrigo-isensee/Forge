---
tipo: qa
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: 104ec9e812e41c8fac700374beab1750fa91ffe8
parecer: aprovado
revisor: qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-forge-check-a (branch a1: E1 e E2)

Aprovado no head 104ec9e. Os dois bloqueantes do parecer anterior (7f5a1f8) estão fechados: A1 pelo teste do pedido relativo só na 2ª raiz (b6187cd), A2 pela spec de mutantes do autor (9921391, db6c9de, d591bcc). A3 (recomendado) virou o M9 da spec e morre.

## Achados
- A1 (recomendado) bin/forge-check:988 · `forge-mutante --cobertura` lista `valor.startswith('~/')` como "sem mutante", mas o M8 da spec muta exatamente essa linha e morre; falha da heurística da ferramenta, não da spec.

## Delta lido (revalidação)
`forge-check delta`: intervalo 7f5a1f8..104ec9e; só `tests/mutantes/impl-forge-check-a.json` (+146) e `tests/test_forge.py` (+8: linhas 4909 e 4925-4931). `bin/forge-check` não mudou no delta. Li os dois; o diff inteiro de `bin/forge-check` contra a base segue o já avaliado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 / FC-ENTREGA-PEDIDO-CAMINHO: Pedido por caminho vale só pelo realpath do pedido (abs, `~/`, link, -REV) | EntregasParalelas.test_pedido_do_brief_por_caminho_vale_so_pelo_realpath_do_pedido_conferido | homônimo noutra pasta, link para outro pedido, `~usuario`, NUL, Base-sha diferente | passou |
| E1 / `~/` e relativo | EntregasParalelas.test_pedido_do_brief_com_til_e_relativo_so_valem_na_forma_certa | `./`, `../`, `~/` duplicado | passou |
| E1 / A1 do review: sem linha `Pedido:` reprova sem Traceback | EntregasParalelas.test_brief_sem_a_linha_pedido_reprova_com_linha_limpa | valor ausente | passou (guarda; ver vermelho) |
| E1 / `~outro` nunca expande | EntregasParalelas.test_til_de_outro_usuario_nunca_expande | getpwnam dublê | passou |
| E2 / FC-PEDIDO-CAMINHO-DUPLO: sem `docs/pedidos/` nem `.md` em caminho completo; raiz só em docs/pedidos | CaminhoDoPedido (4 testes) | travessia, link para fora, inexistente, quebra de linha rc 2 | passou |
| E3, E4 | fora desta branch (a2, a3) | n/a | n/a |

## Execução real
- `python3 -m unittest tests.test_forge.EntregasParalelas tests.test_forge.CaminhoDoPedido`: Ran 17, OK no head. `scripts/validar-plugin.sh`: Validation passed. Suíte inteira não rodada aqui (pre-push e CI, M8).
- Vermelho: mantido do parecer anterior (testes novos falham com `bin/forge-check` da base: `FAILED (failures=12, errors=1)`, `AttributeError ... 'mesmo_pedido'`; no head, OK). Os dois testes novos desta volta (cwd vence, 2ª raiz) matam M3 e M5 na rodada abaixo.
- Mutação, `bin/forge-mutante tests/mutantes/impl-forge-check-a.json`, rc=0: M1 a M10 todos `morreu` (linhas 793, 795, 797, 799, 802, 983, 985, 988, 989, 1011); sem equivalente declarado.
- `forge-mutante --cobertura --base 234dbe0`: rc 0, cobre as condições do diff; única linha "sem mutante" é a 988, coberta pelo M8 (ver A1).
- M14: bin/forge-check +39 -7 e tests +94 -2 na entrega original; o delta desta volta só soma teste e spec de mutantes (+154 linhas fora do corte de produção). Um comportamento só, sem hooks: cumpre.
- Casos de abuso do modelo de ameaças: cobertos pelos testes da tabela (travessia, link, `~usuario`, NUL, homônimo, quebra de linha).

## Veredito
Aprovado. Nenhum bloqueante aberto; bugs zero.
