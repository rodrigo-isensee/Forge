---
tipo: qa
contrato: 1
pedido: lote-prepush-parecer
branch: melhoria/lote-prepush-parecer
commit: 5ca9a43d31b1b273ae47c906800bb4cd56105962
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: lote-prepush-parecer

Escopo: E1 PREPUSH-PRIMEIRO-PARECER, E2 PARECER-PUSH-CORRIDA, E3 COMENT-RESTO (pedido `LOTE-PREPUSH-PARECER`, sem especificação de UX; as obrigações são E1 a E3 do pedido e `R-VERIFY`). Base `9c4c6159f88c`, head `5ca9a43d31b1`.

## Achados
- A1 (bloqueante) .githooks/pre-push:324 · guarda nova `[ ! -L "$1" ]` do `anotar` sem mutante declarado e sem teste: o mutante Q2 (tirar a guarda) sobrevive a `test_pre_push_parecer_curto`, `test_pre_push_parecer`, `test_pre_push_trava` e `test_pre_push_afetados`; no ramo `acrescentar` o `>>` seguiria um `.verde` que fosse link (regra do QA: linha de guarda mudada sem mutante bloqueia)
- A2 (bloqueante) tests/mutantes/lote-prepush-parecer.json:1 · lista incompleta contra o diff: faltam mutantes para as guardas mudadas em .githooks/pre-push:191 (`tem_prova "$verde"`), :205 (`curta` só fora do `--suite`), :243 (recaptura do início após a espera) e :333 (`arvore_fim = arvore_inicio`); Q4 e Q3 morrem só com testes de outros módulos, Q5 sobrevive (provável equivalente: `so_parecer` exige `n_refs=1`, que o `--suite` não tem; o autor justifica ou testa)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 primeiro parecer após o dirigido roda só as classes curtas | `test_primeiro_parecer_depois_do_envio_dirigido_roda_so_as_classes_curtas` | prova `.dirigida` presente | passou |
| E1 só o dirigido verde anota `.dirigida`, nunca `.verde` | `test_so_o_dirigido_verde_anota_a_prova_dirigida_e_nunca_a_da_suite_inteira` | suíte inteira x dirigido | passou |
| E1 prova `.dirigida` que é link é ignorada | `test_prova_dirigida_que_e_link_e_ignorada` | link simbólico | passou |
| E2 envio só de parecer não espera a trava alheia | `test_envio_so_de_parecer_nao_espera_a_trava_da_suite_alheia` | trava ocupada | passou |
| E2 envio de código continua esperando a vez e é barrado | `test_envio_de_codigo_continua_esperando_a_trava_e_e_barrado_sem_a_vez` | tempo de espera esgotado | passou |
| E2 atrás do remoto falha na hora com `git pull --rebase` (dois casos) | `test_envio_atras_do_remoto_falha_na_hora_mandando_fazer_o_pull_rebase`, `test_remoto_que_andou_e_nao_esta_aqui_manda_fazer_o_pull_rebase` | remoto ausente localmente; não fast-forward | passou |
| E1/E2 sem afrouxar o caminho curto | `test_pre_push_parecer` (20), `test_pre_push_trava` (29), `test_pre_push_afetados` (20), `test_pre_push_shellcheck` (3) | arquivo fora de docs/{reviews,security,qa,devops}/ roda a suíte | passou |
| E3 comentários alinhados (`.githooks/pre-push`, `bin/forge-fechar:375`) | leitura do diff (só comentário, +1 -1) | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_pre_push_parecer_curto`: 9 testes OK. Os outros quatro módulos do pre-push: 20, 29, 20 e 3 OK. Suíte completa não rodada por mim (decisão: só os testes do item; o pre-push roda a inteira).
- Vermelho: `bin/forge-testes --vermelho 9c4c6159f88c` saiu 124 (prazo, 74 módulos; sem veredito). Recuo, em cópia no `$TMPDIR`, com `.githooks/pre-push` da base e os testes do head: `FAILED (failures=5, errors=1)` em 9 (os seis testes de comportamento novo caem na base; os três de regressão passam nas duas), 9 OK no head. O autor deve colar a saída do `--vermelho` com veredito.
- `bin/forge-mutante tests/mutantes/lote-prepush-parecer.json`: M2 a M9 todos `morreu`, rc=0 (a lista vale só o que cobre; ver A2).
- `bin/forge-mutante --cobertura --base 9c4c615...`: `não coberto: .githooks/pre-push`, `não coberto: bin/forge-fechar` (shell não é checado por ele; a conferência foi manual contra o diff).
- Mutantes meus (spec fora do repo), com os quatro módulos do pre-push: Q1 (`-O` em `tem_prova`) sobreviveu (equivalente no teste: o arquivo é sempre do próprio usuário, sem como trocar o dono); Q6 (`-f`) sobreviveu (equivalente: `grep` falha em arquivo ausente ou diretório); Q2 e Q5 sobreviveram (A1, A2); Q3 (`:333`) e Q4 (`:191`) morreram.
- `scripts/validar-plugin.sh` não rodado por mim (só texto de agentes mudou); o pre-push do envio só de parecer roda o `forge-check docs`.
