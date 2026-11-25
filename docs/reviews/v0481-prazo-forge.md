---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 21a96c1ab06722ed0e7b9cc7c3276912ea841b49
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481

Review por delta (E7.28) de a4d12870 a 21a96c1a. Li o delta pelo `forge-check parecer delta docs/reviews/v0481-prazo-forge.md` (`revalida: sim`, porque o parecer anterior reprovou; no domínio: `hooks/_comum.py`, `hooks/conformidade.py`, a fixture nova, as 6 specs, `tests/test_hooks.py`, `tests/test_hooks_volta_propriedades.py`, o índice das fixtures e o fragmento do changelog).

## Achados
- A1 (recomendado) hooks/_comum.py:2898 · Continua o A3 do parecer anterior. Com FIFO no .git, na sessão do Forge, `ls` recusa (S4) com o texto "a chamada com ação crítica". Quando `hook.marcado is None`, cite o .git que não respondeu.
- A2 (recomendado) hooks/_comum.py:2947 · No erro interno, o `falhar_fechado` depois do registro lê a sessão sem vigia; com FIFO no .git pode ir ao corte de 10 s, que libera. Já era assim antes do diff e exige erro interno e FIFO juntos. Vira cartão.

## Sondas
- S1 · hook real, FIFO no commondir e no gitdir da worktree, sessões Forge e projeto, raiz na worktree e na principal, push na main, `--force` e `--no-verify` (24 casos) · espera: 2 · obtido: 2 nos 24 (R-CONFORMIDADE de 3,7 a 4,3 s, ou R-MAIN e R-VERIFY direto)
- S2 · sessão de projeto, `python3 -c "import os; os.mkfifo('.git/x')"`, e também com `os.mknod` e com o `mkfifo` do perl · espera: 2 · obtido: 2 R-CONFORMIDADE (antes do diff, o mkfifo dava 0)
- S3 · sessão de projeto, `python3 -c "import os; os.mkfifo('fila')"` e `python3 -c "print('mkfifo')"` · espera: 0 · obtido: 0
- S4 · `ls` com FIFO no .git · espera: 0 no projeto · obtido: 0 no projeto; 2 na sessão do Forge (já era assim, A1)
- S5 · carga: `prazo_vencido`, sessão do Forge, linha sem marcador (sessão e registro, cada um com o seu vigia), 50 voltas, loadavg 9,9 em 12 núcleos · espera: bem abaixo de 0,5 s, e libera · obtido: mediana de 0,39 ms, pior caso de 0,66 ms, liberou nas 50
- S6 · `gh pr merge 12 --squash` e `gh pr ready 12` com FIFO, nas duas sessões (24 casos), contra o corte de 10 s · espera: decisão antes de 10 s · obtido: pior parede de 5,3 s, sem nenhum corte

## Parecer
Aprovado: os dois bloqueantes do parecer anterior foram resolvidos.

- **A1 anterior (specs).** As 7 specs voltaram a casar com a fonte, e a `lote-unico-032-l31` também foi alinhada. `tests.test_forge_mutante -k test_toda_spec_do_forge_confere` dá OK. `bin/forge-mutante --conferir --todas` dá 26 linhas, o mesmo número da base. Nenhuma delas é de spec tocada pelo diff: as 2 que casam pelo nome são `lote-unico-032-l32-2` e `-l49`, que já estavam lá.
- **A2 anterior (mkfifo por interpretador).** `mkfifo|mknod` entrou em `ESCRITA_NO_TEXTO`, com a fixture `fifo-python-mkfifo-git-projeto-bloqueia` e o M12. Na sessão do Forge, o texto de um interpretador escrevendo no `.git` segue livre, e o `os.remove('.git/x')` também. É a política de antes, e o efeito do FIFO lá agora é recusar, não liberar.
- **Ordem nova no `prazo_vencido`.** A sessão se decide primeiro, sob o seu vigia, e o registro vem depois, em `registrar_sob_vigia`, com outro vigia. O registro não muda a decisão: o `recusa` já foi calculado antes, e o `except` do registro só descarta a linha. Nos dois piores casos, o tempo total fica em 8 + 0,5 + 0,5 s, abaixo dos 10 s, e na prática ficou em 5,3 s (S6). O erro interno usa o mesmo caminho (M11). Do restante desse caminho trata o A2.
- **Testes novos.** `test_registro_que_nao_termina_nao_muda_a_decisao` usa um vigia real com sono de 5 s e confere lento e falha, com e sem marcador. `test_erro_interno_com_registro_lento_nao_espera_o_corte` confere a parede abaixo de 4 s. As sequências de alarmes armados nos testes do relógio falso passaram a esperar dois pares (sessão e registro), o que bate com o código.

Verificadores que rodei no Revisar-sha:
- `PrazoVencidoNaSessaoDoForge`, `SondaS1ComRelogioFalso` e `VigiaAgentesPesado`: 11 testes, OK.
- `bin/forge-mutante --processos 1` em `v0481-prazo-forge.json` (M1 a M8) e em `v0481-prazo-forge-2.json` (M9 a M12): todos morreram. O M4 e o M9 morreram por erro do teste declarado sob o mutante, que passa sem ele.
- `--cobertura --base a4d12870`: as specs editadas foram reconhecidas, e a da base ficou isenta fora do diff. Nenhuma guarda ficou descoberta.
- CI do #888 no 21a96c1a ainda em andamento quando escrevi. A suíte 4/5 passou nas duas versões do Python, e era ela que o A1 anterior deixava vermelha. A `catraca` espera o rótulo do dono (mudança em hooks), e a `bateria (pareceres)` espera os pareceres.
- Tamanho H1: 59 linhas de código adicionadas no item todo (base 5fb8e328), dentro do teto.
