---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: a4d1287031926560dc2742f125b5456cccaa149a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.26, #888, 1ª rodada)

Gatilhos: hook de bloqueio (`hooks/_comum.py`, `prazo_vencido` e `recusa_no_prazo`; `hooks/conformidade.py`, `especial_no_git`), R-MAIN, R-VERIFY, R-CONFORMIDADE.

## Resumo
- Lido: o diff inteiro de `5fb8e328..a4d12870` (`hooks/_comum.py`, `hooks/conformidade.py`, as 6 fixtures `fifo-*`, `tests/test_hooks.py`, `tests/test_hooks_volta_propriedades.py`, `tests/mutantes/v0481-prazo-forge.json`). Não havia parecer anterior na branch nem modelo de ameaças da demanda.
- **Só aperta ou neutro, por escrito: aperta.** `prazo_vencido` (`_comum.py:2875-2881`) recusa um conjunto que contém o da base: `recusa_no_prazo` devolve `sessao_vigiada` ou mais, e o vigia que vence ou o erro mantêm o valor inicial (`PreToolUse`, ou marcador com evento antes da ferramenta), que é a condição da base antes de olhar a sessão. A guarda ganha um ramo `elif` só para `mkfifo` e `mknod`, que antes não caíam em ramo nenhum, e `ESCRITORES` só cresce. Nas 146 chamadas das sondas, nenhuma recusa da base vira liberação no head.
- **Fecha a liberação (provado com o hook real, como o Claude Code o chama: `python3 -s -E`, corte de 10 s).** FIFO no `commondir` e no `gitdir` da worktree, e também no `config` e no `HEAD` do `.git` principal; sessão do Forge e de projeto; raiz na worktree e na principal; push na main, `--force`, `--no-verify`: as 48 combinações recusam no head em até 3,8 s. Na base, 18 delas, todas da sessão do Forge, liberavam (10 s, ou código 0 em ~8,2 s). Com o `git` lento e sem FIFO (sonda de carga), o push na main na sessão do Forge também liberava na base e agora recusa.
- **`mkfifo` e `mknod` no `.git`:** 35 formas nas duas sessões. Recusam o literal, `mknod p`, `-m`, `--mode=`, `--`, caminho absoluto, `\mkfifo`, entre aspas, `env`, `command`, `nice`, `timeout`, `sudo`, `busybox`, `bash -c`, `eval`, `.GIT`, `..`, `cd` antes, substituição, variável, curinga, chaves, `find -exec`, o `.git` da worktree e o `commondir` por caminho absoluto. Ficam livres as formas em A3, sem caminho de liberação: com o FIFO no lugar, o prazo recusa (acima).
- **O vigia de 0,5 s sob carga (pergunta do brief): sim, recusa uma linha legítima** (A1). Na sessão do Forge, uma linha sem marcador que passou dos 3 s e cujo registro (`Hook.run`, `git rev-parse`) leva mais de 0,5 s recusa com "a chamada com ação crítica". Na base ela liberava, e o requisito do item (a docstring de `recusa_no_prazo` e o changelog) só manda recusar a linha marcada. As linhas sem marcador não chamam `git` na decisão (sonda de carga: `ls`, `cat`, `git status` liberam no head com `git` de 4 s), então o caso real é uma linha longa sem marcador numa máquina carregada.
- **FIFO no `commondir` e sessão do Forge:** toda linha recusa no head (`ls src`, `cat`, `git status`, inclusive o `rm` que desfaria o FIFO). Na base, cada uma esperava 10 s e liberava. A causa é a leitura bloqueante do `commondir` em `diretorio_comum` (`_comum.py:168`), dentro da própria decisão da sessão (`e_projeto`), e não o registro: com a ordem trocada continua recusando. Isso segue a regra "sem decidir a sessão, vigia" de `sessao_vigiada` e não é achado deste item. O #886 troca essa leitura por `O_NONBLOCK` e só arquivo regular.
- Prazo total: 8 s (merge e `agentes`) + 0,5 s fica abaixo dos 10 s do `hooks.json`. Na sonda, a recusa sai em 3,6-3,8 s com o prazo de 3 s.
- CI do PR #888 no Revisar-sha: as partes 1, 2, 3 e 5 estão verdes. A parte 4/5 falha nas duas versões em `test_forge_mutante.ConferirTodas` (A2). A catraca falha só pelo rótulo do dono para `hooks/_comum.py` e `hooks/conformidade.py`, o que não é achado de segurança. `bateria (pareceres)` falha porque os pareceres ainda faltam. Rodados aqui: `ConferirTodas` (reproduz A2) e as sondas abaixo.

