---
tipo: qa
contrato: 1
pedido: backlog-ate-sexta
branch: melhoria/backlog-lote-1111
commit: b0cf649d31e65f3342b1fd1666241bcd27a28a8a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-11
---
# QA: backlog-ate-sexta (junção melhoria/backlog-lote-1111)

Junção de 9 frentes já revisadas (maq-i9-refazer-1, tm17-dado-neutro, varredura-caminho-pessoal, tm25-pesados-stack, orcamento-tempo-no-log, fechar-medir-do-log, fechamento-540s, revisor-sem-rerrodar, diretrizes-jarvis-12-14) sobre a develop 36d976df. A bateria completa roda no CI do PR (R-QA); aqui, só os testes afetados e as mutações da junção.

## Achados
- A1 (recomendado) agents/jarvis.md:1 · a origin/develop andou 18 commits desde o 36d976df (PR 491 e outros): o merge do head com ela hoje conflita em agents/jarvis.md. Trazer a develop de novo antes do PR e reconferir.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem perda de correção na junção (E1.16/E1.17) | cherry-pick dos commits das frentes sobre 36d976df, em cópia, comparado com o head | n/a | só 1c06dc18 conflita (tests/test_forge.py); o head guarda os dois testes (test_dado_neutro... e caminho_pessoal_falha/test_caminho_do_windows_sob_mnt_falha); sem marca de conflito em arquivo rastreado |
| MAQ-I9 fatia 1 (sem-veredito no revert) | tests.test_conferir_reversao + mutantes C7-1, C7-2 | plano do revert pede a bateria inteira | passou; 2/2 morreram |
| TM-17 / varredura de caminho pessoal | tests.test_forge.VerificarContribuicao (14) + mutantes P1-P6 | /Users, /mnt/c/Users, /home com ponto ou maiúscula; dado neutro passa | passou; 6/6 morreram |
| TM-25 pesados da stack | test_hooks.Hooks.test_fixtures_do_tm25; pesados.json tem stryker e test:db | fila de um por vez | passou |
| ORCAMENTO-TEMPO-NO-LOG | test_hooks.Hooks.test_orcamento_sai_numa_linha_de_formato_fixo | formato fixo da linha | passou |
| FECHAR-MEDIR-DO-LOG | tests.test_fechar_medir + mutantes M1-M8 e fechar-medir-do-log-2 M1-M2 | log sem a linha, linha presente | passou; 10/10 morreram |
| Docs (540s, sem-rerrodar, diretrizes 12-14) | tests.test_reval_delta, test_sugerir (68 testes com test_conferir_reversao e test_fechar_medir, OK); contagem de README no test_conferir_reversao ajustada para 14 no commit 0eb79b49 | n/a | passou |

## Cenários e resultado real
- Os 4 fixtures agentes/* do test_hooks (sandbox, /proc de outro namespace) falham também na develop: não bloqueiam, conforme o brief. Não rodei o test_hooks inteiro (R-TETO); só os testes novos da junção.
- Vermelho antes do verde: cada frente trouxe os próprios pareceres; a junção não traz teste novo de regra além dos já revisados, e os mutantes acima provam que os testes caem sem a guarda.
- Changelog: 9 fragmentos em changelog.d/, um por frente; CHANGELOG.md intocado.
- Máquina: um comando pesado por vez, worktree descartável em $TMPDIR, branch não escrita.
- Registro de erro meu: um comando inicial caiu na árvore principal por falha ao criar a worktree e deixou cherry-picks na main local; desfeito com reset para 73efa627, sem envio e sem perda (a main local voltou ao estado anterior; o untracked docs/propostas/aq-orkastery-anti-alucinacao.md segue intacto).
