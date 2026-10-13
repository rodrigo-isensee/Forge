---
tipo: review
contrato: 1
pedido: hook-conformidade
branch: melhoria/hook-conformidade-v2
commit: c175f6b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: hook `conformidade`, `parecer` com `gh pr merge` e autoria dos pareceres

Escopo: `origin/develop..a3b0be1` (4 commits): `hooks/conformidade.py`, `hooks/conformidade.json`, `hooks/parecer.py`, `hooks/_comum.py`, `hooks/hooks.json`, `bin/forge-check`, fixtures e testes, `docs/hooks.md`, `CHANGELOG.md`. Referências: ADR 0009 (seções 2, 3, 6 e 7), ADR 0003 e ADR 0008 (4.3).

Como revisei: leitura do diff; `python3 -m unittest discover -s tests` (93 testes, verde); execução do hook, fora dos fixtures, num projeto temporário com `.forge/versao`, simulando o trabalho normal de cada papel (cerca de 150 comandos e escritas), mais um teste de erro interno e uma medição de tempo.

Parecer: **reprovado**, com 4 ajustes que bloqueiam. A arquitetura está certa: a política fica no JSON, o Write/Edit decide pelo `file_path` resolvido e o papel vem do `agent_type`, com o prefixo `forge:`. O trabalho normal de dev, QA, tech-lead e Jarvis passa sem falso bloqueio. Os problemas são três: a falha fechada pode paralisar a escrita de código comum; instruções de agentes e regras contradizem o hook; os lançadores `env` e `sudo` deixam passar o que a documentação diz que é barrado.

## O que está correto
- **(a) Sem falso bloqueio no trabalho normal**, reproduzido:
  - dev: `npm test`, `pytest | tee log`, `git add/commit`, `git push -u origin feature/x`, `git merge develop` na branch de trabalho, `rm -rf node_modules`, `docker compose up`, `cat .env.example`, `git stash push`;
  - QA: `npx playwright test`, `npx playwright install`, `npm ci && npm run e2e`, `pnpm install --frozen-lockfile`, `yarn install --immutable`, evidências e parecer em `docs/qa/` (Write e heredoc);
  - tech-lead: commit com mensagem em heredoc contendo "merge"/"--force", `git push -u`, `gh pr create`, `gh pr view/list/checks`, `git merge origin/develop`, `git merge --no-ff` na `develop`, `gh pr merge <branch>`, parecer em `docs/reviews/`, `git push origin --delete feature/x`;
  - Jarvis: ler e editar o `KANBAN.md`, gravar `docs/pedidos/`, `gh pr create`.
  - Nenhum erro interno em cerca de 60 linhas de shell variadas (laços, `$(...)`, substituição de processo, `exec 3>&1`, `cd -`, heredocs, aspas desbalanceadas).
- **(c) Sessão principal sem `agent_type` vira `jarvis`**: cria PR (`gh pr create` passa; o `parecer` continua exigindo os pareceres), mas não mescla (`gh pr merge` e `git merge` na `develop` saem com `R-CONFORMIDADE`; na `main`, `R-MAIN`). Não grava `docs/reviews/`, `docs/qa/`, `CLAUDE.md` nem `.claude/`. É o que pedem a matriz da ADR 0009 e a R-CONTRIB ("projeto abre PR, nunca mescla").
- **(d) Prefixo `forge:` obrigatório**: `tech-lead`, `Forge:tech-lead` e `other:tech-lead` caem em `dev`; só `forge:tech-lead` grava `docs/reviews/`. Um agente local com o mesmo nome não herda o papel.
- **Bloqueios corretos:** push para `develop` por nome, por `HEAD:refs/heads/develop`, por `--delete` e por `-C`; `--force-with-lease`, `+refspec`, `--no-verify`, `commit -n`; `core.hooksPath` por `-c`, por `config --global`, por `--unset` e por `GIT_CONFIG_KEY_*`; `rm .githooks/pre-push`; `gh api` de merge e de refs.
- **(e) Desempenho:** mediana de 47 a 50 ms por chamada nesta máquina (p90 de 62 ms; um `python3` vazio custa 22 ms). Fica abaixo do orçamento de 100 ms.
- **(f) Neutralidade e custo zero:** só biblioteca padrão; sem rede (a base do PR vem do git local); o slug do Forge vem do `plugin.json`; nenhum termo de projeto. O teste `Neutralidade` passa.
- **(g) O que é [B] está documentado** em `docs/hooks.md` ("Limites conhecidos" e "Ainda não coberto"), incluindo que o hook não está ativo no próprio Forge (ADR 0008, 4.4). As exceções estão nos achados B3 e R1.
- Autoria: o hash é do texto sem espaços nas pontas, igual no hook e no `forge-check`; o arquivo de autoria é lido da cópia principal, então as worktrees somam no mesmo arquivo; sem o arquivo (CI), o comportamento é o de antes.

