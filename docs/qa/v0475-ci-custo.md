---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: 5a397c61c3be84a131d0ec14e824bcc4575263ab
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0475-ci-custo

Escopo (E3.66, pedido v0474): modelo de CI de projeto enxuto (`templates/projeto/.github/workflows/ci.yml` e `ci-docs.yml`), seção "CI de projeto privado: minutos" da skill `ci-cd`, mapa do `bin/forge-testes`. Obrigação: `R-CUSTO`.

## Achados
- A1 (recomendado) templates/projeto/.github/workflows/ci.yml:12 · o modelo só se prova por texto; a execução real no Actions (agregador `ci` verde com ci-docs, PR misto md+código) não foi exercida aqui, confirmar no primeiro projeto.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| R-CUSTO: suíte só em PR e nas branches do fluxo | SuitePesada.test_push_so_nas_branches_do_fluxo, test_pull_request_dispara_a_suite | push de branch de trabalho fora | passou |
| Documento não roda a suíte; par cobre a mesma lista | test_so_documento_nao_roda_a_suite_e_o_par_cobre_a_mesma_lista | lista de caminhos idêntica nos dois | passou |
| Neutro de stack (ADR 0001) | test_comando_vem_da_stack_sem_nome_de_ferramenta | sem nome de ferramenta | passou |
| Check exigido nunca pendente | CheckObrigatorio (3 testes) | falha da suíte reprova o agregador; skipped não passa | passou |
| concurrency por branch | Concorrencia.test_push_e_pr_da_mesma_branch_dividem_o_grupo_e_cancelam | push e PR no mesmo grupo | passou |
| Higiene (timeout, SHA, permissões) | Higiene (3 testes) | sem continue-on-error nem pull_request_target | passou |
| Entrega pelo forge-init e skill | Entrega (2 testes) | placeholder substituído | passou |
| Mapa do pre-push roda o teste | test_testes_tocados (M16, M17) | módulo listado | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_modelo_ci.py`: Ran 13 tests, OK.
- `test_testes_tocados.py`: Ran 162 tests, OK (skipped=1, preexistente).
- Vermelho: `forge-testes --vermelho 3d8ad440` cai em suíte completa (o diff toca `bin/forge-testes`) e estourou meu prazo de 280 s (rc 124, sem veredito; não vale como vermelho). Substituto: o teste novo copiado sobre a árvore da base (`git archive 3d8ad440`): `Ran 13 tests ... FAILED (failures=1, errors=12)`, ou seja, nenhum passa sem a implementação.
- Mutação: `bin/forge-mutante tests/mutantes/v0475-ci-custo.json tests/mutantes/v0475-ci-custo-2.json --processos 3`: M1 a M17 todos `morreu`, nenhum sobrevivente. Lista conferida contra o diff: cada guarda mudada (gatilhos, paths, concurrency, agregador, timeout, mapa) tem mutante.
- Não rodei a suíte inteira; vale o check-run `bateria` do CI do PR (não há PR ainda).

## Revalidação por delta (f59f7766..d8e1b09b)
Delta no domínio: ci.yml (um workflow só, job `mudanca`, agregador `ci` único), remoção do ci-docs.yml, skill, `test_modelo_ci.py`, specs de mutantes. A detecção e o agregador agora são exercidos executando o shell dos passos (Deteccao e CheckObrigatorio rodam `bash -c`), não só por texto: o A1 anterior fica atendido no que é verificável localmente.
- `python3 -I -m unittest discover -s tests -p test_modelo_ci.py`: Ran 17 tests, OK.
- Vermelho: testes novos copiados sobre `git archive f59f7766`: Ran 17, FAILED (failures=11); os 6 que passam na base são de higiene herdada, os de regra nova caem.
- Mutação do delta: `bin/forge-mutante tests/mutantes/v0475-ci-custo.json tests/mutantes/v0475-ci-custo-2.json --base f59f7766 --processos 3`: `base=f59f7766bfcecbb1887cce0b6c0aff6ab31880cd`, M1 a M20 todos `morreu`, nenhum sobrevivente. Cada guarda mudada (gatilhos, sem filtro de caminho, `if` da suíte, `case` da detecção, padrão código, agregador, concurrency, timeout, SHA) tem mutante.
- Não rodei a suíte inteira: vale o check-run `bateria` do CI do PR no mesmo sha.
- Resíduo (recomendado, não bloqueia): execução real no Actions segue por confirmar no primeiro projeto.

## Revalidação por delta (d8e1b09b..8a4a9707)
Delta no domínio: `--no-renames` na detecção do ci.yml, skill, `test_modelo_ci.py` (ambiente limpo, sondas S1 e S2 de renomeação), mutantes M21 e M22.
- `python3 -I -m unittest discover -s tests -p test_modelo_ci.py`: Ran 19 tests, OK.
- Vermelho: o teste novo sobre `git archive d8e1b09b`: Ran 19, FAILED (failures=3); caem test_renomear_codigo_para_documento_roda_a_suite, test_deteccao_usa_no_renames e a asserção da skill.
- Mutação: `bin/forge-mutante tests/mutantes/v0475-ci-custo.json tests/mutantes/v0475-ci-custo-2.json --base d8e1b09b --processos 3`: `base=d8e1b09b050f7455637234be5a9ccbc97c9d0ed5`, M1 a M22 todos `morreu`, rc 0; a única guarda mudada (`--no-renames`, M21; texto da skill, M22) tem mutante.
- Suíte inteira: vale o check-run `bateria` do mesmo sha. Resíduo A1 inalterado (recomendado).

## Revalidação por delta (8a4a9707..7c7f6c42)
Delta no domínio: `bin/forge-testes` (mapa: + test_parecer_delta e test_revisar_sha), `tests/test_forge.py` (marcador `{{` sem `$`), `tests/test_modelo_ci.py` (ambiente_git.sem_manutencao), `tests/test_reval_delta.py` (citação conhecida), mutante M30.
- `catraca.py --base origin/develop`: rc 0, sem guarda sem mutante.
- `test_modelo_ci` 19 OK; `test_parecer_delta` 4 OK; `test_revisar_sha` 4 OK; `test_ambiente_git` 20 OK; `test_reval_delta` 10 OK; `tests.test_forge.ForgeInit` e `IsolamentoDoGit` 12 OK.
- Mutação: `bin/forge-mutante tests/mutantes/v0475-ci-custo-3.json --base 8a4a9707`: `base=8a4a97077c22308b0a503d4e33f72bb91700e12a`, M30 `morreu`, rc 0.
- `test_metricas_texto`: 1 falha (A2), anterior ao delta mas provada no head; a `bateria` do CI a pegaria.
- Suíte inteira: vale o check-run `bateria` do mesmo sha. Resíduo A1 inalterado.

## Revalidação por delta (7c7f6c42..ae44f02b)
Delta no domínio: `skills/ci-cd/SKILL.md` (enxuta; o miolo foi para `skills/ci-cd/ci-de-projeto-privado.md`), `tests/test_modelo_ci.py` (lê a skill e o arquivo novo), `tests/mutantes/v0475-ci-custo-2.json` (M17, M18, M22 apontam para o arquivo novo). A2 (teto de texto) corrigido: `tests.test_metricas_texto` passa.
- `catraca.py --base origin/develop`: rc 0, sem guarda sem mutante.
- `test_metricas_texto` 2 OK; `test_orcamento_instrucao` 8 OK; `test_modelo_ci` 19 OK; `test_ambiente_git` 20 OK.
- Mutação: `bin/forge-mutante tests/mutantes/v0475-ci-custo-2.json`: M17 a M22 todos `morreu`, rc 0 (os trechos `de` seguem existindo no arquivo novo, o que prova o deslocamento sem perda de guarda).
- Suíte inteira: vale o check-run `bateria` do mesmo sha. Resíduo A1 inalterado (recomendado).

## Revalidação no 5a397c61 (delta desde ae44f02b)
Delta: merge da develop; conflito de texto na skill `ci-cd` resolvido (linha de medição de minutos, agora com `forge-cota-ci`; o CI de projeto privado segue em `ci-de-projeto-privado.md`). Sem marcas de conflito.
- `python3 -m unittest tests.test_metricas_texto` Ran 2 OK; `tests.test_orcamento_instrucao` Ran 8 OK; `tests.test_modelo_ci` Ran 19 OK; `tests.test_cota_ci` Ran 26 OK.
- `python3 -I tests/catraca.py --base origin/develop`: rc=0.
- Suíte inteira: vale o check-run `bateria` do CI do PR (A1 anterior segue como recomendado).
