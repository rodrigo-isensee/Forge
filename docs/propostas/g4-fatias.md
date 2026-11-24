# G4: fatias para trocar a lista de comandos proibidos pela trava real

Pedido v0481, etapa E7.1 (ordem do dono de 24/11 19:54: G4 fechando os remendos da `R-CONFORMIDADE` que cobre; o que afrouxa vai ao dono). Parte do desenho já na develop, `docs/propostas/g4-trava-real-bp8.md` (citado aqui como "desenho", com as ameaças T1 a T13 e os passos 1 a 12 dele), e do que o dono aplicou em 24/11. Só proposta: nenhum hook, teste, workflow nem configuração do GitHub foi mudado. Público: o dono e o time. Revisão: 2026-12-24.

Medida que o item move: **recusa falsa** (seção 2).

## 1. Estado real em 24/11 ~20:00 (só leitura: `gh api`, `git`, `test -w`)

| Camada | Estado lido | Cobre |
|---|---|---|
| Ruleset 26701749 `checks-obrigatorios-develop-main` | ativo; `develop` e `main`; só `required_status_checks` (`bateria`, `bateria (python 3.14)`, `catraca`, fonte Actions 15368); `bypass_actors: []`; `current_user_can_bypass: never` | merge e push sem os três checks, para todos, inclusive o token dos agentes (T2) |
| Ruleset 25432260 `merge-commit-homolog-main` | ativo; `homolog` e `main`; `pull_request` (só merge commit), checks (`bateria` e `catraca` **sem fonte fixa**), `non_fast_forward`, `deletion`; `bypass_actors: []` | push direto, force push e deleção em `homolog` e `main` (T1 nessas duas) |
| Ruleset 27992073 `tags-v-imutaveis` | ativo; `refs/tags/v*`; `update` e `deletion`; `bypass_actors: []` | mover e apagar tag `v*`; a **criação segue aberta** (o GitHub recusou o Actions como exceção, 422, cartão RULESET-TAGS-CRIACAO) |
| Ruleset 24947028 `mainRuleset` | `disabled`, sem alvo | nada |
| Token dos agentes | ainda o do dono: `gh api user` dá a conta do dono; `permissions.admin: true`; escopos clássicos com `repo`, `workflow`, `delete_repo`, `admin:org`, `admin:repo_hook` | nada; é a lacuna principal (T3, T5, T6, T7, T12) |
| Secret scanning e push protection | `disabled` | nada (T8) |
| `.github/CODEOWNERS` | não existe | nada (T6) |
| Sandbox, `test -w` na sessão do Forge (sonda S1) | não graváveis: `.git/config`, `.git/hooks`, `.forge/`, `.git/forge/run`, `.claude/settings.json`, `~/.claude/settings.json`, `~/.claude/plugins`, `~/.forge/maquina`; graváveis: o resto de `.git/` (inclusive `.git/forge` fora de `run`), `.claude/` fora dos settings, `hooks/`, `.githooks/`, `.devcontainer/`, a pasta de controle (`~/.forge-contrib/KANBAN.md`, `docs/pedidos/`) e, **nos clones em `~/.forge-contrib/wt/`, `.git/config` e `.git/hooks`** | T9 e T10 em parte |
| Rede | `strictAllowlist` não ligado; só `deniedDomains` das APIs de modelo | T10 (API paga) |
| Hook `conformidade` no 8d7914bc | 112 chamadas `barrar(` com o ID da regra literal (64 `R-CONFORMIDADE`, 19 `R-REVIEW`, 11 `R-CONTRIB`, 9 `R-VERIFY`, 6 `R-MAIN`, 3 `R-FLUXO`), o critério do desenho (111 em 21/11, +1). O `grep -c 'barrar('` dá 138: soma as 2 definições e 24 chamadas com o ID vindo de tupla ou variável (`*PROVA_DA_SUITE`, `*publico`, `*apagar`, `rid`, `guarda` e outras) | é onde nascem as recusas falsas |