## Achados: bloqueiam

**B1. A falha fechada casa o marcador no conteúdo e paralisa a escrita de código comum.**
- Onde: `hooks/_comum.py:265` (`critico.search(bruto)`) e `hooks/conformidade.py:24-27` (`CRITICO` sem `\b`).
- Problema: `bruto` é o JSON inteiro, incluindo `content`/`new_string` do Write/Edit. Reproduzido com um `.forge/config.json` que não é objeto. Esse arquivo é só do usuário, e o erro está em `hook.projeto()`, antes de qualquer decisão. Nesse estado, ficaram bloqueados:
  - `Write` de `src/app.js` com `a.push(1)`;
  - `Edit` com `merge(a,b)`;
  - `npm test -- merge.spec.ts`.

  Ou seja, todo arquivo JS que use `push` fica bloqueado até o usuário intervir. Além disso, `merge`/`push` sem borda casam com `pushd`, `emerge` e `mergeSort`.
- Sugestão: com o JSON válido, casar `CRITICO` só em `tool_input.command` e em `file_path`/`notebook_path`; usar o `bruto` só se o JSON não abrir. Pôr `\b` em `merge`/`push`. No Write/Edit, decidir pelo caminho sem depender de `config()`: a config inválida usa o padrão e vai para o log. Faltam fixtures para os dois casos.

**B2. Instruções e regras contradizem o hook no fluxo normal (ADR 0002, uma fonte por regra).**
- Onde e problema:
  - `skills/iniciar-projeto/SKILL.md:16` manda o Jarvis preencher com o usuário as seções do `CLAUDE.md`. O passo 8 grava `.forge/versao` antes disso, então o `Edit` é barrado.
  - `agents/jarvis.md:79` e `agents/agile-coach.md:21` mandam registrar exceções locais no `CLAUDE.md` por PR.
  - `docs/regras/R-CONTRIB.md:12` e `agents/jarvis.md:62` dão ao Jarvis um checklist de merge na `develop`/`homolog`, mas o hook nega merge ao `jarvis`, como pede a matriz da ADR 0009.
- Sugestão: seguir a ADR 0009, seção 4 ("o agente propõe o diff, o usuário aplica") na skill, no Jarvis e no coach; o checklist de merge da R-CONTRIB passa a ser só do `tech-lead`. Com isso, o Jarvis não bate num bloqueio já na abertura de um projeto.

**B3. Os lançadores `env` e `sudo` perdem as opções do comando seguinte.**
- Onde: `hooks/conformidade.py:84-91` (`sem_lancadores`).
- Problema: para `env`, o filtro tira todo argumento que começa com `-` da linha inteira, não só as opções do `env`. Para `sudo`, as opções não são puladas. Reproduzido, todos saem com 0:
  - `env FOO=1 git push --force origin feature/x`;
  - `env -i bash -c 'git push origin develop'` (o `-c` some);
  - `sudo -u x git push origin develop` (o programa vira `-u`).

  O `docs/hooks.md` afirma que os lançadores são seguidos.
- Sugestão: pular só as opções do próprio lançador:
  - `env`: `-i`, `-0`, `-u NOME`, `-C DIR`, `-S`, `--`;
  - `sudo`: `-u`, `-g`, `-C`, `-D`, `-p`, `-r`, `-t`, `-U` levam valor; as demais são booleanas.

  Faltam fixtures `env-*`/`sudo-*` para os três casos.

**B4. Os 4 commits da branch têm o autor `t <t@t>`.**
- Onde: `b2ba1d6`, `fba5049`, `b038940`, `a3b0be1`.
- Problema: a identidade vazou para o `.git/config` comum (ver a investigação abaixo). O mesmo vale para os commits de `melhoria/catraca-ci` a partir de 22:33. Nenhuma das duas branches foi enviada ao `origin`.
- Sugestão: o usuário tira a seção `[user]` do `.git/config` do clone principal (ajuste local dele). Depois, o autor de cada branch reescreve a autoria antes do push: `git rebase origin/develop --exec 'git commit --amend --no-edit --reset-author'`.

