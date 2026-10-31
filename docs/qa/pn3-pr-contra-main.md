---
tipo: qa
contrato: 1
pedido: pn3-pr-contra-main
branch: melhoria/pn3-pr-contra-main
commit: 4b3bf3298a5bf02f26327b04bb4e9683a4cc963d
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: pn3-pr-contra-main (volta 1)

Escopo: P-N3, o `scripts/promover-homolog.py` roda `forge-check pr release-<versão> --ref <ref> --base main` na release e para antes de abrir o PR. Sem especificação de UX nem gatilho de segurança; os critérios vêm do pedido (E1, E2). Base 31257c1, head 4b3bf32; delta ccf72bb..4b3bf32 (158998c: filtro de devops e segurança, falha fechada, mensagem com a branch da release; 4b3bf32: mutantes M5 a M8).

## Achados
(nenhum; o A1 do parecer 9453161 está resolvido: ramo `except` coberto por ContraMainFalha e pelo mutante M5)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 parecer da release desatualizado contra a main para antes do PR | ContraMain.test_parecer_da_release_desatualizado_para_antes_de_abrir_o_pr (M1, M2, M8) | código depois do parecer; nenhuma chamada gh | passou |
| E1 parecer da release faltando para | ContraMain.test_parecer_da_release_faltando_para (M1, M8) | parecer ausente | passou |
| E1 release válida passa, base main e pedido release-<versão> | ContraMain.test_release_valendo_contra_a_main_passa_e_diz_o_comando (M3, M4) | base e pedido exatos | passou |
| E1 sem versão nova não roda a conferência | Versao.test_sem_versao_nova_nao_e_release_e_nao_confere_changelog (M2) | versão igual à da homolog | passou |
| E1 devops e segurança da leva não param a release | ContraMain.test_devops_e_seguranca_da_leva_nao_param_a_release (M7) | só linhas docs/devops e docs/security | passou |
| E1 forge-check não roda ou estoura o prazo (falha fechada) | ContraMainFalha.test_prazo_estourado_para, test_forge_check_ausente_para (M5) | prazo, executável ausente | passou |
| E1 forge-check cai sem saída (falha fechada) e a mensagem lembra melhoria/release-<versão> | ContraMainFalha.test_queda_sem_veredito_para (M6) | stdout vazio com rc != 0 | passou |
| E2 spec de mutantes M1 a M8 e vermelho antes do verde | forge-mutante, forge-testes --vermelho | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_promover_homolog` sobre 4b3bf32: 36 testes, OK.
- `bin/forge-mutante tests/mutantes/pn3-pr-contra-main.json`, rc=0: M1 a M8 morreram (linhas 158, 240, 150, 149, 155, 158, 158, 157).
- `bin/forge-mutante --cobertura --base 31257c14c8d245d66e7806edb7cd65e22b3aeb04`, rc=0: coberta 157 (M8), 158 (M1, M6, M7), 240 (M2), "declarado, não provado". O ramo `except` (linha 155, `parar(...)`) não é condição Python e tem M5; conferido à mão contra o diff: toda guarda mudada (`if r.returncode and (...)`, `startswith(PARECERES_DA_LEVA)`, `or not linhas`, `except`, `--base main`, pedido, versão) tem mutante.
- Vermelho, `bin/forge-testes --vermelho ccf72bbc346797c0a703ab079c3de625539e5c72 --modulos test_promover_homolog`, rc=0: `vermelho: base=ccf72bbc3467 head=4b3bf3298a5b módulos=test_promover_homolog`; revertidos à base: docs/promocao-integrador.md, scripts/promover-homolog.py; prova (asserção): ContraMain.test_devops_e_seguranca_da_leva_nao_param_a_release (H=ok, B=falha) e ContraMainFalha.test_queda_sem_veredito_para (H=ok, B=falha); contagem: não prova (passa na base)=34, prova=2. Os testes de prazo e executável ausente passam na base porque o ramo `except` já existia; a prova deles é o mutante M5 (morreu).
- Documentação (docs/promocao-integrador.md, docstring) bate com o comportamento; fragmento do changelog presente.
- Itens de PA-7 (achados-recorrentes.md) conferidos: AR-2 resolvida (M5/M6); AR-1 não se aplica, a lista cobre as guardas condicionais; AR-5 ok (`-I` no comando).
