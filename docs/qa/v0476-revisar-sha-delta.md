---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0476-revisar-sha-delta
commit: e4191c1b4546d4c12962aed79d7652faba1a44cb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0476-revisar-sha-delta (E3.49, parecer E3.77)

## Achados
- A1 (recomendado) tests/mutantes/v0433-integracao-2.json:261 · I31 e I32 foram realinhados ao código novo e a spec inteira estoura o prazo local (sem veredito, R-TETO na fila); o CI ou o autor confirmem que ainda morrem.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3.49-a: `Revisar-sha` sai do head remoto quando a ref local ficou na base | `test_revisar_sha.HeadRemoto.test_ref_local_na_base_usa_o_head_remoto` | ref local atrás do remoto | passou; vermelho na base (asserção) |
| E3.49-b: sem branch publicada vale a local | `HeadRemoto.test_sem_branch_publicada_vale_a_local` | sem `origin/<ref>` | passou (regressão, já passava na base) |
| E3.49-c: `HEAD`/`None` nunca vira `origin/HEAD` | `HeadRemoto.test_head_nunca_vira_o_origin_head` | `origin/HEAD` apontando para a develop | passou (mutante M2 morre) |
| E3.49-d: `brief gerar` com PR mesclado diz como continuar | `PrMesclado.test_recusa_diz_como_continuar_sem_recriar_a_branch` | PR MERGED | passou; vermelho na base (asserção) |
| E3.49-e: `.md` de `docs/devops/` sem frontmatter fica no delta | `test_parecer_delta.DocumentoDeDevops.test_documento_sem_frontmatter_fica_no_delta` | sem frontmatter | passou; vermelho na base |
| E3.49-f: documento apagado fica no delta | `DocumentoDeDevops.test_documento_apagado_fica_no_delta` | blob inexistente | passou; vermelho na base |
| E3.49-g: parecer de devops (com frontmatter) sai do delta | `DocumentoDeDevops.test_parecer_de_devops_sai_do_delta` | frontmatter presente | passou (mutante M5 morre) |
| E3.49-h: livre fora de `docs/devops/` segue fora | `DocumentoDeDevops.test_livre_fora_de_devops_sem_frontmatter_segue_fora_do_delta` | KANBAN e security | passou (mutante M4 morre) |
| Mapa de testes do forge-check (95 módulos) | `test_testes_tocados` (162 testes) | contagem | passou |

## Cenários e resultado real
- Rodados com TMPDIR: `test_revisar_sha` (4 OK), `test_parecer_delta` (4 OK), `test_testes_tocados` (162 OK, 1 skip pré-existente, não é meu).
- Vermelho antes do verde (`forge-testes --vermelho 3d8ad440 --modulos test_revisar_sha,test_parecer_delta`): 4 provam (asserção), 4 "não provam (passa na base)" por serem testes de fronteira que protegem a regra contra over-correção; cada um tem mutante que o mata. Saída 0.
- Mutação: 6 mutantes M1..M6 do pedido, todos mortos. Cobertura `--cobertura --base`: as 4 condições mudadas (2387, 3255, 3258, 3314) cobertas.
- Specs editadas: `v047-achados-fora-dominio.json` rodou (AF-M1, AF-M2, AF-M3 mortos). `v0433-integracao-2.json` (I31, I32 realinhados) não teve veredito: estourou o prazo local (rc 124) e a fila pesada; ver A1.
- A suíte inteira roda no CI do PR (check `bateria`); não rodei a suíte inteira aqui.
- Sem UI: acessibilidade n/a.