## Achados: recomendados
- **R1. `git config` de escrita não é barrado** (`hooks/conformidade.py:271-273`). `git config user.email t@t && git config user.name t` passa para todos os papéis, e foi o vetor do incidente. Sugestão: barrar `git config` sem `--get`/`--list`/`--show-*` e o `git -c user.*=...` para todos os agentes [B], com fixture; ou registrar a lacuna em "Limites conhecidos". Numa worktree, o `git config` sem `--worktree` grava no `.git/config` comum a todas as cópias.
- **R2. Arquivos em vigor do `~` sem proteção** (`hooks/conformidade.json:28-33`). `~/.claude/CLAUDE.md`, `~/.claude/commands/` e `~/.claude.json` são graváveis por Write. A ADR 0009, seção 3, cobre `~/.claude` inteiro. Sugestão: incluí-los, com fixtures.
- **R3. Pacotes.**
  - O QA é barrado em instalações que seguem o lockfile em outras stacks: `composer install`, `poetry install`, `bundle install`, `uv sync`.
  - A dica é sempre a do npm (`hooks/conformidade.py:359`).
  - `pip install -r requirements.txt pacote-novo` passa como congelado, porque `-r` está em `flags_congeladas` (`conformidade.json:59`).
  - `yarn` sem subcomando passa.

  Hoje só existe a stack `node-react`, então o impacto é baixo. Sugestão: dica por gerenciador e "congelado" por gerenciador; para `pip`, só `--require-hashes` ou `-r` sem pacote extra.
- **R4. Falso positivo de escrita no texto** (`hooks/conformidade.py:31-32`). `ESCRITA_NO_TEXTO` casa `replace` e o literal `'a'`. `python3 -c "print(open('CLAUDE.md').read().replace('a','b'))"`, que só lê, é barrado para o Jarvis. Sugestão: casar modos de abertura (`open(..., 'w'|'a')`) e chamadas de escrita, não a palavra solta.
- **R5. Ativação no próprio Forge** (`hooks/conformidade.py:63-64` e `140-141`). `em_qualquer_lugar` barraria `templates/projeto/CLAUDE.md`, `templates/projeto/.claude/`, `templates/projeto/.githooks/` e `templates/projeto/.forge/config.json`, e melhorar o modelo de projeto viraria tarefa só do usuário. Hoje o Forge não tem `.forge/versao`, então nada disso age. Os fixtures `regra-*` simulam um clone com `.forge/versao`, que não existe na realidade. Sugestão: anotar no cartão da ativação (ADR 0008, 4.4) e em `docs/hooks.md:25` que as regras de "clone do Forge" só valem depois da ativação.
- **R6. Escopo do `git -C`.** `git -C <outro repositório> push origin develop` é barrado mesmo quando o outro repositório não é projeto do Forge (`hooks/conformidade.py:274-278` e `294-321`). Severidade baixa: o push direto já é proibido.
- **R7. Documentos defasados.**
  - `bin/forge-check:201` ainda diz "nos hooks vira erro interno, que libera".
  - A ADR 0003, item 4, não traz a nota "emendado pela ADR 0009, seção 7".
  - A ADR 0009 continua "Estado: proposta": a aceitação é decisão do usuário e deve vir antes da promoção a `homolog`/`main`.
- **R8. Custo do `PostToolUse`.** Todo Bash/Write/Edit roda o hook de novo, carregando `parecer` e `forge-check`, só para a autoria. Sugestão: um pré-filtro barato (`docs/reviews`/`docs/qa` na entrada crua) antes dos imports corta cerca de metade do custo extra por chamada.
- **R9. Transição da autoria.** Assim que `autoria.jsonl` existe, ficam sem registro e são recusados pelo `forge-check pr`:
  - pareceres de pedidos em andamento gravados antes da 0.7.0;
  - pareceres corrigidos com `sed -i`;
  - pareceres editados à mão pelo usuário.

  O arquivo também não tem rotação. Sugestão: documentar no CHANGELOG/migração (ou exigir só para pareceres gravados depois da instalação) e rotacionar como o `erros.log`.

