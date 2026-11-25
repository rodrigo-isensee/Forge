---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: 21a96c1ab06722ed0e7b9cc7c3276912ea841b49
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.30, #888, revalidação por delta)

Gatilhos: hook de bloqueio (`hooks/_comum.py`, `prazo_vencido`, `registrar_sob_vigia`, `executar`; `hooks/conformidade.py`, `ESCRITA_NO_TEXTO`), R-MAIN, R-VERIFY, R-REVIEW, R-CONFORMIDADE.

## Resumo
- Delta lido: `git diff a4d12870..21a96c1a` inteiro (`hooks/_comum.py`, `hooks/conformidade.py:130`, a fixture `fifo-python-mkfifo-git-projeto-bloqueia`, as 6 specs realinhadas e a nova `v0481-prazo-forge-2`, `tests/test_hooks.py`, `tests/test_hooks_volta_propriedades.py`, changelog). A rodada anterior (E7.26, em `a4d12870`) fica no git. Depois do Revisar-sha, `5309b5c1` só toca `docs/reviews/`.
- **Só aperta ou neutro, por escrito.** Contra a base `5fb8e328`: aperta. As 48 combinações críticas com FIFO recusam no head (na base, 18 liberavam pelo corte de 10 s), e nenhuma recusa da base vira liberação nas 146 chamadas da sonda. Contra `a4d12870`, o delta afrouxa em dois pontos, os dois por escrito:
  - a linha sem marcador com registro lento volta a liberar. É a correção pedida em A1.
  - a recusa no prazo longo ganha mais 0,5 s de registro antes de sair, e isso pode passar do corte de 10 s (A5, novo).
  - O resto aperta ou é neutro: `mkfifo` e `mknod` em `ESCRITA_NO_TEXTO` só alargam a recusa, e o registro do erro interno ganha o próprio vigia sem mudar a decisão de `falhar_fechado`.
- **Achados anteriores:**
  - A1 resolvido. A sessão se decide antes do registro (`_comum.py:2887-2892`), e o registro roda em `registrar_sob_vigia` (`:2865`). S1 refeita: o head libera nas duas variantes (raiz declarada e raiz fixada), onde `a4d12870` recusava. Teste `test_registro_que_nao_termina_nao_muda_a_decisao`, mutantes M9 e M10 mortos.
  - A2 resolvido. `ConferirTodas` passa (4 testes), e os mutantes realinhados morrem todos no head: D11; trava-crítica M1-M5; agentes-pesado M1-M6; prazo-forge M1-M8; lote-032 M1-M2. Cada um guarda o mesmo controle de antes:
    - M1 (trava-crítica) e D11 recolocam a isenção sem marcador.
    - M2 (trava-crítica) faz `recusa_no_prazo` responder sempre `True`, o mesmo que "fora da sessão vigiada" antes.
    - M3, M4 e o M1-M2 de agentes-pesado trocam o mesmo termo, agora na expressão de `recusa`.
  - A3 continua `recomendado` e mudou de forma. No projeto, `python3 -c` e `perl -e` com `mkfifo` no `.git` passaram a recusar. Na sessão do Forge, as 7 formas seguem livres, e o changelog diz o contrário (ver A3).
  - A4 resolvido. Ver `_comum.py:2946`, o teste `test_erro_interno_com_registro_lento_nao_espera_o_corte` e M11 morto. Fica fora dele, como na base, a leitura bloqueante de `sessao_vigiada` em `falhar_fechado`: só pesa com FIFO no `commondir`, e o #886 troca essa leitura.
- **Sondas refeitas** com o hook real (`python3 -s -E`, corte de 10 s), comparando o head, `a4d12870` e a base:
  - FIFO no `commondir`, no `gitdir`, no `config` e no `HEAD`, nas duas sessões: 48/48 recusam no head, em até 4,2 s; antes, em até 3,8 s.
  - As 70 formas de `mkfifo`/`mknod`: 62 recusam. As 8 livres são as de A3.
  - Linhas legítimas (P3): mesmo resultado de `a4d12870`. A sessão do Forge com FIFO no `commondir` recusa tudo, como antes, agora em 4,1-4,3 s.
  - Carga (`git` com 4 s e 1 s de atraso): idêntica a `a4d12870`. `ls`, `cat` e `git status` liberam; push na main e `--no-verify` recusam.
- **A margem do prazo longo (A5):** o hook `parecer` com `gh pr merge` e FIFO no `commondir`, na sessão do Forge, sai em 9,08 s sem carga (`a4d12870`: 8,61 s). Com a CPU carregada (48 laços de CPU em 12 núcleos):
  - head: 9,41 a 10,11 s em 7 rodadas, e numa delas o processo foi morto aos 10 s, ou seja, liberado (S3);
  - `a4d12870`: 8,99 a 9,72 s, 0 de 7 mortas.
  A causa é a soma `PRAZO_DO_MERGE_S` 8 + sessão 0,5 + registro 0,5 = 9 s nominais, mais a partida do Python e a leitura da entrada antes de `inicio`. A conta foi proposta na minha própria correção de A1 ("8 + 1 s no merge, abaixo dos 10 s") e não guardava folga de parede.
