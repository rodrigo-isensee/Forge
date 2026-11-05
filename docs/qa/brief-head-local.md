---
tipo: qa
contrato: 1
pedido: versao-034
branch: melhoria/brief-head-local
commit: f7e34819f8402d6e6e1c6b049c21e4d7903d42d3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: versao-034, E2 BRIEF-HEAD-LOCAL

Código testado: f7e3481 (head da branch 500aa80; entre os dois só mudam os pareceres de review e segurança, `git diff f7e3481 HEAD --stat`: 2 arquivos em docs/). Base 360186e. Afrouxa o `commit:` da R-BRIEF por decisão literal do dono (07:15); o rótulo `afrouxa-regra` é da E1.8.

## Achados
- A1 (recomendado) tests/test_hooks.py:1865 · test_muitos_heredocs_recusam_dentro_do_orcamento falhou na suíte (5,78 s contra limite de 5,0 s, carga 17 em 12 núcleos). Isolado passa no head e na base 360186e. Instável por carga, sem relação com o diff; dono do teste decide folga.
- A2 (recomendado) bin/forge-check:4936 · Q3 (D em `status in ("A","M")`) sobreviveu: equivalente, pois D tem modo novo 000000, que o teste de modo já recusa. Defesa em profundidade; sem ação.
- A3 (recomendado) bin/forge-testes:1 · `--vermelho 360186e` estourou 590 s sem veredito (carga). Vermelho feito à mão, abaixo; o autor repete com a máquina livre.

## Critério → teste → resultado
O pedido não traz CA em EARS; as obrigações são os controles C-1 a C-9 do modelo de ameaças.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-1 remoto conferido | test_so_o_ref_de_rastreio_sem_remoto_conferido_nao_concede_a_excecao; sonda 7 | remoto ausente/sem rede | passou |
| C-2 ancestralidade | test_head_que_nao_descende_...; test_head_com_a_arvore_do_remoto_mais_um_parecer_...; sondas 5, 6, 8 | divergente, amend, nunca enviada | passou |
| C-3 diferença de árvore, nome com controle | test_head_a_frente_so_vale_para_arquivo_novo_ou_alterado_comum; sonda 9 | quebra de linha no nome | passou |
| C-4 lista branca igual à do pre-push | test_head_a_frente_com_algo_fora_...; test_a_lista_de_pareceres_do_forge_check_e_a_do_pre_push; sondas 1 a 4 | ameacas, aceites, `_modelo`, KANBAN, ux, código | passou |
| C-5 só A e M | mesmo teste de C-3; sondas 10, 11, 11b | apagar, renomear, symlink | passou |
| C-6 só review, seguranca, qa | test_head_a_frente_nas_etapas_de_branch_inteira_continua_reprovando; sondas 12a, 12b | pr, merge-integracao | passou |
| C-7 forge-check pr não muda | test_parecer_so_local_a_frente_do_remoto_continua_sem_parecer_no_pr_pela_ref_do_remoto | ref origin sem o parecer | passou |
| C-8 aviso, não silêncio | test_head_a_frente_so_com_pareceres_passa_com_aviso_nas_etapas_de_parecer; sonda 13 | 4 pastas x 3 etapas | passou |
| C-9 conferente com o mesmo critério | test_forge.TextoDoConferenteNoLote.test_pr_da_etapa_de_merge_le_a_origin_... | texto da tabela | passou (na suíte) |

## Casos de abuso em repositório descartável (E2)
Sonda `/tmp/qa-brief-head-local-sonda.py`, repositórios `/tmp/qa-brief-head-local-*` (remoto nu fora da worktree), `bin/forge-check brief` do head: TOTAL 18 / 18. Reprovam com `commit:` (rc 1) e sem `aviso:`: código no intervalo (cita `bin/forge-check`), aceite forjado, KANBAN, docs/ux, `_modelo`, amend (cita "não descende de origin"), remoto que andou, remoto inexistente, branch nunca enviada, nome com `\n`, symlink, parecer apagado, parecer renomeado, etapas pr e merge-integracao. Caminho aceito (só pareceres à frente em docs/reviews, qa, security, devops), nas três etapas, rc 0 com:
`aviso: commit: o head ca2d772 de melhoria/x está à frente de origin/melhoria/x c7ce8f4 só com pareceres (4 arquivos); envie antes do PR (R-BRIEF)`

## Vermelho antes do verde
`bin/forge-testes --vermelho 360186e` estourou o prazo (sem veredito, A3). À mão: base 360186e extraída em `/tmp/qa-brief-head-local-dev` com o tests/test_etapa_do_brief.py do head: `Ran 74 tests ... FAILED (failures=23, errors=1)`; caem os 7 testes novos (a lista do pre-push, fora das pastas, só pareceres com aviso, árvore sem descender, parecer só local no pr) e passam os 67 antigos. No head: `Ran 74 tests in 46.149s OK`.

## Mutação
Sem spec do autor (`tests/mutantes/` não tem o pedido); spec minha em `/tmp/qa-brief-head-local-mutantes.json`, 14 mutantes, um por linha de guarda do diff: 10 morreram (Q1, Q4, Q6 a Q12, Q14), 3 equivalentes declarados (Q2, Q5, Q13: defesas inalcançáveis sem repositório corrompido, ou troca de tipo que o git rotula T) e Q3 sobreviveu como equivalente (A2). Nenhum sobrevivente real.

## Suíte inteira (tmux qa-brief-head-local, trava esperou ~1 h)
`suite-paralela: 2621 testes em 92 módulos, 2 processos`; processo 2 rc 0 (1654 testes); processo 1 rc 1 (967 testes) com uma falha, a de A1. `Ran 2621 tests in 2158.452s (2 processos) FAILED (failures=1, skipped=30, guarda=1)`, `rc=1`. A falha é de tempo sob carga e passa isolada (`Ran 1 test ... OK`) no head e na base; os 74 testes do módulo do E2 passam na suíte. A suíte limpa fica para a máquina livre ou o CI.

## Acessibilidade
n/a (ferramenta de linha de comando).