O que isso muda em relação ao desenho:
1. Sem bypass, **merge sem os checks virou impossível** para os agentes (T2), salvo a parte dos pareceres, que segue no hook `parecer` até o G2.
2. **T1 fechada em `homolog` e `main`**; na `develop` seguem abertos o force push, a deleção e o push direto de um commit que já tem os checks verdes (cabeça de PR sem os pareceres).
3. **T4 pela metade:** mover e apagar `v*` impossível; criar, possível.
4. **Enquanto o token for o do dono, toda camada do servidor é desfazível por um agente** (um `PUT` no ruleset devolve o bypass). Por isso o grupo "gh api que altera refs, regras ou acessos" (`hooks/conformidade.py:3779`) segura todas as outras: nenhuma fatia antes do D3 afrouxa a leitura de `gh api` que escreve.
5. **Achado novo (recomendado):** na `homolog`, `bateria` e `catraca` vêm só do 25432260, sem fonte fixa; um status de commit com o mesmo nome, gravado com o token do ambiente, satisfaz o check ali. A `main` não sofre (o 26701749 fixa o Actions). O passo D1 fecha (a `homolog` entra no 26701749).
6. **No clone do agente, `.git/config` e `.git/hooks` são graváveis**: o `pre-push` nunca é trava real fora da pasta de trabalho principal; a trava é o servidor. Isso pesa nas fatias F7 e F10.

## 2. Medida que move: recusa falsa

Linha de base: `.forge/run/comandos.jsonl.1` seguido de `.forge/run/comandos.jsonl` da pasta do Forge, só as linhas com `hora` até `2026-11-24T20:00:00` (a primeira é de 10:29:14): **2518 linhas, sha256 das linhas na ordem `1e864a97b3ad0f3c6c6f8bdf1d1217509a104585d6e81d5bdf81a07bfdfd916a`**. Chamadas distintas por (hora, sessão, agente, forma): **788 chamadas, 99 recusadas (12,6%)**: `git commit` 39, `git push` 21, `gh pr checks` 9, `gh pr view` 6, `git config` 5, `gh pr create` 4, `gh api` 4, `git merge` 4, `gh pr list` 3, `gh pr edit` 2, `git worktree` 1, `git reset` 1. A contagem da primeira versão (908 e 126) não se refazia e sai. O `.1` é sobrescrito na próxima rotação: se o sha256 não bater, a linha de base é a desta seção, e a medida nova sai do registro da F1.

- As 18 de `gh pr checks`, `gh pr view` e `gh pr list` são leitura pura: toda é recusa falsa. Alvo da F2: **0**.
- As 39 de `git commit` são, pelos relatos (heredoc, `$?`, crase), texto de mensagem lido como comando. Alvo da F3: só as que tentam gravar caminho de controle.
- Hoje nada no registro separa recusa falsa de recusa com efeito: `barrado` guarda só o ID da regra, e o registro não guarda a linha. A F1 grava os campos `grupo` e `alvo`; a partir dela, **recusa falsa** é a linha com `barrado` ou `teria_barrado` e `alvo` nulo, e recusa com efeito é a que tem `alvo`.

Como medir (só leitura, na pasta do Forge):
```
python3 -I -c 'import json,hashlib,collections as C;h=hashlib.sha256();u={};L=[l for f in (".forge/run/comandos.jsonl.1",".forge/run/comandos.jsonl") for l in open(f,"rb") if json.loads(l)["hora"]<="2026-11-24T20:00:00"];[h.update(l) for l in L];[u.setdefault((d["hora"],d.get("sessao"),d.get("agente"),d.get("forma")),d.get("barrado")) for d in map(json.loads,L)];b=[k[3] for k,v in u.items() if v];print(len(L),h.hexdigest(),len(u),len(b),C.Counter(b).most_common())'
```

## 3. Fatias

Cada fatia é um PR para a `develop` com até 150 linhas mudadas (teto por PR). "Afrouxa" é `R-CONFORMIDADE`, `R-MAIN`, `R-VERIFY` ou `R-FLUXO` e pede o rótulo `afrouxa-regra` do dono (D9) e o texto da regra mudado no mesmo PR (`verificada_por` passa a citar o ruleset ou o sandbox). Toda fatia que passa um grupo a aviso fica uma semana em aviso, com o vigia contando, antes de qualquer remoção de código (desenho, seção b).

### Parte A: já coberto pelo que está em vigor (sem passo novo do dono)

