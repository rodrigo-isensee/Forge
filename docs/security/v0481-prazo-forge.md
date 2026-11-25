---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 1d6692f507ac6bf65faf1b5be6cff0de3403c9dc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.39, #888, revalidação por delta)

Gatilhos: hook de bloqueio (`hooks/_comum.py`, `PRAZO_DO_MERGE_S`, `prazo_vencido`), R-REVIEW, R-CONFORMIDADE.

## Resumo
- Delta lido: `forge-check parecer delta` de `21a96c1a` a `1d6692f5`. No domínio: `hooks/_comum.py:2823-2831`, as 4 fixtures `tests/hooks/parecer/v0455-*`/`v0456-*` e `tests/test_hooks.py`. Fora do domínio, lidos também: o changelog, as specs `v0455-prazo.json` (P1) e `v0481-prazo-forge-2.json` (M13) e `tests/prova_de_carga.py`. A rodada E7.30 fica no git.
- **Só aperta ou neutro, por escrito.** Contra `21a96c1a`, aperta:
  - o prazo do merge cai de 8 s para 7,5 s, e o vigia recusa mais cedo;
  - um merge legítimo com `git` lento entre 7,5 e 8 s passa a recusar, falhando fechado. É custo de uso, não abertura;
  - nada que barra hoje deixa de barrar. `prazo_vencido`, `recusa_no_prazo` e `registrar_sob_vigia` não mudaram;
  - as fixtures caem de 4 s para 3,5 s e de 8 s para 7,5 s só para acompanhar a constante. A de 9 s segue recusando.
  - Contra a base `5fb8e328`, também aperta: na S3 abaixo, a base é morta pelo corte em 6 de 6 rodadas.
- **Achados anteriores:**
  - **A5 resolvido** na forma pedida, a opção (a). O nominal volta a 7,5 + 0,5 + 0,5 = 8,5 s, o mesmo de `a4d12870`. Prova:
    - teste `SondaS1ComRelogioFalso.test_recusa_do_prazo_longo_presa_deixa_folga`, que lê o `timeout` do `hooks.json`;
    - M13 morto (`bin/forge-mutante --ids M13`);
    - S3 refeita, abaixo.
    - Fica um resíduo de parede, presente desde a base, registrado como A6.
  - **A3 continua recomendado, reduzido.** O changelog agora diz "só no projeto" para o interpretador. Falta registrar as formas livres na docstring de `especial_no_git` (`hooks/conformidade.py:1773-1775`), que segue dizendo "trava nas duas sessões".
- **S3 refeita**: hook `parecer` real, `gh pr merge 1 --squash`, FIFO no `commondir` de uma worktree, sessão do Forge, `timeout 10`. Árvores por `git archive`, rodadas alternadas na mesma carga. A máquina já estava com carga de 12 a 150 (12 núcleos) por outros agentes. Código 2 é recusa; 124 é morto pelo corte, ou seja, liberado:
  - sem laços extras: head 5 de 6 recusas, 8,80-9,50 s, e 1 morta a 10,02 s com carga 23. `21a96c1a`: 3 de 6. `a4d12870`: 6 de 6, até 9,92 s. Base: 0 de 6;
  - com 48 laços de CPU: head 5 de 5, 9,02-9,48 s. `a4d12870`: 5 de 5, 9,11-9,90 s. Os dois empatam;
  - numa rodada isolada só do head, com carga de 98 a 149, foram 4 de 7 mortas.
- **CI:** o PR #888 está `CONFLICTING` com a `develop` (`3e7ad984`), em `docs/hooks-fixtures.md`. Por isso nenhuma execução do CI existe para `1d6692f5`.
  - O último CI do PR, em `f17ee6f4` (= `21a96c1a` mais docs), teve as 10 partes da suíte verdes.
  - Não há como conferir no CI as 2 falhas por tempo que o autor relata (`pesado/mesma-sessao-libera`, carga 50-62). O hook `pesado` não é tocado pelo PR.
  - Sem o bloco `- ci:` (A7). A7 nasceu bloqueante, e o `forge-check docs` o rebaixou pela G1.2: está fora das linhas do delta e não tem sonda explorável.
  - Este aprovado vale para o delta de segurança, não para o CI. O merge da `develop` que A7 pede toca o domínio (`hooks/_comum.py`, `hooks/conformidade.py`, `tests/test_hooks.py`). Isso pede nova volta por delta, com as partes do CI verdes citadas.
