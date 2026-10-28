---
tipo: qa
contrato: 1
pedido: aq1-forge-check
branch: melhoria/aq1-forge-check
commit: 7ae7606228d7723ea4ec95919856ec919f65cbf9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: aq1-forge-check

Sem UX nem API; as obrigações são E1 a E4 do pedido `AQ1-FORGE-CHECK` (P4 e a parte do `agile-coach` ficam fora, por decisão). Head `7ae7606` sobre a base `a83de9e` (develop); não escrevi o diff. Rodado em `~/.forge-contrib/wt/wt-qa-aq1-forge-check`, com o parecer em paralelo ao review e à segurança (decisão ACELERA-RODADA).

## Achados
- A1 (recomendado) tests/test_medidas_m14b.py:320 · o teste `test_aq1_resumo_conta_por_origem...` na base dá erro (FileNotFoundError em `escapes.md`, porque `--origem` não existe), não asserção; o `forge-testes --vermelho` classifica "sem veredito" e sai 2; afirmar `escapes.md` existente (ou checar o rc de cada `registrar`) antes de lê-lo vira "prova (asserção)". Não bloqueia: 15 testes provam e o mutante M20 mata o comportamento.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 `Depende de:` traz as decisões do origem (um nível) | `DecisoesCobradas.test_depende_de_traz_a_decisao_do_origem_e_a_cobra`, `test_gerar_copia_a_decisao_do_origem_com_o_subtitulo_do_registro`; M1 a M4, M17 a M19 | si mesmo/repetido, sem registro, nome inválido, registro grande, teto de fontes | passou |
| E1 texto do conferente e do Jarvis | `TextoDoConferenteNoLote.test_recomendacao_incluida_precisa_da_decisao_tecnica_do_historico` | n/a | passou |
| E2 recomendação incluída exige DECISÃO TÉCNICA que cite o id | `VoltaComRecomendacao.test_recomendacao_incluida_sem_decisao_tecnica_reprova_e_o_gerar_pede_a_linha`, `test_decisao_tecnica_de_outro_id_ou_fora_do_historico_nao_cobre`; M5 a M8 | id de outro achado (`A1` x `A10`), linha fora do Histórico, com e sem `--ref` | passou |
| E3 regex aceita `qa` e classe com espaços; 5 linhas AR | `AchadosRecorrentes.test_aq1_formato_aceita_o_tipo_qa_e_a_classe_com_espacos_sem_abrir_texto_livre`, `test_aq1_o_arquivo_do_forge_traz_as_linhas_ar_da_proposta`; M9 a M13 | 70/71 caracteres, maiúscula inicial, dois espaços, espaço final, vírgula, `·` e quebra de linha na classe, tipo fora da lista | passou |
| E4 `escape registrar --origem`, padrão, coluna, resumo | `DefeitoEscapado.test_aq1_origem_gravada_na_ultima_coluna_e_o_padrao_e_nao_classificado`, `test_aq1_origem_invalida_e_recusada_sem_gravar_e_sem_ecoar_o_valor`, `test_aq1_resumo_conta_por_origem_e_le_a_linha_antiga_sem_a_coluna_como_nao_classificado`; M14 a M16, M20 | valor inválido (não grava, não ecoa), linha antiga de 7 colunas, valor fora da lista | passou |
| E4 doc (`melhoria-continua.md`) | suíte estrutural (`tests/test_forge.py`) | n/a | passou |

## Execução (resultado real)
- `python3 -m unittest tests.test_forge tests.test_erros_no_brief tests.test_medidas_m14b`: `Ran 520 tests in 200.604s`, `OK`. Suíte completa não rodada por mim (roda no pre-push; decisão ACELERA-RODADA).
- Vermelho: `bin/forge-testes --vermelho a83de9e24908195fef0c92ebfcb1603518b58390 --modulos test_forge,test_erros_no_brief,test_medidas_m14b`, saída abre com `vermelho: base=a83de9e24908 head=7ae7606228d7` e `revertidos à base: agents/conferente.md, agents/jarvis.md, bin/forge-check, changelog.d/aq1-forge-check.md, docs/engineering/achados-recorrentes.md, docs/melhoria-continua.md`; fecha com `contagem: não prova (passa na base)=503; prova (API ausente)=1; prova (asserção)=15; sem veredito=1`, rc=2. Nenhum teste cai no HEAD (todos `H=ok`). O único sem veredito é o do A1; reproduzido na base, falha com `FileNotFoundError: .../docs/kanban/escapes.md`, ou seja, pelo motivo certo (a opção não existe), só não por asserção. A primeira tentativa, sobre todos os módulos, estourou o meu prazo de 550 s (rc=124, sem veredito) e foi refeita restrita aos três módulos.
- Mutantes: `bin/forge-mutante tests/mutantes/aq1-forge-check.json tests/mutantes/aq1-forge-check-2.json tests/mutantes/aq1-forge-check-3.json`: M1 a M20 `morreu`, rc=0.
- `bin/forge-mutante --cobertura --base a83de9e24908195fef0c92ebfcb1603518b58390`: dez linhas `coberta` (1319, 1434, 1479, 2520, 2581, 4253, 4255, 4259, 4263, 4265), nenhuma "sem mutante"; conferi a lista contra o diff: as linhas de guarda mudadas (regex, `tem_decisao_tecnica`, validação de `--origem`, `Depende de:`) têm mutante.
- Sonda do regex `ACHADO_RECORRENTE` (acima): sem backtracking catastrófico (5000 repetições em 8 µs).
- Merge da develop (`6bed86b`): os textos de `agents/conferente.md` e `agents/jarvis.md` trazem as duas partes (o que a develop passou a dizer e o que o lote acrescenta), e os testes de texto passam.

## Riscos
- `escapes.md` em uso ganha a coluna só nas linhas novas; o cabeçalho antigo (7 colunas) não é reescrito, e o resumo lê linha de 7 colunas como `nao-classificado` (provado no teste de resumo).