**F0. Fechar cartões sem código.** Arquivos: só o quadro (agile-coach, com a prova). Aperta: nada. Afrouxa: nada.
| Cartão | Prova para fechar |
|---|---|
| DESENHO-G4-NUMEROS | já corrigido no #819 (0ed441e9); passos 9b, 10 e 11 e a soma 111 conferem no desenho |
| AV1-BYPASS-RULESET, parte (a) | `bypass_actors: []` em 26701749 e 25432260 (gh api, 24/11); a parte (b) segue aberta |
| AE8-RULESET-DEVELOP-SEM-EXCECAO | o sub-item que restava (develop sem exceção, inclusive para o dono) está em vigor; fecha quando a auditoria do cartão der zero por 3 dias |
| RULESET-TAGS-V | aplicado como 27992073 (mover e apagar); a criação segue no RULESET-TAGS-CRIACAO |
| CONFORMIDADE-S22-FLUXO | o efeito (o `git push` que chega à `main`) é recusado pelo servidor (25432260: `pull_request` e `non_fast_forward`, sem bypass); fecha pelo critério da seção (d) do desenho |
| CONFORMIDADE-TIL-EM-SUBSTITUICAO | o alvo (`~/.claude/settings.json`) não é gravável pelo Bash (sonda S1); no projeto, `~` nem está no `allowWrite` |

**F1. Modo aviso por grupo (infra).** Depende: nada. Arquivos: `hooks/conformidade.json` (~15: mapa grupo → `barrar` ou `avisar`, todos em `barrar`), `hooks/conformidade.py` (~40: o `barrar` consulta o grupo; em `avisar`, imprime a forma certa, grava `teria_barrado` no `comandos.jsonl` e deixa passar; nos dois modos grava `grupo` e `alvo`: o caminho de controle, a ref protegida ou o destino opaco que disparou o `barrar`, ou nulo quando o disparo veio só do texto da linha, como a mensagem de commit), `tests/test_hooks.py` (~50: grupo em aviso passa e registra; grupo fora do mapa, mapa ilegível ou valor desconhecido barra), `docs/hooks.md` (~8). Total ~115. Aperta: a medida da seção 2 passa a ter o "teria barrado". Afrouxa: nada (todo grupo nasce `barrar`, falha fechada), sem rótulo. Cartões: nenhum; é pré-requisito de F4 a F8 e F10.

**F2. Leitura pura fora da maquinaria.** Depende: nada (leitura não muda estado). Regra: a linha cujos comandos todos passam pela gramática de leitura que o papel só de leitura já usa (`forma_de_leitura_git` e as recusas de `hooks/conformidade.py:2589` a `2655`, que já barram `--output`, `--ext-diff`, gpg, `--web` e transporte `::`) é decidida só por ela, para qualquer papel. Aceita `$?`, `$TMPDIR`, `$HOME` e variável atribuída por literal na mesma linha cujo valor não começa com `-`; `$(…)` só se o de dentro também passar pela gramática; redireção só para `/dev/null` ou `"$TMPDIR/<nome literal>"`, sem atribuir `TMPDIR` na linha; `gh api` só sem `-X`/`--method` diferente de `GET` e sem `-f`, `-F`, `--field`, `--raw-field`, `--input`. Arquivos: `hooks/conformidade.py` (~50), `tests/test_hooks.py` (~70: corpus de legítimos com as formas das 18 recusas e casos de abuso `git log --output=$f`, `gh api -f x=1 …`, `TMPDIR=. ; git diff > "$TMPDIR/x"`, `f=--output=x; git log $f`), `docs/hooks.md` (~6), `docs/regras/R-CONFORMIDADE.md` (~2). Total ~130. Aperta: nada. Afrouxa: `R-CONFORMIDADE` em linha só de leitura com variável, crase ou `cd -P` (rótulo, D9). Cartões que fecha: HOOK-LEITURA-COM-VARIAVEL, CONFORMIDADE-CD-OPCAO-P e a parte de leitura do HOOK-FALSO-POSITIVO-TEXTO. Medida: leitura recusada de 18 para 0.

