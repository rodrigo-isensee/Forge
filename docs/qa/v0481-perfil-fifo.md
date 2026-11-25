---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-perfil-fifo
commit: 8dfe968f7cfc0c8240a62136b6af02a49bc6d3df
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 (E7.17), #886: texto da recusa sem FIFO no perfil nem git

Classe C, correção sem especificação de UX nova (sem plano antecipado). Obrigações: `R-VERIFY`, `R-MAIN`, ADR 0003 (fixtures), A2 e S3 da segurança no #885: com FIFO em `.forge/perfil`, a recusa sai com a regra certa, sem esperar, e o prazo vencido na escolha do texto não vira liberação.

## Achados
- A1 (recomendado) hooks/conformidade.py:1582 · `Hook.iniciante` (read_text) ainda espera o FIFO em `perguntar` e na guarda de escrita do perfil (1740): 3 s e, no projeto, recusa "não decidiu"; na sessão do Forge a escrita ao perfil libera após 3 s. Item próprio.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Push na main, `--force`, `--no-verify` recusam com a regra certa, FIFO no perfil, sessões Forge e projeto | `RecusaComFifoNoPerfil.test_recusa_com_a_regra_dela_e_sem_prazo_vencido` (6 subtestes) | FIFO no perfil, sem `não decidiu` | passou |
| Leitura do perfil não espera o FIFO nem chama git | `test_fifo_no_perfil_nao_espera_e_vale_experiente` (alarme 5 s, Popen proibido) | FIFO; valor `Iniciante` com caixa | passou |
| Worktree com FIFO lê o perfil da cópia principal, sem git | `test_worktree_com_fifo_le_o_perfil_da_copia_principal` | FIFO na cópia, perfil na principal | passou |
| Prazo vencido na escolha do texto cai no texto técnico e a recusa segue | `test_prazo_vencido_na_escolha_do_texto_recusa_com_o_texto_tecnico` + fixture `trava-prazo-no-perfil-bloqueia-iniciante` | prazo forçado em `perfil_iniciante` | passou |
| Nada deixa de barrar; iniciante ainda recebe o texto simples | `test_perfil_iniciante_recebe_o_texto_simples` | perfil regular, `iniciante` | passou |

## Cenários e resultado real
- Classe rodada (não o módulo inteiro): `python3 -m unittest tests.test_hooks.RecusaComFifoNoPerfil` -> `Ran 5 tests ... OK` (1,4 s).
- Vermelho antes do verde, à mão (o `forge-testes --vermelho` com `--modulos test_hooks` roda o módulo inteiro, fora do que o brief permite; sem `--modulos`, estourou meu prazo de 580 s sem veredito, então não vale): cópia em `$TMPDIR` com `hooks/conformidade.py` da base `5fb8e328`: `Ran 5 tests ... FAILED (failures=4, errors=2)`. Os 4 subtestes de push na main e `--force` (Forge e projeto) falham; `perfil_iniciante` ausente derruba 2 testes por `AttributeError`. O `--no-verify` já passava na base.
- Mutação: `bin/forge-mutante tests/mutantes/v0481-perfil-fifo.json --processos 2` -> rc 0, M1 a M7 `morreu` (linhas 1516, 1519, 1523, 1524, 1573, 1575, 1577). `forge-mutante --cobertura --base 5fb8e328`: as 5 condições do diff `coberta`, nenhuma `não coberta`. Sem mutante: o limite de 64 bytes (`os.read(fd, 64)`), que não muda o resultado de nenhum valor lido (sem consequência na decisão).
- Sonda extra (arquivo `sonda_fifo.py` no scratchpad, contra a árvore do PR), FIFO em `.forge/perfil`: push na main (R-MAIN), `--force` e `--no-verify` (R-VERIFY) recusam com a regra certa, 0,2 a 0,3 s, nas duas sessões. Controle com perfil regular `experiente` e `iniciante`: mesmas decisões de antes, `git reset --hard` pergunta só no projeto iniciante.
- Resíduo (A1): ainda com FIFO, `git reset --hard` no projeto recusa em 3,2 s por "não decidiu" (perfil experiente liberaria; falha fechada) e `Write` em `.forge/perfil` leva 3,2 s (Forge: libera; projeto: recusa por prazo). Nenhuma recusa que existia deixou de existir; o resíduo é o `Hook.iniciante` que o item deixou de fora, então não bloqueia este PR. Resposta ao brief: não precisa entrar neste item, mas pede cartão próprio (trocar `Hook.iniciante` pela mesma leitura sem espera e decidir o prazo vencido nesses dois pontos).
- CI do sha 8dfe968f: `bateria (python 3.14)` success (check-run 138975314335), suítes 3.12 e 3.14 verdes, tetos de pulados verdes. `bateria (pareceres)` e `catraca` falham no mesmo run do sha: não li o log (cache de `gh` somente leitura); `bateria (pareceres)` é o esperado antes dos pareceres desta etapa. Quem mescla confere os dois depois dos pareceres.