## Achados
- A1 (bloqueante) hooks/_comum.py:2878 · registro no erros.log sob o mesmo vigia de 0,5 s que decide a sessão: o registro lento (git do Hook.run sob carga) vence o vigia e a linha sem marcador na sessão do Forge recusa como "ação crítica", contra o requisito (só a marcada); na base liberava (S1)
- A2 (bloqueante) hooks/_comum.py:2875 · a troca de prazo_vencido tira da fonte o `de` de 7 mutantes que guardam o próprio controle (v0480-vigia-trava-critica M1-M4, v0480-vigia-agentes-pesado M1-M2, heredoc-donos D11): VIGIA-PRAZO-TRAVA, VIGIA-AGENTES-PESADO e C-4 ficam sem prova de mutação; CI 4/5 vermelho (S2)
- A3 (recomendado) hooks/conformidade.py:2511 · mkfifo no .git segue livre por `echo .git/x | xargs mkfifo` (duas sessões), `xargs mkfifo <<< .git/x` (Forge), python/perl no texto (duas) e, na sessão do Forge, mkfifo fora e mv, ln ou cp -a para o .git; sem liberação (o prazo recusa), só travamento
- A4 (recomendado) hooks/_comum.py:2934 · no ramo de erro interno, o registrar_erro segue fora de vigia: com FIFO no commondir (até o #886) e um erro interno numa linha crítica, a espera vai ao corte de 10 s e libera onde o falhar_fechado recusaria; por leitura, sem sonda

## Sondas
- S1 · sonda_registro.py: prazo_vencido real, sessão do Forge, hook.raiz no clone, marcado False, PreToolUse, git do PATH com sleep 1 · espera: libera (None), como a base · obtido: head codigo 2 "R-CONFORMIDADE: o hook não decidiu em 3 s a chamada com ação crítica"; base e correção None
- S2 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes no a4d12870 · espera: nenhuma spec fora da fonte · obtido: FAILED, 7 specs (heredoc-donos D11; v0480-vigia-agentes-pesado M1, M2; v0480-vigia-trava-critica M1 a M4)

## Detalhe dos achados
**A1.** Evidência: `hooks/_comum.py:2877-2881`. `registrar_erro` e `recusa_no_prazo` dividem um único vigia de `PRAZO_DA_SESSAO_S`, e o vencimento por causa do registro mantém `recusa` no valor inicial. `registrar_erro` chama `Hook.run`, que chama `copia_principal`, que roda `git rev-parse --git-common-dir`: um processo novo, que numa máquina carregada passa fácil de 0,5 s. A mensagem fala em "ação crítica" para uma linha que não tem marcador. Caminho de ataque: nenhum, é recusa indevida (disponibilidade) que o requisito do item proíbe. Severidade baixa, mas é defeito provado (S1) e é a pergunta do brief. Correção mínima, provada numa cópia de rascunho: decidir primeiro `recusa = recusa and recusa_no_prazo(...)` sob o vigia de 0,5 s e depois registrar sob um vigia próprio de 0,5 s, cujo vencimento ou erro não muda `recusa` (`except (PrazoVencido, Exception): pass`). Com isso, S1 libera, e as 48 combinações críticas com FIFO continuam recusando: no `commondir` porque a sessão não se decide (falha fechado), no resto pela sessão. Teste: um caso em `PrazoVencidoNaSessaoDoForge` com `registrar_erro` lento (`side_effect` que dorme ou lança `PrazoVencido`), `marcado=False` e sessão do Forge, com resultado esperado `None`; o caso marcado continua dando 2. Atualizar `relogio.armados` nos dois testes de relógio falso (dois vigias). O prazo total fica em 3 + 0,5 + 0,5 s (ou 8 + 1 s no merge), abaixo dos 10 s. Esforço P. Dono: o autor do #888.

**A2.** Evidência: S2 e o CI do PR (parte 4/5, 3.12 e 3.14). Os `de` que sumiram são as linhas antigas de `prazo_vencido`: `if evento == "PostToolUse" or not sessao_vigiada(hook, clone_do_forge):` e `if critico is None and evento != "PreToolUse":`. Caminho: nenhum ataque direto, mas as guardas de mutação do controle que este item altera deixam de rodar. Uma regressão futura que volte a liberar no prazo vencido (o contrário de E7.23) passaria sem teste vermelho. Correção mínima, no mesmo commit da mudança: realinhar as 7 specs ao código novo, cada uma com a mesma guarda. Mapeamento das 7:
- v0480-vigia-trava-critica M1: a isenção sem marcador volta (por exemplo, `hook.marcado is not False and` em `recusa`).
- v0480-vigia-trava-critica M2: fora da sessão vigiada libera.
- v0480-vigia-trava-critica M3: `critico is not None or evento == "PreToolUse"` trocado.
- v0480-vigia-trava-critica M4: `evento != "PostToolUse"` trocado.
- v0480-vigia-agentes-pesado M1: `critico is None` libera.
- v0480-vigia-agentes-pesado M2: sem marcador, recusa fora do PreToolUse.
- heredoc-donos D11: `hook.marcado is False` isenta com corpo pendente na sessão vigiada.

Conferir com `bin/forge-mutante --conferir --todas` e rodar as 7. `critério mudou:` não se aplica: o achado nasce bloqueante porque as specs guardam o controle com gatilho tocado por este delta (no #886 a spec era de outro controle e ficou `recomendado`). Esforço P. Dono: o autor do #888.

**A3.** Evidência: sonda da família (`sonda_fifo.py`, parte 2). Na sessão do Forge, `echo .git/x | xargs mkfifo`, `xargs mkfifo <<< .git/x`, `python3 -c "import os; os.mkfifo('.git/x')"`, `perl -e 'use POSIX; POSIX::mkfifo(".git/x", 0600)'` e `mkfifo src/q && mv|ln|cp -a src/q .git/x` dão código 0. No projeto, as do `xargs` por pipe e as dos interpretadores dão código 0, e `mv`, `ln` e `cp` recusam pela regra do `.git`. O PR já declara a forma com interpretador. Caminho: quem planta o FIFO é o próprio agente da sessão. O efeito é travar a própria sessão (todas as linhas recusam até alguém tirar o FIFO por fora), não liberar push na main, `--force` ou `--no-verify` (48/48 recusam). Severidade baixa. Correção mínima: escrever no changelog e na docstring de `especial_no_git` que a trava cobre o programa no argumento e não o FIFO criado por outro meio. Se quiser fechar, `mkfifo` e `mknod` em `ESCRITA_NO_TEXTO` (interpretadores) e o alvo do `xargs` lido da entrada como opaco. Esforço P. Dono: o autor do #888.

**A4.** Evidência: `hooks/_comum.py:2933-2935`, igual na base. Caminho: exige um erro interno do hook numa linha crítica e um FIFO no `.git`. Hoje não há como provocar o primeiro de propósito, por isso fica sem sonda. Severidade baixa. Correção mínima: o mesmo vigia de registro de A1 em volta de `registrar_erro(erro)` no ramo `except Exception`, sem mudar a decisão de `falhar_fechado`. Esforço P. Dono: o autor do #888, ou item próprio.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas:
- leitura estática do diff e do caminho `executar` → `prazo_vencido` → `registrar_erro` / `recusa_no_prazo` → `sessao_vigiada` / `diretorio_comum`;
- `gh pr checks 888` e os logs dos jobs que falharam;
- `ConferirTodas` local;
- as sondas no scratchpad desta sessão, escritas em arquivo:
  - `sonda_fifo.py`, com as partes 1 (48 críticas com FIFO), 2 (70 formas de `mkfifo`/`mknod`) e 3 (28 linhas legítimas, com e sem FIFO);
  - `sonda_carga.sh` (`git` lento, sem FIFO);
  - `sonda_registro.py` (S1);
  - `sonda_dbg.sh` (onde a decisão espera).

As sondas rodaram o head, a base (`git archive 5fb8e328`) e uma cópia com a correção de A1. Só repositórios temporários; nada externo.

Varredor de segredos, SAST e auditor de dependências: o delta não traz dependência nem segredo.