## Investigação: `user.name=t` no `.git/config` do clone principal (só leitura)
Hipótese mais provável: o vazamento **não** veio do `HookPrePush.setUp`. Veio de um commit manual de teste adversarial da catraca, feito numa worktree temporária do clone principal, com `git config user.email t@t` e `git config user.name t` sem `--worktree`. Numa worktree, esse comando grava no `.git/config` comum.

Evidências:
1. O `mtime` do `.git/config` é 22:30:14.670. Existe um commit pendurado, `a15b455`, de autor e committer `t <t@t>`, criado às 22:30:14 com a mensagem `x`, cujo pai é `57b77c1`, o HEAD de `melhoria/catraca-ci` naquele instante. O diff dele é um ataque de teste à catraca: acrescenta ao `release.yml` um passo que imprime todos os segredos do workflow (o que o job `segredos` deve barrar) e remove `limite_linhas.agente` de `tests/config.json`. Ele não está em nenhuma ref nem foi enviado.
2. O diretório `.git/worktrees/` mudou às 22:30:21, 7 segundos depois. É compatível com a remoção da worktree temporária: a única registrada hoje é a desta branch, criada às 22:14.
3. A troca de identidade está entre 22:27:56 e 22:30:39. Os commits de 22:27:56 da catraca são de "Rodrigo Isensee". A partir daí, tudo é `t`: um stash nesta worktree às 22:30:39 (`476afe8`), os 4 commits desta branch às 22:34:39 e os da catraca a partir de 22:33.
4. Hoje o `.git/config` tem só `[user]`, sem `commit.gpgsign`. O `setUp` grava três chaves em sequência (`user.email`, `user.name`, `commit.gpgsign`), então o conteúdo combina melhor com os dois `git config` manuais.
5. Nenhum caminho dos testes atuais alcança o repositório real. Em `tests/test_forge.py`, `tests/test_hooks.py` e `tests/test_catraca.py` (`develop`, `melhoria/catraca-ci` e esta branch), todo git roda como `git -C <temporário>` com `ambiente_limpo()` (sem `GIT_*`, com `GIT_CONFIG_GLOBAL=/dev/null`). O `IsolamentoDoGit` cobre `GIT_DIR`/`GIT_WORK_TREE` herdados. Os hooks e o `forge-check` também limpam `GIT_*`.

Risco residual encontrado: os testes da `origin/main` (0.2.x) ainda chamam `git` sem `-C`, com o ambiente herdado, e o `pre-push` da `main` não faz `unset GIT_*`. Rodar o `pre-push` numa worktree com o conteúdo da `main` repetiria o vazamento antigo. Foi o que aconteceu às 16:44: `stash@{0}`, "WIP on melhoria/retomada-de-sessao: 701b5d2 inicio", de autor `t <t@t>`, com o `inicio` do `setUp`. Isso se resolve quando a próxima release chegar à `main`.

Prevenção: R1 (barrar `git config` de escrita), o sandbox da ADR 0009, seção 5 (o `.git/config` comum fica fora da pasta de trabalho de uma worktree) e uma instrução para o QA testar a catraca num clone temporário, nunca numa worktree do clone principal.

## Próximo passo
Corrigir B1, B2 e B3 com fixtures; reescrever a autoria dos commits (B4) depois de o usuário limpar a identidade; nova rodada de review no HEAD resultante. Os itens R podem virar cartão, menos R1 e R7, que cabem nesta mesma branch.

## Revalidação (b1bd4ce)
Diff `a3b0be1..b1bd4ce`. 96 testes verdes, com fixtures novos para cada correção.

