---
tipo: qa
contrato: 1
pedido: vel-p1p10
branch: melhoria/vel-p1p10
commit: 9e191c78b4dbed14aa439122ade1f86bcb955a57
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: vel-p1p10

Lote VEL-P1P10 (E1 a E4): teto de 150 linhas e um comportamento por PR, mutante equivalente declarado e 16 mutantes por spec no `bin/forge-mutante`, verificadores do autor antes do push. Pedido sem especificação de UX: as obrigações são os itens E1 a E4 do pedido e `R-QA`. Sem interface, sem teste E2E nem de acessibilidade (`n/a`). Parecer só sobre o commit final, em paralelo com review e segurança (decisão ACELERA-RODADA, item 4).

## Achados
- A1 (recomendado) bin/forge-mutante:271 · a justificativa do equivalente sai na linha sem filtrar caractere de controle (so `split` normaliza espaço); spec versionada pelo autor, risco baixo; não devolve

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 teto 150 no jarvis | tests.test_forge.TetoPorPr.test_teto_de_150_linhas_tambem_no_jarvis | sem "400 linhas" residual | passou |
| E1 teto 150 e um comportamento no tech-lead e na skill | TetoPorPr.test_teto_de_150_linhas_e_um_comportamento_por_pr_no_tech_lead_e_na_skill | número exato, sem 400 | passou |
| E2 limite 16 por spec | test_forge_mutante.ValidacaoDaSpec.test_de_um_a_dezesseis_mutantes | 0, 16, 17 | passou |
| E2 limite 16 em várias specs | ...test_varias_specs_..._teto_de_16 e Execucao.test_mais_de_dezesseis_mutantes_sai_2 | 17 por spec | passou |
| E2 equivalente válido sem testes | ValidacaoDaSpec.test_equivalente_declarado_com_justificativa_e_valido_sem_testes | sem `testes` | passou |
| E2 equivalente sem justificativa reprova | ValidacaoDaSpec.test_equivalente_sem_justificativa_ou_com_testes_e_invalido; Execucao.test_equivalente_sem_justificativa_barra_a_spec_antes_de_rodar | vazio, 12 caracteres, só espaço, None, número, com `testes`, sem a chave | passou (rc 2, "nada foi executado") |
| E2 equivalente não roda nem dá rc 1 | Execucao.test_equivalente_declarado_nao_roda_nao_da_rc_1_e_sai_na_linha_propria | linha `equivalente: <id> · <just>` | passou |
| E2 trecho ausente ou repetido | Execucao.test_equivalente_com_o_trecho_ausente_ou_repetido_sai_2 | 0 e 2 ocorrências | passou |
| E3 verificadores do autor | tests.test_forge.VerificadoresDoAutor | tech-lead e 2 agentes de stack | passou |

## Cenários e resultado real (revalidação sobre 9e191c7: volta 2 cf04778 e merge da develop a55ec03)
- `python3 -m unittest tests.test_forge tests.test_forge_mutante`: 517 testes, OK (143 s).
- Volta 2, `TetoPorPr.test_a_skill_de_qa_divide_a_spec_no_mesmo_limite_que_a_ferramenta` (A1 do review): vermelho provado com `skills/qa-testing/SKILL.md` de 8757265 numa cópia em `$TMPDIR`: `AssertionError: 'Pedido com mais de 16 mutantes divide' not found`, FAILED (failures=1); no HEAD passa. `grep` de `400 linhas`, `mais de 8 mutantes` e `3 a 8` em agents, skills, stacks, bin, docs/regras e templates: vazio.
- `bin/forge-mutante tests/mutantes/vel-p1p10.json` sobre 9e191c7: M1, M2, M3, M5, M6, M7, M8, M9, M10, M11, M12, M13 todos `morreu`, rc=0.
- `bin/forge-mutante --cobertura --base a55ec03113ecf83cc59a8f48dae1f4204dda549e`: rc 0; sete condições mudadas (225, 226, 242, 243, 271, 559, 562) todas `coberta` (M5, M13, M11, M3, M6, M12, M7), "declarado, não provado"; conferi contra o diff da base a55ec03: sem linha de guarda sem mutante, sem isenta.
- Merge da develop: sem conflito de código além da linha AR (AR-9 `limite-antigo-no-texto` gravada pelo review); a suíte dos dois módulos verde sobre o merge.
- Itens do PA-7 conferidos: neutralidade, `git add` explícito, fragmento `changelog.d/vel-p1p10.md` presente, sem skip, sem teste de estrutura sem obrigação.
- Lacuna anotada, não bloqueante: spec só com equivalentes sai rc 0 sem rodar controle.