**F3. Texto que não roda.** Depende: nada. Regra: o corpo de heredoc com delimitador entre aspas (`<<'FIM'`) e o arquivo dado a `git commit -F`, `gh pr create|edit|comment --body-file` são dado: crase, `$?`, `$var`, `>`, `#` e palavras soltas dentro deles não são lidos como comando. O destino da redireção do heredoc segue analisado como hoje; heredoc sem aspas segue como hoje (o bash expande `$(…)` nele). Arquivos: `hooks/conformidade.py` (~35), `tests/test_hooks.py` (~60: mensagem com crase, `$?`, `rm -rf` e `> .claude/x` no texto passa; `cat > hooks/x <<'FIM'` segue pela regra do destino; `<<FIM` com `$(…)` segue recusado), `docs/hooks.md` (~5). Total ~100. Aperta: nada. Afrouxa: `R-CONFORMIDADE` sobre texto de heredoc entre aspas (rótulo, D9). Cartões que fecha: o resto do HOOK-FALSO-POSITIVO-TEXTO (com a F2). Medida: as 39 recusas de `git commit`.

**F4. Tag: mover e apagar viram aviso.** Depende: F1 e o 27992073 (em vigor). Grupo: as formas de `R-FLUXO` (`hooks/conformidade.py:3085`, `3100`) que movem ou apagam (`git tag -f|-d`, `git push --delete` de tag, `git push origin :refs/tags/v…`, `+refs/tags/…`); **a criação segue barrada** (criação aberta no servidor). Arquivos: `hooks/conformidade.json` (~3), `hooks/conformidade.py` (~15), `tests/test_hooks.py` (~25), `docs/regras/R-FLUXO.md` (~2). Total ~45. Aperta: nada. Afrouxa: `R-FLUXO` em mover e apagar tag (rótulo, D9). Cartões: completa o RULESET-TAGS-V (F0).

**F5. `homolog` e `main`: push direto, force, apagar e reescrever viram aviso.** Depende: F1 e o 25432260 (em vigor). Grupo: `hooks/conformidade.py:2970`, `2991`, `2995`, `3138`, `3140` e o `--force` de `3115`, só quando o destino literal é `homolog` ou `main`; destino opaco ou `develop` segue barrado. O `--mirror` (`3117`) **não entra**: não tem destino literal e envia todas as refs (ver F6). O merge na `main` por agente (T3, `2734`, `3768`) **não entra**: com o token do dono, a `main` aceita o merge de PR verde. Arquivos: `hooks/conformidade.py` (~20), `hooks/conformidade.json` (~4), `tests/test_hooks.py` (~40), `docs/regras/R-LIMITES.md` (~3). Total ~70. Aperta: nada. Afrouxa: `R-MAIN` (push na `main`) e `R-VERIFY` nas duas branches (rótulo, D9). Cartões: CONFORMIDADE-S22-FLUXO (F0).

### Parte B: depois de um passo do dono (seção 4)

**F6. `develop`: force, apagar, reescrever e push direto viram aviso; `--force` em qualquer branch também.** Depende: F1 e D1 conferido. Grupo: os mesmos pontos da F5 para a `develop`, e `3115` para qualquer branch (nas `melhoria/*`, o parecer é preso ao sha revisado; reescrever só o invalida). A tag no envio segue barrada pelo `R-FLUXO` (`3100`), com ou sem `--force`. **O `--mirror` (`3117`) segue barrado**: envia `refs/tags/*` e cria tag `v*`, que o servidor não barra enquanto o D2 está aberto (sonda S1 do review: a `v9.9.9` chegou ao remoto), e apaga do remoto toda branch que a cópia não tem, inclusive `melhoria/*` de outro papel, que nenhum ruleset protege; vai para a seção 5. Testes: `git push --mirror <remoto>`, `git push -f origin v9.9.9` e `git push --force --tags` seguem recusados. Arquivos: `hooks/conformidade.py` (~15), `hooks/conformidade.json` (~3), `tests/test_hooks.py` (~35), `docs/regras/R-LIMITES.md` (~2). Total ~55. Afrouxa: `R-VERIFY` (`--force` em branch) e `R-CONFORMIDADE` (push direto na `develop`) (rótulo, D9); nenhuma forma que cria tag. Cartões que fecha: RULESET-DEVELOP-APAGAR-REESCREVER (pelo D1 conferido).

