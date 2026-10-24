---
tipo: qa
contrato: 1
pedido: PREPUSH-DELETE
branch: melhoria/prepush-delete
commit: 509dbd18123a1bedbee15af9f7f62cda426ed120
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: PREPUSH-DELETE

Escopo: `.githooks/pre-push` pula a suíte e a trava quando toda ref do push é remoção; remoção de `main`, `homolog` e `develop` segue barrada; push misto e push com código rodam a suíte. A especificação é a decisão do dono "A" do pedido (sem `CA-n` EARS); as obrigações abaixo saem dela.

## Achados
- A1 (recomendado) .githooks/pre-push:134 · comentário obsoleto: diz que o push que apaga ref segue rodando a suíte, contrário ao novo comportamento (já apontado no review).
- A2 (recomendado) changelog.d/suite-paralela-d4.md:3 · o texto diz que o push que só apaga continua rodando a suíte, contrário ao PREPUSH-DELETE (já apontado no review).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Push só de remoção sai sem suíte, trava ou fila | CT-01, CT-02, CT-08; `test_push_que_so_apaga_nao_roda_a_suite` | uma e várias remoções | passou |
| Remoção não espera trava de outra suíte | CT-09; `test_push_que_so_apaga_nao_espera_a_trava_de_outra_suite` | trava ocupada | passou |
| Remover main, homolog ou develop segue recusado | CT-03, CT-04; `test_apagar_main_homolog_ou_develop_segue_barrado`, `test_remocao_de_branch_comum_com_develop_junto_segue_barrada` | cada branch protegida, também junto de remoção comum | passou |
| Push misto roda a suíte | CT-05; `test_push_misto_remocao_mais_envio_roda_a_suite` | ordem remoção/envio | passou |
| Push com código roda a suíte | CT-06 | n/a | passou |

## Cenários e resultado real
Repositório de teste em `$TMPDIR` (remoto bare local, hook copiado do head, suíte fictícia de 2 s que grava o marcador `rodou`; o `--no-verify` só semeou o remoto do próprio fixture). Push real pelo git.

| ID | Cenário | Resultado |
|---|---|---|
| CT-01 | `git push origin --delete melhoria/a` | rc 0, 0,027 s, suíte não rodou, ref apagada |
| CT-02 | `--delete t1` (tag) | rc 0, 0,024 s, sem suíte (confere a nota da segurança) |
| CT-03 | `--delete main` | rc 1, 0,023 s, "envio direto para main bloqueado" |
| CT-04 | `:melhoria/b :develop` | rc 1, 0,025 s, barrado; `melhoria/b` continua no remoto (atômico) |
| CT-05 | `HEAD:melhoria/new :melhoria/c` | rc 0, 2,23 s, suíte rodou, criou e apagou |
| CT-06 | push de commit novo | rc 0, 2,19 s, suíte rodou |
| CT-08 | duas remoções | coberto no teste unitário (subTest "duas") |
| CT-09 | remoção com trava segurada por outra suíte, `FORGE_TRAVA_ESPERA=1` | sem aviso de espera, saiu com "suíte não roda" (a duração de 6 s medida é o `wait` do meu invólucro, não do push) |

Tempo de um push de remoção: cerca de 25 ms contra 15 a 20 min da suíte completa.

`python3 -m unittest tests.test_pre_push_trava`: 29 testes, OK (11,5 s).

Vermelho antes do verde: com o `.githooks/pre-push` de `origin/develop` no lugar, o mesmo comando falha 3 de 29 (`test_push_que_so_apaga_nao_roda_a_suite` [uma] e [duas], `test_push_que_so_apaga_nao_espera_a_trava_de_outra_suite`); hook restaurado, árvore limpa. Os testes de recusa e de push misto já passavam antes (guardam o que não pode afrouxar).

Mutação: sem ferramenta gratuita para shell na stack; não rodada. Suíte completa do repositório não rodada por mim (cabe ao push e ao CI; só a classe do pre-push, como pedido).

Sem bugs abertos.