- Rodados aqui:
  - `SondaS1ComRelogioFalso` e `test_prazo_do_merge_abaixo_do_timeout_do_hooks_json`: 4 testes, OK;
  - M13 morto;
  - `test_prazo_do_merge` (fixtures reais com `git` lento): com carga de 20 a 85, recusou `v0456-merge-depois-de-env` por prazo, e o P1 deu "controle vermelho". É falha fechada sob carga, a mesma família que o autor relata. Quem julga é o CI.

## Achados
- A3 (recomendado) hooks/conformidade.py:1774 · a docstring de especial_no_git diz trava nas duas sessões, mas na do Forge python3 -c, perl -e, xargs por pipe ou here-string e mkfifo fora com mv, ln ou cp -a para o .git seguem livres; registrar as formas livres (o changelog já foi corrigido)
- A6 (recomendado) hooks/_comum.py:2934 · o prazo conta de inicio, depois da partida do Python e da leitura da entrada; sob carga acima de ~2x os núcleos, essa parte passa da folga de 1,5 s e o corte de 10 s mata a recusa do merge com FIFO (1 de 6 no head, empate com a4d12870, a base 6 de 6)
- A7 (recomendado) docs/hooks-fixtures.md:5 · o PR #888 está em conflito com a develop (aqui e na linha 13), e o CI não rodou em 1d6692f5: as partes da suíte que contam, entre elas as de test_hooks que o autor relata vermelhas sob carga, não estão provadas verdes; mesclar a develop e citar o CI

## Detalhe dos achados
**A7.** Evidência:
- `gh run list --commit 1d6692f5` dá `[]`;
- `gh pr view 888` dá `mergeStateStatus: DIRTY`;
- `git merge-tree --write-tree origin/develop 1d6692f5` dá conflito em `docs/hooks-fixtures.md`, nos trechos das linhas 5 e 13 da branch.

O GitHub não dispara o CI de `pull_request` num PR com conflito. O merge da `develop` também mescla sozinho `hooks/_comum.py`, `hooks/conformidade.py` e `tests/test_hooks.py`, que estão no domínio.

Correção mínima: mesclar a `develop` na branch (sem `--force`), deixar o CI rodar no head novo e citar as partes verdes. Esforço P. Dono: o autor do #888.

**A6.** Evidência: `hooks/_comum.py:2929` lê a entrada, e `:2934` fixa `inicio = relogio()`. Tudo antes disso, a partida do Python e o import do módulo, fica fora da conta do vigia. `tests/test_hooks.py:3324` (`FOLGA_DE_PAREDE_S = 1.5`) mede 1,1 s, mas a S3 refeita viu passar de 1,5 s com carga de 23 em 12 núcleos.

Caminho de ataque: o mesmo de A5. O agente planta o FIFO no `commondir` e roda `gh pr merge` com a máquina carregada. A diferença é que hoje isso não vem do delta: está em `a4d12870` e é pior na base.

Severidade: baixa. A probabilidade é baixa, porque exige o FIFO e a carga. Na sessão do Forge, o CI de pareceres segura como segundo portão.

Correção mínima: contar o prazo da partida do processo (por exemplo, `time.monotonic()` lido na primeira linha do script do hook e passado a `executar`). Junto, a opção (b) da rodada anterior: armar o vigia do registro com o que resta até um teto de parede abaixo dos 10 s. Teste no relógio falso com partida simulada. Esforço M. Dono: o autor do #888, ou um cartão próprio.

**A3.** O changelog foi corrigido em `changelog.d/v0481-prazo-forge.md:2`. Resta a docstring. O caminho e a severidade são os da rodada anterior: trava a própria sessão, sem liberar crítica. Esforço P. Dono: o autor do #888.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas:
- `forge-check parecer delta`, `git diff 21a96c1a..1d6692f5` e `git merge-tree`;
- `gh pr view`, `gh run list` e `gh run view` (CI de `f17ee6f4`);
- `bin/forge-mutante` (M13, P1);
- unittest dos testes citados;
- sondas no scratchpad da sessão, escritas em arquivo, em repositórios temporários e árvores tiradas por `git archive` (head, `21a96c1a`, `a4d12870` e `5fb8e328`): `sonda_s3.sh` e `sonda_s3_alterna.sh`.

Nada externo. Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