**F7. `--no-verify` e `core.hooksPath` viram aviso.** Depende: F1, D1 e D5. Grupo: `2411`, `2709`, `2712`. O que o `pre-push` barra (branch protegida, segredo) passa a ter camada no servidor; e no clone do agente ele já é contornável (seção 1, item 6). Arquivos: `hooks/conformidade.py` (~10), `hooks/conformidade.json` (~3), `tests/test_hooks.py` (~25), `docs/regras/R-LIMITES.md` (~2). Total ~40. Afrouxa: `R-VERIFY` (rótulo, D9); a regra segue como conduta. Cartões: CONFORMIDADE-COPIA-RECURSIVA-GIT só em parte. Fecha a troca do `.git/config` e do `core.hooksPath` (na pasta do Forge o sandbox já não deixa gravar `.git/config` nem `.git/hooks`; no clone, o `pre-push` deixa de ser camada). **Fica aberta** a outra parte: `cp -r tp/. .` na pasta do Forge grava `.git/forge/` fora de `run` (gravável, seção 1), onde fica a marca de sessão (T9), e o hook não vê os nomes. Fecha só com `.git/forge` inteiro no `denyWrite` do sandbox da sessão do Forge (passo do dono, depois de conferir que nada grava ali pelo Bash) ou como lacuna aceita pelo dono, como a D10.

**F8. Merge, PR, rótulo e `gh api` que escreve viram aviso.** Depende: F1, D3 e D4 conferidos. Grupo: `R-MAIN` merge na `main` (`2734`, `3768`), programa por expansão com `pr merge` ou `api` (`2446`), merge pela API (`3695`), `gh api` que altera refs, regras ou acessos (`3779`), rótulo `afrouxa-regra` (`3412`; a catraca só aceita o da conta do dono, que deixa de ser a dos agentes), `gh pr create` e `gh pr merge` por papel (`3383`, `3391`, `3394`, `3759`, `3771`). **Fica barrado:** `gh pr merge --admin` (`3684`; forma literal, sem recusa falsa, e ordem do dono de 24/11). Arquivos: `hooks/conformidade.py` (~25), `hooks/conformidade.json` (~10), `tests/test_hooks.py` (~60), `docs/regras/R-LIMITES.md` e `R-CONFORMIDADE.md` (~5). Total ~100. Afrouxa: `R-MAIN`, `R-CONTRIB` (rótulo) e `R-CONFORMIDADE` por papel (rótulo, D9). Cartões: nenhum à parte; move as recusas de `gh api`, `gh pr create` e `gh pr edit` da seção 2.

**F9. `CODEOWNERS` dos caminhos de controle.** Depende: D3 (antes dele o dono e os agentes são a mesma conta e a aprovação não separa nada). Arquivo: `.github/CODEOWNERS` (~15), com a lista inteira do passo 10 do desenho: `.github/`, `.githooks/`, `.claude/`, `.claude-plugin/`, `.devcontainer/`, `hooks/`, `tests/catraca.py`, `tests/config.json`, `tests/neutralidade.py`, `tests/hooks/`, `docs/regras/`, `docs/adr/` e o próprio `.github/CODEOWNERS`. Aperta: o merge de arquivo de controle passa a exigir a aprovação do dono (depois do D7). Afrouxa: nada.

