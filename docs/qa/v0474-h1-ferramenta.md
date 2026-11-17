---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0474-h1-ferramenta
commit: db0b1f987bccc0cf549d47cd2cd7073a01404ac0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0474 (E2.27, H1 ferramenta)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| H1: aviso acima de 150 linhas de código | test_borda_do_teto_de_linhas, sonda 150/151 | exatamente 150 sem aviso, 151 com | passou |
| H1: testes e documentação não contam | test_so_codigo_conta_e_binario_fica_fora, sonda | só testes, só docs: 0 linhas | passou |
| H1: reprova só com PR aberto sem a linha de motivo | classe NoPr, motivo vazio e forma errada | sem PR, sem rede, motivo vazio | passou |
| PEDIDO-TETO-BRIEF: aviso acima de 50 etapas e brief a 90% do teto | sonda das funções (50 sem, 51 com; 8999 sem, 9000 com de 10000) | 50, 90% | passou |
| ref diferente de HEAD no tamanho do PR | test_ref_diferente_do_head_mede_a_ref, M20 | ref explícita | passou |
| PR fechado ou mesclado não reprova | test_pr_fechado_ou_mesclado_nao_reprova | estado CLOSED/MERGED | passou |

## Cenários e resultado real
- Vermelho (E2.36): `vermelho: base=681d4b33f753 head=7924b25bd1fc módulos=test_forge_tamanho (restrito por --modulos)`, `contagem: não prova (passa na base)=3; prova (API ausente)=15; prova (asserção)=5`, saída 0.
- Mutantes (3 specs, `--processos 3`): saída 0, M1 a M22 todos `morreu` (22 mortos; M2, M7, M9, M12, M17 por erro do teste declarado, que passa sem o mutante).
- Cobertura (`--cobertura --base 681d4b33`): resta `sem mutante · bin/forge-check:8477` (`dados.get('body') or ''`), coberta por M19 (a troca sai do nó da condição; aceito); `spec editada · tests/mutantes/lote-l08-e7.json`.
- Testes: `python3 -m unittest tests.test_forge_tamanho tests.test_forge_mutante.ConferirTodas`: 27 testes, OK.
- Suíte inteira: não rodada aqui; vale o check-run `bateria` do CI do mesmo sha.
- Revalidação E2.49 (head db0b1f98, delta sobre 7924b25b): junção da develop; no domínio só `bin/forge-testes` (+ `test_conformidade_verde` na lista) e a contagem 92 em `tests/test_testes_tocados.py`, sem lógica nova. `python3 -m unittest tests.test_testes_tocados tests.test_forge_tamanho`: 185 testes, OK (1 pulado pelo sandbox, /proc de outro namespace). Suíte inteira: check-run `bateria` do mesmo sha.
- Revalidação E2.36 (head 7924b25b, delta sobre 4ddaa68b), achados fechados: A1 (tests/test_forge_tamanho.py, carga sob demanda; `forge-testes --vermelho 681d4b33 --modulos test_forge_tamanho` sai 0 com 20 provas, 15 API ausente e 5 asserção, e 3 que passam na base, negativos esperados); A2 (bin/forge-check:1412, teste `test_ref_diferente_do_head_mede_a_ref` e M20 morreu; `ref or "HEAD"` já não sobrevive).
