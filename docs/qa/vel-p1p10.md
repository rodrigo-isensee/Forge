---
tipo: qa
contrato: 1
pedido: vel-p1p10
branch: melhoria/vel-p1p10
commit: 0b4585f172afa6ba0c1e535da996938711ada03e
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

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_mutante tests.test_forge.TetoPorPr tests.test_forge.VerificadoresDoAutor`: 73 testes, OK (só os testes do item; a suíte completa roda no pre-push, decisão M8).
- Rodei a mutação: `bin/forge-mutante tests/mutantes/vel-p1p10.json` sobre `0b4585f`: M1, M2, M3, M5, M6, M7, M8, M9, M10, M11, M12, M13 todos `morreu`, rc=0 (12 mutantes, dentro do teto de 16).
- `bin/forge-mutante --cobertura --base 3b94791a8e96771c061eabb8e2b77381151289d1`: rc 0, sete condições mudadas (linhas 225, 226, 242, 243, 271, 559, 562) todas `coberta`; conferi contra o diff: cada linha de guarda mudada tem mutante (M1 e M2 cobrem a constante da linha 66, fora da lista da cobertura por não ser condição). Sem guarda sem mutante, sem isenta.
- Equivalente sem justificativa reprovando: provado por `test_equivalente_sem_justificativa_ou_com_testes_e_invalido` e pelo mutante M3 (justificativa de 20 para 2 caracteres, morto).
- Vermelho antes do verde: os testes novos são provados por morte de mutante sobre o código do HEAD (cada mutante reverte a regra nova e derruba o teste); `forge-testes --vermelho` não foi rodado por mim, a suíte completa fica fora do meu escopo por brief.
- Itens do PA-7 conferidos: neutralidade (nada de projeto nos textos), `git add` explícito, versão e fragmento `changelog.d/vel-p1p10.md` presente, sem skip em teste.
- Lacuna anotada, não bloqueante: spec só com equivalentes sai rc 0 sem rodar controle (nenhum requisito do pedido a proíbe).