- CI do PR #888 (head `5309b5c1`, só docs depois do Revisar-sha):
  - verdes: suíte 3.12 partes 2 e 5, instalação, passos, verificações longas e árvore provada; as demais partes da suíte ainda rodavam;
  - catraca: falha só pelo rótulo do dono para `hooks/_comum.py` e `hooks/conformidade.py`;
  - `bateria (pareceres)`: falha porque faltam os pareceres.
  Rodados aqui: `ConferirTodas`, `PrazoVencidoNaSessaoDoForge`, `SondaS1ComRelogioFalso` e `VigiaAgentesPesado` (11 testes, OK), e as specs citadas no `forge-mutante`.

## Achados
- A3 (recomendado) changelog.d/v0481-prazo-forge.md:2 · o changelog diz que mkfifo no .git por interpretador recusa nas duas sessões, mas na do Forge python3 -c, perl -e, xargs por pipe ou here-string, e mkfifo fora com mv, ln ou cp -a para o .git seguem livres (no projeto, só o xargs por pipe); sem liberação, só travamento
- A5 (bloqueante) hooks/_comum.py:2893 · com o registro depois da sessão, a recusa do prazo longo (gh pr merge, 8 s) sai em 8+0,5+0,5 s mais a partida: sob carga, o hook parecer com FIFO no commondir passou dos 10 s e foi morto (liberado) em 1 de 7 rodadas; em a4d12870, 0 de 7 (S3)

## Sondas
- S3 · CARGA=1 bash sonda_merge36.sh <arvore> (FIFO no commondir, Forge, hook parecer, `gh pr merge 1 --squash`, 48 laços de CPU, timeout 10) · espera: código 2 antes de 10 s · obtido: head 1 de 7 morto aos 10,11 s, as outras 9,4-10,0 s; a4d12870 7 de 7 com 2, 9,0-9,7 s

## Detalhe dos achados
**A5.** Evidência: `hooks/_comum.py:2826` (`PRAZO_DO_MERGE_S = 8.0`), `:2829` (`PRAZO_DA_SESSAO_S = 0.5`) e `:2888-2893`. Na recusa, a sessão que não se decide gasta os 0,5 s do seu vigia, e o registro, que também espera o FIFO pelo `git` do `Hook.run`, gasta outros 0,5 s antes do `bloquear`.

Caminho de ataque: o agente da sessão planta o FIFO no `commondir` da worktree e roda `gh pr merge` com a máquina carregada (uma suíte em segundo plano basta). O corte de 10 s do `hooks.json` libera o merge sem a conferência dos pareceres. Na sessão do Forge, o CI de pareceres segura como segundo portão. No projeto, a decisão do hook é o portão.

Severidade: média, com probabilidade baixa (exige o FIFO e carga). Bloqueia porque é defeito provado num controle com gatilho e porque o delta o introduziu: em `a4d12870` a mesma sonda não liberou.

Correção mínima, uma das duas:
- (a) `PRAZO_DO_MERGE_S = 7.5`, que devolve a folga de `a4d12870`. O `forge-check pr` leva cerca de 2 s, e o comentário de `:2823-2826` muda junto.
- (b) armar o vigia do registro com `min(PRAZO_DA_SESSAO_S, max(0.05, 9.0 - (relogio() - inicio)))`, passando `inicio` e `relogio` a `prazo_vencido`.

O comentário de `:2827-2828` passa a contar a parede (partida + prazo + 0,5 + 0,5 < 10 s com folga), não só a soma dos prazos. Teste: no relógio falso de `SondaS1ComRelogioFalso`, conferir que o maior prazo mais os dois vigias ficam a pelo menos 1 s dos 10 s do `hooks.json`, lido do próprio `hooks.json`, para não depender de carga. Mutante: voltar `PRAZO_DO_MERGE_S` a `8.0` (em a) ou tirar o `min` (em b). Esforço P. Dono: o autor do #888.

**A3.** Evidência: as sondas da família (P2, 8 formas livres), `hooks/conformidade.py:130` e o changelog na linha 2. O texto "também no texto de um interpretador (`python3 -c` com `os.mkfifo`)" vem depois de "recusam nas duas sessões", mas a fixture nova é só do projeto, e na sessão do Forge `python3 -c "import os; os.mkfifo('.git/x')"` dá código 0. O caminho segue o da rodada anterior: o efeito é travar a própria sessão, sem liberar crítica (48/48 recusam). Correção mínima: dizer no changelog "no projeto" para a forma com interpretador e registrar as formas livres na docstring de `especial_no_git`, ou fechar na sessão do Forge pelo mesmo `checar_texto`. Esforço P. Dono: o autor do #888.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas:
- leitura do delta e do caminho `executar` → `prazo_vencido` → `recusa_no_prazo` / `registrar_sob_vigia`;
- `gh pr checks 888` e o log da catraca;
- `ConferirTodas` e os testes citados;
- `bin/forge-mutante` nas specs citadas;
- as sondas no scratchpad da sessão, escritas em arquivo e rodadas em árvores tiradas por `git archive` (head, `a4d12870` e a base `5fb8e328`):
  - `sonda_fifo.py` (partes 1 a 3);
  - `sonda_carga.sh`;
  - `sonda_registro.py` (S1);
  - `sonda_merge36.sh` (S3).

Só repositórios temporários; nada externo. Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
