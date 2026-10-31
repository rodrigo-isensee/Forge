---
tipo: qa
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: 7f5a1f85ed83e0b21503f387acc8a0753b13a6e6
parecer: reprovado
revisor: qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: impl-forge-check-a (branch a1: E1 e E2)

Reprovado só pela prova de mutação (`R-QA`): o diff muda guardas de `bin/forge-check` sem spec de mutantes do autor, e a spec que o QA escreveu deixou sobreviventes que provam lacuna de teste. Comportamento, vermelho e M14 estão certos.

## Achados
- A1 (bloqueante) bin/forge-check:802 · mutante M13 sobrevive: tirar `arquivo_existe(achado)` do laço das raízes não derruba teste; falta teste de pedido relativo que só existe na 2ª raiz (a 1ª não o tem).
- A2 (bloqueante) tests/mutantes/impl-forge-check-a.json:1 · o diff muda 10 condições Python de bin/forge-check sem mutante declarado (`forge-mutante --cobertura` lista as 10); o autor declara a spec, um mutante por guarda (M14 de lote de controle).
- A3 (recomendado) bin/forge-check:989 · mutante M15 sobrevive: `bool(arquivo)` sem teste direto de `mesmo_pedido` com arquivo vazio e Pedido igual ao cwd; só atinge chamada sem `caminho`, que o CLI não faz.

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
- `python3 -m unittest tests.test_forge.EntregasParalelas tests.test_forge.CaminhoDoPedido`: Ran 16, OK no head. Suíte inteira não rodada aqui (o pre-push e o CI a rodam, M8).
- Vermelho, manual: `bin/forge-testes --vermelho 234dbe0` passou do prazo de 10 min sem veredito (rc 124, vale como "sem veredito", não como vermelho). Em cópia do head com `bin/forge-check` da base, os 8 testes novos: `FAILED (failures=12, errors=1)`, incluindo `AttributeError: module 'forge_check_teste' has no attribute 'mesmo_pedido'`; no head, `OK`. O teste do brief sem `Pedido:` passa também na base: ele guarda a regressão do commit intermediário, não a base.
- M14: bin/forge-check +39 -7 e tests +94 -2 (142 linhas pelo numstat, teto 150; um comportamento só, caminho do Pedido; sem hooks): cumpre.
- Mutação (spec do QA, 15 mutantes em cópia, `forge-mutante`): morreram M1 a M9, M14 e M11 (re-rodado com o teste C1 certo; a primeira lista o deixava de fora por erro meu). Sobrevivem M13 e M15 (A1, A3). Equivalentes, justificados: M10 (`caminhoso and is_absolute` no retorno cedo: o laço seguinte devolve `dado` igual para caminho absoluto) e M12 (`ValueError` de `arquivo_existe`: argv não carrega NUL; o NUL do brief passa por `mesmo_pedido`, coberto).
- Casos de abuso do modelo de ameaças da branch: cobertos pelos testes acima (travessia, link, `~usuario`, NUL, homônimo, quebra de linha).

## Veredito
Reprovado por A1 e A2; a correção é teste e spec do autor, sem mudar código de produção. Revalidação por delta sobre esses dois pontos.
