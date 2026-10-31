---
tipo: qa
contrato: 1
pedido: cobertura-equivalente
branch: melhoria/cobertura-equivalente
commit: dec6630de1e247677edf0d0ad278dbabab01e511
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-30
---
# QA: cobertura-equivalente

Base `3fec04b9d7b8e8916b0eef486a9253a854f227e7`, head `dec6630`. Pedido de controle (`bin/forge-mutante`): FM1, segundo PR. Parecer `R-QA` em paralelo ao review (decisão ACELERA-RODADA, item 4).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| (a) condição coberta só por equivalente sai `só equivalente` e rc 1 | `Cobertura.test_condicao_coberta_so_por_equivalente_sai_em_linha_propria_e_1` | equivalente sozinho (rc 1) x equivalente mais mutante comum (rc 0, `coberta`) | passou; vermelho na base; Q1, Q2, Q3 morrem |
| (b) spec só de equivalentes sem `testes` sai rc 2 | `Execucao.test_spec_so_de_equivalentes_sem_testes_nao_sai_0` | nenhum teste rodou | passou; vermelho na base; Q4 morre |
| (c) equivalente com `testes` roda; o que os testes matam é `inválido`, rc 2 | `Execucao.test_equivalente_com_testes_roda_e_o_que_eles_matam_e_invalido` | morto (rc 2) x sobrevive (`equivalente`, rc 0) | passou; vermelho na base; Q5 a Q8 morrem |
| validação da spec: `testes` opcional no equivalente, mas bem formado quando presente | `ValidacaoDaSpec.test_equivalente_sem_justificativa_ou_com_testes_mal_formados_e_invalido`, `test_equivalente_declarado_com_justificativa_e_valido_sem_testes` | lista vazia, id sem módulo, texto em vez de lista; justificativa curta | passou; vermelho na base (o primeiro); Q9 a Q11 morrem |
| texto da skill `qa-testing` descreve o novo comportamento | leitura do diff (`skills/qa-testing/SKILL.md:85`) | n/a | conferido |

## Cenários e resultado real
- `python3 -m unittest tests.test_forge_mutante` no head: `Ran 71 tests ... OK` (inclui o teste da spec comum, que não muda).
- `bin/forge-mutante tests/mutantes/cobertura-equivalente.json`: Q1 a Q11 `morreu`, rc=0.
- Conferência da lista contra o diff: as 10 condições Python mudadas (linhas 230, 231, 250, 479, 485, 552, 574, 604, 605, 620) têm um mutante cada; a linha 603 (`rodou = True`) é atribuição, coberta por Q5. Sem linha de guarda sem mutante (AR-1). Nenhum equivalente declarado nesta spec.
- `bin/forge-mutante --cobertura --base 3fec04b...` sem spec na linha de comando (usa as specs do diff): as 10 condições saem `coberta`, rc=0. Com spec na linha de comando a ferramenta recusa (`--cobertura e --base vêm juntos e sem SPEC`), como documentado.
- Vermelho: `bin/forge-testes --vermelho 3fec04b9d7b8e8916b0eef486a9253a854f227e7 --modulos test_forge_mutante`, rc=0. Abre com `vermelho: base=3fec04b9d7b8 head=dec6630de1e2 módulos=test_forge_mutante`; revertidos à base: `bin/forge-mutante`, fragmento do changelog e a skill. Contagem: 4 provam (asserção), 67 passam na base (herdados). Os 4 que provam são os testes novos de (a), (b), (c) e da validação.
- Specs de `tests/mutantes/` com equivalente declarado: só `hk3-parecer-texto-4.json` (V2, V3, V4, V10, V12). Rodadas as 4 specs `hk3-parecer-texto*.json` juntas: rc=0, os equivalentes seguem saindo `equivalente: <id> · <justificativa>` sem virar rc 2 (há mutante que roda na rodada).
- `scripts/verificar-contribuicao.sh origin/develop`: rc=0, nenhum segredo nem caminho pessoal.
- Itens de PA-7 conferidos: AR-1 (lista completa, acima); AR-6 (guarda de shell: não há mudança de shell no diff); AR-9 (limite antigo no texto: docstring de uso e skill atualizadas, 16 mutantes e demais limites intactos).

## Observações (sem achado)
- Equivalente com `testes` que sobrevive sai `equivalente` e vale rc 0 se for o único mutante da spec: é o comportamento do requisito (c), coberto por teste.
- No `--cobertura`, o equivalente com `testes` também conta como `só equivalente` (não prova a condição): coerente com (a), pois a prova é a rodada.
