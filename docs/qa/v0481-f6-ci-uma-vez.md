---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: ac8202d0e2644d015f1c13be3fd7f040101db06f
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E32.7, #929, F6: o CI do PR roda a suíte uma vez)

- ci: ac8202d0e2644d015f1c13be3fd7f040101db06f verde

## Achados
- A1 (bloqueante) .github/workflows/diario.yml:128 · Guarda do diário sem teste: sem o `ruim=1` os mutantes vivos nunca reprovam o job (a issue não abre); a matriz de 5 para 3 partes passa; tirar `ref: develop` da suíte (l.32) passa (o teste só faz assertIn do texto). Falta mutante ou teste por job (R-QA).
- A2 (recomendado) .github/workflows/ci.yml:317 · Sem teste que falhe: trocar o `run` da fumaça do 3.14 por `true` passa; o `if [ -n "$aberta" ]` do cartão (diario.yml:153, comentar em vez de abrir outra issue) também. Um teste por passo evita regressão silenciosa.

## Critério → teste → resultado
O pedido não tem `docs/ux/` com CA-n para esta etapa; os critérios vêm do objetivo do brief.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte do PR roda uma vez (3.12), sem job da suíte no 3.14 | `test_suite_partes.FiacaoDoCI.test_f6_o_pr_roda_a_suite_uma_vez` + os da matriz e agregadores | 5 partes; nenhum job `*-quatorze` fora instalação e agregador | passou; vermelho na base (falha) |
| 3.14 só instalação e fumaça; `bateria (python 3.14)` junta só a instalação | `MatrizNeedsEAgregadorTest` (needs, estado com perna vermelha), CI-M1, X3, X4 | needs e `always()` do agregador | passou; X3 e X4 morreram |
| Fumaça do 3.14 de fato roda | nenhum | passo da fumaça | descoberto (A2, X1 sobreviveu) |
| Verificações longas e mutantes saem do PR | `test_f6_o_pr_roda_a_suite_uma_vez` (sem `forge-mutante` no ci.yml, e2e só em `instalacao-quatorze`) | texto do ci.yml | passou; CI-M1 morreu |
| diario.yml diário, só leitura, escreve só issue | `test_f6_diario_roda_o_que_saiu_do_pr_na_develop_e_abre_o_cartao`, CI-M2, CI-M3 | `issues: write` único, `always()` do cartão | passou; M2 e M3 morreram |
| Fatia do dia, uma spec por chamada, pendentes de fora | `test_f6_diario_roda_uma_spec_por_chamada_sem_os_pendentes_conhecidos` (executa o programa da fatia), CI-M4 a M8 | dia % 30, pendentes, `--ids`, spec sem mutante | passou; M4 a M8 morreram |
| Jobs do diário usam a develop, 5 partes, mutante vivo reprova | só assertIn global | `ref: develop` por job, matriz, `ruim=1` | descoberto (A1; X2, X5 e X6 sobreviveram) |
| Issue só para quebra nova | dedupe do cartão (`gh issue list`) | issue aberta recebe comentário | sem teste (A2; X8 sobreviveu) |
| Push na develop roda a suíte no 3.12 | `test_agregador_da_develop_exige_as_cinco_pernas_e_o_teto_sem_rodar_codigo`, `test_pernas_da_develop_*` | agregador `rapida` | passou |
| Nomes dos checks exigidos não mudam | `Workflows` em test_catraca (timeouts, always), `test_agregadores_*` | `bateria`, `bateria (python 3.14)` | passou |
| YAML válido (`name:` com dois pontos entre aspas) | `test_f6_todo_workflow_tem_name_de_passo_entre_aspas_quando_tem_dois_pontos` | todos os workflows | passou |
| Check `bateria` do PR não vale como prova da árvore | `test_arvore_testada.Provar.test_check_bateria_do_pr_nao_e_prova_*` | base fora do head | passou |

## Cenários e resultado real
- Trava: `flock -n /root/.forge-contrib/trava-teste-a.lock` negado (ocupada). Por isso não rodei `bin/forge-testes --vermelho` nem `bin/forge-mutante`; rodei só os testes afetados mais curtos (texto puro, 0,3 s) e, em cópias descartáveis em `$TMPDIR`, um script meu que aplica o `de`/`para` da spec e roda os testes dela.
- Verde no head: `FiacaoDoCI` mais o teste novo de `ConferirTodas` e o novo de `Provar`: Ran 15, OK.
- Vermelho (cópia do head com o `ci.yml` da base b31f01fd e sem `diario.yml`): `FiacaoDoCI` Ran 13, failures=5, errors=2; `test_f6_o_pr_roda_a_suite_uma_vez` falha e os dois testes do diário dão erro. Não é a saída oficial do `forge-testes --vermelho` (sem veredito oficial; fica para quem tiver a trava).
- Mutantes declarados (8, CI-M1 a CI-M8) conferidos contra o diff: todos morreram. Não é a saída oficial do `forge-mutante` (rc não obtido).
- Mutantes extras do QA (8): X3 (needs do agregador 3.14 vazio), X4 (sem `always()`) e X7 (e2e do diário vazio) morreram; sobreviveram X1 (fumaça `true`), X2 (suíte do diário sem `ref: develop`), X5 (mutante vivo sem reprovar), X6 (diário com 3 partes) e X8 (cartão sem dedupe).
- CI do PR #929 no head ac8202d0 (`gh pr checks 929`): verdes `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, suíte 3.12 partes 1 a 5, teto de pulados, árvore; `skipping` os de push na develop e cobertura (esperado). Vermelhos esperados: `bateria`, `bateria (pareceres)`, `catraca` (esperam parecer ou rótulo).
- Observação: o `schedule` do diario.yml só dispara com o arquivo na branch padrão (diz o próprio comentário), então o diário só começa a rodar depois do `homolog` → `main`; até lá, só `workflow_dispatch`.
- Acessibilidade e E2E de interface: não se aplicam (mudança só de workflow e testes).