| # | Achado | Situação |
|---|---|---|
| B1 | Falha fechada casava o conteúdo gravado | **Corrigido.** `texto_da_acao` usa só `command`, `file_path` e `notebook_path`; a entrada crua só vale se o JSON não abriu. `CRITICO` exige `git`/`gh` antes de `merge`/`push`, com `\b`. Fixtures: Write JS com `push`, Edit com `merge(`, teste com `merge` no nome. |
| B2 | Instruções contradiziam o hook | **Corrigido, por outro caminho que o sugerido:** em vez de mudar a skill e o Jarvis, a política passou a liberar ao `jarvis` o `CLAUDE.md` do projeto e o merge em `develop`/`homolog` (ainda sujeito ao `parecer`; a `main` segue barrada), com ajuste registrado na ADR 0009 e em `docs/hooks.md`. O `agile-coach` passou a propor a exceção no relatório. Ver N1. |
| B3 | `env` e `sudo` perdiam opções | **Corrigido.** `LANCADORES` leva as opções com valor de cada prefixo (inclui `nice`, `timeout`, `xargs`); fixtures `env-*`, `sudo-*`, `nice-*`, `timeout-*`, `xargs-*`. |
| B4 | Autoria `t <t@t>` | **Não corrigido.** 14 commits do intervalo `origin/develop..b1bd4ce` seguem como `t`, e o `[user]` ainda está no `.git/config` comum. Mecânico: o usuário limpa o `.git/config`, depois `git rebase origin/develop --exec 'git commit --amend --no-edit --reset-author'`, antes do push. |
| R1 | `git config` de escrita | **Corrigido.** Barra `user.*`, `core.*`, `commit.gpgsign`, `include*`, `alias.*` para todos os papéis; leitura e `--worktree` passam. A suíte confere que o `.git/config` real não muda. |
| R2 | Arquivos do `~` | **Corrigido.** |
| R3 | Pacotes | **Corrigido** por gerenciador (`composer`, `poetry`, `bundle`, `pip -r`); a dica ficou genérica. `yarn` sem subcomando segue passando (baixa). |
| R4 | Falso positivo de escrita no texto | **Corrigido** (`.replace(` e `'a'` não casam). |
| R5, R8, R9 | Ativação no Forge, pré-filtro, transição da autoria | **Registrado** como pendência no CHANGELOG e em `docs/hooks.md`; aceito. |
| R6 | `git -C` em outro repositório | **Registrado** como limite conhecido. |
| R7 | Documentos defasados | **Parcial.** Docstring do `forge-check` e ADR 0003 corrigidas; a ADR 0009 segue "proposta" (aceite é do usuário, antes da promoção). |

Achados novos:
- **N1 (média):** o merge do `jarvis` vale também num clone do Forge, porque `merge_integracao` não distingue o Forge. A R-CONTRIB diz que a sessão de projeto abre PR no Forge e nunca mescla. Sugestão: limitar o merge do `jarvis` a repositórios que não sejam clone do Forge (`parecer.e_clone_do_forge`), com fixture, ou registrar a exceção na R-CONTRIB. Como o ajuste mexe na matriz da ADR 0009, o `software-architect` deve confirmar.
- **Baixa:** o `>` em `ESCRITA_NO_TEXTO` casa comparações dentro de `python -c`/`node -e` que citam um caminho protegido; só falso positivo.

## Parecer da revalidação
**Reprovado só por B4**, que é mecânico e depende de o usuário limpar a identidade do `.git/config`; B1 a B3 estão corrigidos e sem crítico ou alto em aberto no código. N1 entra nesta branch ou vira cartão antes da `homolog`. Fecha com a reescrita da autoria, sem nova rodada de código, se N1 for resolvido.

## Revalidação (c175f6b)
Reaplicação do commit sobre a `develop` (`melhoria/hook-conformidade-v2`). O código de `hooks/`, `bin/`, `tests/hooks/`, `docs/regras/` e `agents/` é idêntico ao revisado em `226cfba`: `git diff 12fc258 c175f6b` nesses caminhos vem vazio, e o `226cfba` (que resolve N1) é o mesmo código. Testes: `python3 -m unittest discover -s tests` verde (164 testes); `tests/catraca.py --base origin/develop` sem reprovação.

| # | Achado | Situação |
|---|---|---|
| B4 | Autoria `t <t@t>` dos commits | **Resolvido pelo processo.** Decisão do Jarvis: o merge é por squash e grava na `develop` o commit com o autor do PR, como no #10. Os commits locais com autor `t` não chegam à `develop`, então o ajuste de autoria do `.git/config` deixa de ser pré-requisito de envio. |
| N1 | Merge do `jarvis` valia também num clone do Forge | **Resolvido em `226cfba`.** A R-CONTRIB distingue a sessão que mantém o Forge (clone do próprio Forge, `tech-lead` ou Jarvis) de uma sessão de projeto, que nunca mescla, mesmo com o mesmo login. |

Demais achados da rodada anterior seguem como na tabela acima (B1 a B3, R1 a R4 corrigidos; R5, R8, R9 e R6 registrados).

## Parecer da revalidação
**Aprovado.** Nenhum achado bloqueante em aberto; B4 resolvido pelo processo de merge e N1 resolvido em `226cfba`.
