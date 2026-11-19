---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp8-maquina
commit: 528cc26744ae2331c46006c638c9670b49928a77
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0479-mp8-maquina (E23.8, revalidação)

Diff 0c47762a..6ebd057c: `bin/forge-status --maquina` (MP8), `tests/test_maquina.py` (10 testes novos), 13 mutantes. Suíte inteira no CI do PR; aqui só os testes do diff.

## Achados
- A1 (recomendado) tests/test_maquina.py:352 · 5 dos 10 testes novos dão `erro` (não `falha`) na base, e o `forge-testes --vermelho` os lista como "sem veredito"; asserte sem desempacotar a saída (ex.: `len(linhas)`) para a prova de vermelho valer em todos.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| MP8: sem projeto, "nenhum" + medida | SemProjeto.test_sem_projeto_diz_nenhum_e_mede_a_maquina | vazio | passou (vermelho na base) |
| MP8: sem /proc e núcleos inválidos | SemProjeto.test_sem_leitura_de_proc_nem_de_nucleos | entrada inválida | passou |
| MP8: registro ilegível recusa o escape | SemProjeto.test_registro_ilegivel_nao_lista_e_recusa_o_escape | arquivo corrompido | passou |
| MP8: pasta não absoluta/ausente fica fora | SemProjeto.test_sessao_sem_pasta_absoluta_fica_fora | pasta relativa, vazia | passou (vermelho na base) |
| MP8: --help | SemProjeto.test_help_mostra_a_opcao | n/a | passou (vermelho na base) |
| MP8: um projeto, teto inteiro, versão, decisões | UmProjeto.test_um_projeto_tem_o_teto_inteiro_versao_e_decisoes | 1 projeto, 2 sessões | passou |
| MP8: versão do plugin, link não seguido, `?` | UmProjeto.test_versao_do_clone_do_forge_link_e_sem_versao | symlink, sem versão | passou (vermelho na base) |
| MP8: decisões por link `?`, uso fora da forma | UmProjeto.test_decisoes_por_link_e_uso_fora_da_forma | link, tipo errado | passou (vermelho na base) |
| MP8: tarefa pesada viva conta | UmProjeto.test_tarefa_pesada_viva_conta | n/a | passou |
| MP8: vários projetos repartem pelo peso, escape recusado | VariosProjetos.test_varios_projetos_repartem_o_teto_pelo_peso_e_o_escape_nao_vale | peso desigual, 2 projetos | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_maquina.py`: 33 testes, OK.
- `forge-testes --vermelho 0c47762a --modulos test_maquina`: 5 provam (asserção), 5 sem veredito (erro na base, A1), 23 herdados da base passam (não são novos); nenhum cai no HEAD.
- `forge-mutante` v0478-mp8-maquina.json + -2.json (pedido v0478): MP8-1 a MP8-13 todos `morreu`.
- `forge-mutante` v0476-mp2-mp4-3.json (spec editada, S1 reapontado): P7 a P10, S1 a S3, M11 todos `morreu` (P10 com aviso de erro do teste declarado sob o mutante, que passa sem ele; morte válida).
- `forge-mutante --cobertura --base 0c47762a`: toda condição mudada em `bin/forge-status` coberta (linhas 86 a 146, MP8-2 a MP8-13); sem condição descoberta.
- Sem bugs. Rede: nenhuma chamada no `--maquina`.

## Revalidação E23.8 (head 528cc267, delta 6ebd057c..528cc267)
Delta lido por `forge-check parecer delta`: `bin/forge-status` (pasta-mãe em link), `bin/forge_dono.py` (teto de 8 MB), testes e mutantes MP8-14 e MP8-15. Parecer: aprovado; o A1 acima segue recomendado, não bloqueia.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 segurança: `.forge`/`.claude-plugin` por link não se lê | UmProjeto.test_pasta_da_versao_em_link_nao_se_segue | link na pasta-mãe, as duas por link | passou (vermelho: falha na base) |
| A2 segurança: pedido acima de 8 MB fora da contagem | UmProjeto.test_pedido_acima_do_teto_nao_conta | teto exato conta, teto+1 não | passou (vermelho: erro de API na base) |
| Regressão: KANBAN ilegível vira aviso | test_forge_dono.PerguntasAbertas.test_quadro_ilegivel_vira_aviso (mock passou a `Path.open`) | arquivo ilegível | passou |

- `test_maquina.py`: 35 testes OK; `test_forge_dono.py`: 79 testes OK (TMPDIR local, sem suíte inteira).
- `forge-testes --vermelho 6ebd057c --modulos test_maquina`: `base=6ebd057c42e7 head=1b876623ae32`; 2 provam (asserção e API ausente), 33 não provam (já existiam), nenhum cai no HEAD.
- `forge-mutante` (2 specs, `--base 6ebd057c`, `base=6ebd057c… rev=1b876623…`): MP8-1 a MP8-15 todos `morreu`, rc 0; MP8-14 (forge-status:82) e MP8-15 (forge_dono.py:581) cobrem as duas linhas de guarda mudadas.
- O head 1b876623 só soma o parecer de segurança sobre 528cc267; código idêntico.
