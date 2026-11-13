---
tipo: qa
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-worktree-jarvis
commit: c61435e6efaa446b3c73bb4504ea6e1cf60ca06c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: mp1311-worktree-jarvis

Item 12 do pedido melhorias-de-projeto-1311 (E2.20): o Jarvis cria a worktree na própria sessão antes de delegar; clone local como saída.

## Achados
- A1 (recomendado) agents/jarvis.md:40 · o passo 4 perdeu a menção ao ID Z10 ("uma escrita por branch, Z10"); a regra segue na skill, mas o agente deixou de citar o ID.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Jarvis cria a worktree antes de delegar | `WorktreeAntesDeDelegar.test_o_jarvis_cria_a_worktree_antes_de_delegar` | passo 4 do agente | passou |
| Brief avisa worktree alheia só leitura e oferece `update-branch` | `test_a_skill_manda_avisar_no_brief_e_oferece_o_caminho_pelo_github` | texto da skill | passou |
| Clone local como saída, em `~/.forge-contrib/wt/<nome>-c`, da `origin/develop` | `test_a_skill_da_o_clone_local_como_saida_quando_a_worktree_nao_grava` | texto da skill | passou |
| Cortes de redação não tiraram regra | leitura do diff + `tests.test_jarvis_nucleo` (20) e testes de invariantes | `R-BRIEF`, `R-PROVA`, `R-REVIEW` ainda citados | passou |

## Cenários e resultado real
- Cortes conferidos linha a linha: saiu "(padrão `node-react`)" (stack fixa, ganho de neutralidade, `R-NEUTRO`), "gerado", "Ele não confere forma", "Em seguida"/"Depois", "executor genérico" abreviado. Nenhuma regra com ID saiu; `R-BRIEF`, `R-PROVA`, `R-REVIEW` e o limite de 10.000 caracteres seguem na skill. Só o ID Z10 saiu do agente (A1).
- Vermelho antes do verde: com `agents/jarvis.md` e a skill da base (efe7c9e8), `python3 -m unittest tests.test_jarvis_nucleo` dá `FAILED (failures=3)` (os 3 testes novos); no head, `Ran 20 tests ... OK`. Feito por troca manual dos dois arquivos numa cópia, não por `forge-testes --vermelho`.
- Rodado no head: `tests.test_jarvis_nucleo`, `test_jarvis_n_jar_a`, `test_invariante_gatilho`, `test_skills_v0442`, `test_pesos_teto`, `test_permissao_agentes_md`, `test_aq1_texto`: 16 + 20 OK. Suíte inteira não rodada local (carga); sem PR aberto, não há check-run `bateria`.
- Mutação: sem ferramenta de mutação para texto de agente/skill; não aplicável (não toca `bin/`, `hooks/`, `.githooks/`).

## Delta até c61435e6 (E2.24)
- O commit c61435e6 restaura em `skills/briefs-e-conferencia/SKILL.md` a frase "Leia a skill `checagem-do-brief`" e tira ", selado como qualquer outro" do brief de volta (já dito no passo 4). Nenhuma regra com ID saiu.
- Vermelho antes do verde: com a skill do b94e026e, `python3 -m unittest tests.test_modelos_projeto.ChecagemDoBrief` dá `Ran 7 tests ... FAILED (failures=1)`; no head, `OK`. Troca manual do arquivo numa cópia.
- No head: `ChecagemDoBrief`, `test_jarvis_nucleo`, `test_pesos_teto`, `test_invariante_gatilho`, `test_skills_v0442`: `Ran 34 tests ... OK`. Suíte inteira não rodada local; sem check-run `bateria` consultado.
- Mutação: texto de skill, não aplicável. A1 (recomendado) segue aberto, sem bloqueio.