**F10. A maquinaria da lista negra sai.** Depende: F1, D3, D7 conferidos e o G2 (parecer como status do commit); a parte da pasta de controle depende da D10. Em duas etapas:
- F10a (~60 linhas: `hooks/conformidade.json`, testes): os grupos abaixo vão a aviso por uma semana.
- F10b (remoção, em 4 a 6 PRs de até 150 linhas, um por família): opacos e teto de destinos (`1835` a `1880`), linha longa e excesso (`2128`, `2150`), heredoc com programa não modelado, aspas sem par e `#` (`2200` a `2264`), lançadores e reavaliação (`2244` a `2256`, `2331`, `2374` a `2406`), pathspec pela entrada (`2789` a `2876`), caminho trocado na linha (`4147`), e o `R-REVIEW` local (`2413`, `2417`, `2690`, `2696`, `2755` a `2776`, `2893`, `2901`, `3064`, `3677`, `3729` a `3739`).
- **Fica barrado:** escrita pelo Write/Edit por `file_path`; ler `.env` (`2551`); papel só de leitura (lista branca, ADR 0011); linhas `brief selado`/`entrega conferida` (`2093`, `2107`); destino **literal** de escrita em `.devcontainer/`, `.vscode/tasks.json`, `.vscode/settings.json`, `.git/forge/` e na pasta de controle; `--admin`.
Afrouxa: `R-CONFORMIDADE` e `R-REVIEW` (rótulo em cada PR, D9). Cartões que fecha: CONFORMIDADE-RESTO-SOBE, CONFORMIDADE-A20-RESTO-BARRA-OPACO, CONFORMIDADE-DESTINO-FIXTURES, HOOK-HEREDOC-EXTGLOB-E-CAIXA (o hook `parecer`, com o G2) e a parte `.forge/` do CONFORMIDADE-CURINGA-PASTA (sandbox na sessão do Forge). Só com a D10: CONFORMIDADE-LINK-POR-COPIA, CONFORMIDADE-PASTA-MAE-REMOCAO e a parte `docs/brief?/` do CONFORMIDADE-CURINGA-PASTA (o alvo é a pasta de controle, que nenhuma camada real cobre; o que sobra é a detecção pelo sha256 do brief e pelo git da pasta).

Ordem: F0, F1, F2, F3, F4, F5 (já); D1 → F6; D5 → F7; D3 → D4 → F8; F9 → D7; G2 → F10a → uma semana → F10b.

## 4. O que só o dono faz, com o comando

No terminal do dono, fora do Claude, dentro do clone do Forge (`R` é o repositório). Nenhum agente roda estes comandos. Depois de cada um, a conferência é só leitura e o time pode rodá-la.
```
R=$(gh repo view --json nameWithOwner -q .nameWithOwner)
```

**D1. `develop` sem force push e sem deleção; `homolog` com checks de fonte fixa; PR obrigatório na `develop`.** Destrava F6 e F7; fecha o achado novo da seção 1, item 5.
```
gh api -X PUT "repos/$R/rulesets/26701749" --input - <<'FIM'
{"name":"checks-obrigatorios-develop-main","target":"branch","enforcement":"active","bypass_actors":[],
 "conditions":{"ref_name":{"include":["refs/heads/develop","refs/heads/homolog","refs/heads/main"],"exclude":[]}},
 "rules":[{"type":"required_status_checks","parameters":{"do_not_enforce_on_create":false,"strict_required_status_checks_policy":false,
   "required_status_checks":[{"context":"bateria","integration_id":15368},{"context":"bateria (python 3.14)","integration_id":15368},{"context":"catraca","integration_id":15368}]}},
  {"type":"non_fast_forward"},{"type":"deletion"}]}
FIM
gh api -X POST "repos/$R/rulesets" --input - <<'FIM'
{"name":"pr-develop","target":"branch","enforcement":"active","bypass_actors":[],
 "conditions":{"ref_name":{"include":["refs/heads/develop"],"exclude":[]}},
 "rules":[{"type":"pull_request","parameters":{"allowed_merge_methods":["squash","merge"],"dismiss_stale_reviews_on_push":false,
   "require_code_owner_review":false,"require_last_push_approval":false,"required_approving_review_count":0,"required_review_thread_resolution":false}}]}
FIM
```
Conferência: `gh api "repos/$R/rules/branches/develop" --jq '[.[].type]|sort'` → `["deletion","non_fast_forward","pull_request","required_status_checks"]`; `gh api "repos/$R/rulesets/26701749" --jq '{bypass_actors,inc:.conditions.ref_name.include}'` → bypass vazio e as três branches. Reversão: o mesmo `PUT` com o JSON lido antes (`gh api "repos/$R/rulesets/26701749" > antes-26701749.json`, guarde antes de aplicar) e `gh api -X DELETE "repos/$R/rulesets/<id do pr-develop>"`.

