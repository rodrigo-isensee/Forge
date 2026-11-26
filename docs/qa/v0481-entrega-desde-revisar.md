---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-entrega-desde-revisar
commit: c056f38d285c454744e3a343b705621d2cacda49
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 entrega-desde-revisar (#904, E16.4, classe C)

Diff lido contra o merge-base com a develop (Base-sha 34ab6714): `bin/forge-check` (`desde_do_parecer_aprovado` e uma linha em `cmd_entrega_conferir`), `tests/test_selo_e_entrega.py` (`CicloDo878`, 12), dois specs de mutantes (ED1 a ED12), `tests/pesos-d4.json`, fragmento do changelog.

- ci: c056f38d285c454744e3a343b705621d2cacda49 verde

CI no head exato (`gh pr checks 904`): verdes `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação`, as 10 partes da suíte (3.12 e 3.14), `teto de pulados`, `árvore já provada`. Vermelhos fora da conta: `bateria (pareceres)` (log: R-REVIEW, PR toca `bin/forge-check` sem parecer aprovado de review), `bateria` (agregado: `pareceres: failure`, o resto success) e `catraca` (espera os pareceres). Nenhum vermelho tem causa de código.

## Análise: nenhum caminho novo libera código não revisado
O Desde só avança da conferida para X quando: há conferida anterior; todo parecer da branch e do pedido no head é `aprovado` com o mesmo `commit:` X; o review está entre eles; X é `Revisar-sha:` de brief selado de cada portão que o assina; X está adiante da conferida, no head e fora da base; depois de X só entram pareceres, quadro, fragmento e merge limpo (`commit_vale`). Faltando uma condição, volta o Desde de sempre; parecer antigo com outro `commit:` ou reprovado também devolve (aperta). O que vem depois de X continua conferido. Caminho neutro ou mais estrito; nenhum afrouxa.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Ciclo do #878: Desde = `commit:` e a conferência cobre o head | `test_ciclo_do_878_o_desde_e_o_revisar_sha_...` | merge da develop depois dos pareceres | passou |
| Sem conferida anterior, sem Desde do parecer | `test_sem_conferida_anterior_nao_ha_desde_do_parecer` | conferida vazia | passou |
| Só pareceres da própria branch e do pedido | `test_parecer_de_outra_branch_ou_pedido_vindo_da_develop_nao_conta` | parecer alheio via develop | passou |
| Um só `commit:` | `test_pareceres_com_commits_diferentes_...`, `test_dois_commits_revisados_selados_nao_dao_desde` | dois commits | passou |
| Review obrigatório | `test_sem_review_mantem_o_desde_da_conferida` | ausência do review | passou |
| Todos aprovados | `test_parecer_nao_aprovado_mantem_o_desde_da_conferida` | reprovado | passou |
| `Revisar-sha` selado | `test_sem_brief_selado_do_portao_mantem_o_desde_da_conferida` | sem selo | passou |
| Adiante da conferida | `test_conferida_adiante_do_revisado_fica` | conferida = head | passou |
| No head e fora da base | `test_revisado_fora_do_head_nao_e_desde`, `test_revisado_na_base_nao_e_desde` | outra branch, base | passou |
| Depois de X só o que não desatualiza | `test_codigo_depois_dos_pareceres_mantem_o_desde_da_conferida` | código após o parecer | passou |

## Execução
- `python3 -m unittest tests.test_selo_e_entrega.CicloDo878`: Ran 12 tests, OK.
- Mutantes (`bin/forge-mutante` com as duas specs, `--processos 3`): ED1 a ED12 todos `morreu` (ED1 por erro do teste com controle verde). Nenhum sobrevivente.
- `bin/forge-mutante --cobertura --base 34ab6714`: todas as linhas de guarda cobertas; só `tests/pesos-d4.json` sai `não coberto`, dado sem guarda.
- Vermelho: `bin/forge-testes --vermelho 34ab6714cbc13e41c35907b13cb3a6b2b71d9688 --modulos test_selo_e_entrega`:
  `vermelho: base=34ab6714cbc1 head=c056f38d285c módulos=test_selo_e_entrega (restrito por --modulos)`; 8 dos 12 de `CicloDo878` provam (1 por asserção, 7 por API ausente); 4 não provam por serem guardas negativas (`codigo_depois_dos_pareceres`, `parecer_nao_aprovado`, `pareceres_com_commits_diferentes`, `sem_review`), cobertas pelos mutantes ED11, ED6, ED4 e ED5, que morrem. Saída 0.
