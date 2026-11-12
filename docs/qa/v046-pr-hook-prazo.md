---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/pr-hook-prazo
commit: b08296cd89fe68c7b76684589312053f58adfd16
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 (E20.5, PR-HOOK-PRAZO)

Diff: `origin/develop...b08296cd` (código do 4ae51318; depois só pareceres de segurança e review). O `forge-check pr` grava o resultado por head em `<git-common-dir>/forge/pr/<head>/` e o hook `parecer` libera a abertura do PR só lendo o aprovado do mesmo head, branch e base. Não há especificação de UX (ferramenta do Forge): as obrigações vêm da E20.1 do pedido e de `R-REVIEW`; os testes são os do autor, conferidos e rodados por mim.

## Achados
- A1 (bloqueante) tests/test_pr_hook_prazo.py:179 · `forge-testes --vermelho` sai rc 2: test_pr_grava_o_reprovado_e_o_hook_o_le dá erro (ValueError ao desempacotar `registros(raiz)` vazio) na base, "sem veredito"; troque por asserção (R-QA, vermelho antes do verde)

## Critério → teste → resultado
| Obrigação (E20.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aprovado do head libera só lendo, dentro do prazo de 3 s | test_aprovado_do_head_libera_so_lendo_dentro_do_prazo | prazo de produção; hook não refaz a checagem (saída 97) | passou |
| Reprovado do head recusa com a violação | test_reprovado_do_head_recusa_so_lendo | resultado reprovado | passou |
| Sem resultado do head: recusa e diz o comando | test_head_diferente_recusa_e_diz_o_comando, test_sem_resultado_recusa_mesmo_sem_violacao | outro head; resultado ausente | passou |
| Outra base, outra branch, outro head, registro ilegível ou estranho não valem | test_resultado_de_outra_base_recusa, test_ilegivel_de_outra_branch_ou_de_outro_head_nao_vale | base nula x develop; JSON quebrado ao lado do aprovado | passou |
| Pedido da branch sem resultado, branch sem pedido, lista malformada | test_pedido_da_branch_sem_resultado_recusa, test_branch_sem_pedido_gravado_recusa, test_pedidos_da_branch_malformado_nao_derruba_a_leitura | vazio; tipo errado | passou |
| Merge segue a conferência de sempre | test_merge_segue_a_conferencia_de_sempre | merge sem cache (v0455) | passou |
| `forge-check pr` grava reprovado/aprovado; previo e HEAD sem branch não gravam | test_pr_grava_o_reprovado_e_o_hook_o_le, test_pr_aprovado_grava_e_o_hook_libera_so_lendo, test_previo_e_head_sem_branch_nao_gravam | modo 0700; sem branch | passou (ver A1) |
| Ref ou base que não resolvem são ausentes | test_ref_ou_base_que_nao_resolvem_sao_ausentes | ref inexistente; base nula | passou |
| Falha ao gravar avisa e não muda o código | test_falha_ao_gravar_avisa_e_nao_muda_o_codigo | `.git/forge` é arquivo | passou |
| Fixtures do hook parecer seguem verdes com o `resultado_do_pr` | 454 fixtures de tests/hooks/parecer | permissões, rascunho, merge | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pr_hook_prazo`: Ran 15 tests in 49.602s, OK.
- Fixtures do hook parecer (as 454 sem prazo de produção, pelo executar_em_lote do test_hooks): 454 de 454, OK (175 s). O `test_fixtures` inteiro estoura 500 s nesta máquina, por isso o recorte. As 5 falhas de agentes/* e pesado/mesma-sessao-libera citadas no brief estão fora da pasta parecer e caem também na develop (review E20.3); não as rodei.
- Mutantes: `forge-mutante --cobertura --base d3453407` rc 0, toda condição mudada com mutante declarado; 2 isentas lidas (`base_sha or ''` só compõe o nome do arquivo, a leitura casa pelo conteúdo; `'veja a saída dele'` é texto de reserva), aceitas. As 5 specs: 33 de 33 morreram, rc 0. M25 morreu por erro do teste declarado, não por asserção (mesma causa do A1).
- Vermelho antes do verde (`forge-testes --vermelho d3453407 --modulos test_pr_hook_prazo`): 13 de 15 provam (3 por asserção, 10 por API ausente); test_previo_e_head_sem_branch_nao_gravam passa na base (guarda negativa, provada pelos mutantes); test_pr_grava_o_reprovado_e_o_hook_o_le sem veredito; saída rc 2 (A1).
- Fora desta entrega: o forjamento do aprovado por escrita em `.git/forge/` (A2 da segurança, E20.6).
- Prova de CI: a suíte inteira roda no CI do PR (check-run `bateria` do mesmo sha); o PR ainda não existe, não citei.