**D2. Criação de tag `v*`.** Sem comando agora: segue o cartão RULESET-TAGS-CRIACAO (devops; chave de implantação ou organização gratuita, sem custo). Enquanto isso, a criação de tag fica barrada no hook, inclusive pelo `git push --mirror`.

**D3. Conta e token dos agentes.** Passos 1 a 5 do desenho (conta de máquina com papel `write`, token fine-grained só do Forge sem Administration, Workflows nem Secrets, troca do `GH_TOKEN` e revogação do token antigo; as telas estão lá). Conferência, na sessão do Forge: `gh api user --jq .login` → a conta dos agentes; `gh api "repos/$R" --jq .permissions.admin` → `false`; `gh api "repos/$R/rulesets/26701749" --jq .current_user_can_bypass` → `never`. Destrava F8 e F9.

**D4. Só o dono mescla na `main`** (depois do D3; antes, o bypass de admin valeria para os agentes):
```
gh api -X POST "repos/$R/rulesets" --input - <<'FIM'
{"name":"main-do-dono","target":"branch","enforcement":"active",
 "bypass_actors":[{"actor_id":5,"actor_type":"RepositoryRole","bypass_mode":"pull_request"}],
 "conditions":{"ref_name":{"include":["refs/heads/main"],"exclude":[]}},
 "rules":[{"type":"update","parameters":{"update_allows_fetch_and_merge":false}}]}
FIM
```
Conferência: na sessão dos agentes, `gh api "repos/$R/rulesets/<id do main-do-dono>" --jq .current_user_can_bypass` → `never`.

**D5. Varredura de segredos e push protection** (gratuitas em repositório público):
```
gh api -X PATCH "repos/$R" --input - <<'FIM'
{"security_and_analysis":{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"}}}
FIM
```
Conferência: `gh api "repos/$R" --jq .security_and_analysis.secret_scanning_push_protection.status` → `enabled`.

**D6. Apagar o ruleset desligado** (só limpeza): `gh api -X DELETE "repos/$R/rulesets/24947028"`. Conferência: `gh api "repos/$R/rulesets" --jq '.[].name'` sem `mainRuleset`.

**D7. Exigir o dono nos caminhos de controle** (depois do merge da F9):
```
gh api "repos/$R/rulesets/<id do pr-develop>" --jq '.rules' > regras-pr-develop.json
gh api -X PUT "repos/$R/rulesets/<id do pr-develop>" --input - <<'FIM'
{"rules":[{"type":"pull_request","parameters":{"allowed_merge_methods":["squash","merge"],"dismiss_stale_reviews_on_push":false,
  "require_code_owner_review":true,"require_last_push_approval":false,"required_approving_review_count":0,"required_review_thread_resolution":false}}]}
FIM
```
Conferência: um PR de teste que toca `hooks/` fica com o merge bloqueado até a aprovação do dono.

**D8. Rede restrita** (fecha a T10 sem depender do hook): o comando do README, seção "Rede restrita de verdade", no `~/.claude/settings.json` do dono; reiniciar a sessão e conferir com `/sandbox`.

**D9. Rótulo nas fatias que afrouxam** (F2 a F8, F10a e cada PR da F10b), depois do último envio do PR: `gh pr edit <número> --add-label afrouxa-regra`.

**D10. Decisão: a pasta de controle sem trava real.** A pasta de controle (`~/.forge-contrib`: quadro, pedidos, briefs) é gravável pelo Bash de todo papel e não é versionada no GitHub. Opções: (a) manter barrado no hook só o destino literal dela (proposta desta lista; o opaco passa e é detectado pelo sha256 do brief e pelo git da pasta); (b) manter a maquinaria só para ela (as recusas falsas continuam em quem grava perto dela). Muda o que a F10 fecha.

## 5. O que fica no hook mesmo com tudo aplicado

Escrita por `file_path` no Write/Edit, ler `.env`, papel só de leitura, linhas de brief e entrega, destino literal em `.devcontainer/`, `.vscode/`, `.git/forge/` e na pasta de controle, criação de tag `v*` (até o D2), `git push --mirror` (cria tag e apaga branch de outro papel), `--admin`, e o `R-CONTRIB` de sessão de projeto contra o Forge até o passo 4 do desenho pôr o token só na sessão do Forge.
