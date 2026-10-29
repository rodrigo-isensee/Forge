---
tipo: qa
contrato: 1
pedido: lote-prepush-parecer
branch: melhoria/lote-prepush-parecer
commit: 97629b0d4ba02e6367aae0bafb4198ab2c13dead
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: lote-prepush-parecer

Escopo: E1 PREPUSH-PRIMEIRO-PARECER, E2 PARECER-PUSH-CORRIDA, E3 COMENT-RESTO (pedido `LOTE-PREPUSH-PARECER`, sem especificação de UX; as obrigações são E1 a E3 do pedido e `R-VERIFY`). Base `9c4c6159f88c`, head `97629b0d4ba0` (volta 1, revalidação por delta 95c7b85..97629b0 sobre o parecer reprovado anterior).

## Achados
(vazio) A1 e A2 do parecer anterior estão resolvidos: M10 a M13 existem e morrem; o Q5 anterior é equivalente (ver abaixo).

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
| E1/E2 guarda do `anotar` não segue prova que é link (A1 anterior) | `test_prova_da_suite_que_e_link_nao_e_seguida_ao_anotar_o_envio_curto` | link simbólico no `.verde` | passou |
| E2 quem esperou a vez anota a árvore do início (A2 anterior) | `test_quem_esperou_a_vez_anota_a_arvore_do_inicio_da_suite` | árvore mudou durante a espera | passou |
| E3 comentários alinhados (`.githooks/pre-push`, `bin/forge-fechar:375`) | leitura do diff (só comentário, +1 -1) | n/a | passou |

## Cenários e resultado real (head 97629b0)
- Testes: `test_pre_push_parecer_curto` 11 OK (eram 9; +2 novos), `test_pre_push_parecer` 20 OK, `test_pre_push_trava` 29 OK, `test_pre_push_afetados` 20 OK. Suíte completa não rodada por mim (só os testes do item; o pre-push roda a inteira).
- Vermelho por recuo (cópia em `$TMPDIR`, `.githooks/pre-push` da base 9c4c615 e testes do head): `test_pre_push_parecer_curto` `FAILED (failures=6, errors=1)` em 11 (os testes de comportamento novo caem; os de regressão passam); no head, 11 OK. `test_commit_no_meio_da_suite_nao_grava_prova` (M13) já existia na base e passa nas duas: o teste é de regressão, e a prova dele é o mutante M13 morrer.
- `bin/forge-mutante tests/mutantes/lote-prepush-parecer.json tests/mutantes/lote-prepush-parecer-b.json` (uma rodada, ids únicos, rc=0): M2 morreu :191, M3 :177, M4 :336, M6 :205, M10 :324, M11 :191, M12 :242, M13 :333, M5 :209, M7 :334, M8 :121, M9 :115. Todos os 12 morreram.
- Lista contra o diff: as linhas de guarda mudadas apontadas antes (:191, :205, :243, :324, :333) têm mutante; nenhuma sem mutante.
- M6 x Q5: o M6 troca a linha `:205` por `curta=1` e o teste do envio de código o mata (morreu). A parte `modo_suite -eq 0` da guarda é equivalente: `:104` zera a entrada no `--suite` e `:181` exige `n_refs=1`, então `so_parecer` já devolve 1; a justificativa está declarada no `guarda` do M6 e eu a aceito. Não é bloqueante (o Q5 anterior, que sobrevivia, é esse equivalente).
- `scripts/validar-plugin.sh` não rodado (o delta 95c7b85..97629b0 só toca teste e specs; agentes e hook não mudaram desde o parecer anterior).
