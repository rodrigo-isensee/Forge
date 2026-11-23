---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-modelo-pedido-brief
commit: 83246fbf4c5ec96f5e9caeb114084f6089289423
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-modelo-pedido-brief (E86.3)

Entrega: o modelo de pedido traz a etapa de retrospectiva, a etapa por delegação e a marca `(outro repositório)`; `checagem-do-brief` ganha `por-tema.md`; o fluxo do pedido manda conferir `git status -sb` na worktree. Sem suíte local; só os testes dos arquivos tocados.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Modelo traz a retrospectiva (agile-coach) | `test_modelo_de_pedido_ja_traz_a_retrospectiva_em_etapas` | etapa dentro de `## Etapas` | passou; vermelho na base |
| Uma etapa por delegação | `test_modelo_de_pedido_pede_uma_etapa_numerada_por_delegacao` | n/a | passou; vermelho na base |
| Dois repositórios com a marca da ferramenta | `test_pedido_com_dois_repositorios_usa_a_marca_que_a_ferramenta_le` | marca literal | passou; vermelho na base |
| Checagem lê o `por-tema.md`, cada tema, sem termo só do Forge | `test_checagem_manda_ler_o_por_tema_e_ele_traz_cada_tema` | termos só do Forge | passou; vermelho na base |
| Worktree conferida com `git status -sb` | `test_onde_se_cria_a_worktree_se_confere_a_branch_logo_depois` | n/a | passou; vermelho na base |
| Tetos de texto | `test_orcamento_instrucao` (8), `test_metricas_texto` (2), `test_jarvis_nucleo` (43) | teto de instrução | passaram |
| Projeto novo recebe o modelo | `bin/forge-init` em repositório vazio | n/a | passou |

## Cenários e resultado real
- `test_modelos_projeto`: 25 testes, OK (`python3 -I -m unittest discover -s tests -p test_modelos_projeto.py`, TMPDIR via mktemp).
- Vermelho antes do verde: `bin/forge-testes --vermelho <base>` com plano completo (37 módulos) estourou meu prazo de 550 s no módulo 12 (rc=124, sem veredito, não vale como vermelho). Troquei pela forma de projeto: cópia do head em `$TMPDIR` com os 5 arquivos de texto revertidos à base `ad3b3b6f` e o por-tema removido. Resultado: `Ran 5 tests ... FAILED (failures=5)`; os 5 testes da classe `ModeloPedidoEBrief` caem.
- Mutantes: `bin/forge-mutante tests/mutantes/v0479-modelo-pedido-brief.json tests/mutantes/v0479-modelo-pedido-brief-2.json`: M1, M2, M3, M4, M5, M6, M7, M9, M10 `morreu`; rc=0, nenhum sobrevivente (9 mutantes).
- `forge-init` em repositório novo: `docs/pedidos/_modelo.md` traz `E1.4 (agile-coach): retrospectiva do pedido` (linha 41) e a marca `(outro repositório)` (linha 37).
- Nenhum teste com `skip`.
