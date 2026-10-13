---
tipo: review
contrato: 1
pedido: contrib-sessao-forjavel
branch: melhoria/contrib-sessao-forjavel
commit: 850d7c3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Review independente: sessão forjável, falha fechada pela raiz e o Forge em qualquer pasta (`R-CONTRIB`, PR #89)

Escopo: `origin/develop...850d7c3`, com `hooks/_comum.py` (`e_projeto`, `tem_manifesto_do_forge`, `e_clone_do_forge`, `raiz_declarada`, `sessao_vigiada`, `falhar_fechado`), `hooks/conformidade.py` (`identificar_sessao`, `repositorio_do_forge`, `urls_dos_remotos`, `alvo_do_forge`, `regras_do_forge`, manifesto no projeto, `aninhado`, `ilegivel`, `env -S`), `hooks/parecer.py`, `tests/test_hooks.py` (`repos`), 28 fixtures novas ou ajustadas, `docs/regras/R-CONTRIB.md` e `CHANGELOG.md` (`## [Não publicado]`). Responde à review reprovada do #84 (`docs/reviews/contrib-identidade-sessao.md`).

## Como foi verificado
- `python3 -m unittest discover -s tests` numa worktree destacada em `850d7c3`: **281 testes, OK** (220 s).
- Sonda com os hooks reais (`conformidade.py` e `parecer.py` lendo o JSON do stdin), com `HOME` temporário, `GIT_CONFIG_GLOBAL=/dev/null` e `CLAUDE_PROJECT_DIR` no processo do hook. Repositórios montados:
  - `proj`: projeto, origin `acme/proj`;
  - `projf`: projeto com `.claude-plugin/plugin.json` `forge` forjado;
  - `proj2`: projeto com um remoto `forge` extra, apontando para o Forge;
  - `site`: projeto cujo origin é `<dono>/Forge-site`;
  - `~/Forge`: manifesto, origin no Forge, sem `.forge/versao`;
  - `~/.forge-contrib/proj` (`melhoria/proj-tema`) e a worktree `~/.forge-contrib/wt/x` (`melhoria/outra`);
  - `outro`: repositório sem projeto.

  Foram cerca de 110 entradas. As que divergem foram repetidas na `develop` (`6c5d07e`) para separar o que é regressão do que já existia.

## Bloqueantes da review do #84: todos resolvidos
| Desvio | #84 | PR #89 |
|---|---|---|
| 1. `cd <300×a>; git push origin HEAD` com raiz no projeto, cwd em `wt/x` ou `~` | passava | barrado (falha fechada `R-CONFORMIDADE`). Com raiz no Forge, em `wt/x`, libera, como deve |
| 2. Manifesto forjado (`projf`): `gh pr merge 70 -R <forge>`, push alheio no clone, `git -C projf push origin main` de `~` | passavam | barrados (`R-CONTRIB`, `R-CONTRIB` e `R-MAIN`). Write ou `echo >` em `.claude-plugin/plugin.json` no projeto: barrado. Apagar ou escrever `.forge/versao`: barrado |
| 3. `~/Forge` com raiz no projeto: `git -C ~/Forge push origin melhoria/outra`, `cd ~/Forge && gh pr merge 70`, `gh pr edit 70 --remove-label` (cwd `~/Forge`), `pushd ~/Forge && gh pr close 70`, `gh api -X PUT 'repos/{owner}/{repo}/pulls/70/merge'` | passavam | barrados. A mesma pasta com a raiz no Forge libera |

## Aninhados (antes, recomendados): resolvidos
Todos estes são barrados:
- `GH_REPO=<forge> bash -c`, `env GH_REPO=<forge> sh -c`, `GH_REPO=<forge> eval`;
- `env -S`, `-iS`, `-S"..."`, `--split-string=`, `-u X -S` e `GH_REPO=<forge> env -S`;
- `bash -lc`, `bash -o pipefail -c`, `bash --norc -c 'git push origin main'` (`R-MAIN`);
- `bash -c 'env -S "..."'`;
- `bash -c` aninhado além da profundidade, que falha fechado ao citar o Forge.

Também seguem barrados:
- `--repo=`, `xargs`, `command`, `exec`, `nohup`, `time`, `\gh`, `/usr/bin/gh`;
- `-R github.com/<forge>`;
- `gh api -X PUT repos/<forge>/pulls/70/merge`;
- o push por URL;
- o push alheio em `wt/x`, tanto por cwd quanto por `cd`.

## Falsos positivos
- **Sessão do Forge** (raiz em `~/Forge`), nada barrado:
  - no `~/Forge`: push, `gh pr merge --squash`, `gh pr edit --add-label`, `bash -c`, `env -S` e Write em `hooks/`;
  - em `wt/x`: push alheio, merge, `--remove-label` e Write;
  - de `~/Forge`: `git -C wt/x push`.
- **Projeto no próprio repositório:**
  - liberam o push da própria branch (com e sem `-u` e sem argumentos), `bash -c`/`env -S` com push próprio, Write em `src/`, Write e push de `melhoria/proj-tema` no próprio clone, `gh pr create -R <forge>` e `gh pr comment -R <forge>`;
  - `gh pr merge 3`/`create` só param no `parecer` (`R-REVIEW`, PR por número), o que é o fluxo normal.
- **Projeto com remoto do Forge (`proj2`), conservador mas tolerável:**
  - liberam `git push origin feature/x`, `push -u origin`, `git push forge HEAD:melhoria/proj2-tema`, `fetch forge` + `merge forge/develop` e `gh pr merge 3 -R acme/proj2` (na conformidade);
  - são barrados `git push` sem argumentos, `gh pr merge 3` e `gh pr edit 3` sem `-R`, porque sem remoto basta qualquer um apontar para o Forge. A saída é dar o nome do remoto ou o `-R`. Ver a recomendação 2.

## Recomendado (não bloqueia)
1. **Comparação por substring em `parecer.aponta_para_o_forge` (regressão de falso positivo).** `slug in texto` casa com `<dono>/Forge-site`, `<dono>/forge-mirror` etc. Antes, isso só afetava `-R` e as URLs. Agora o PR resolve o remoto do próprio repositório, então um projeto cujo slug **começa** com o do Forge tem o fluxo normal barrado:
   - `git push origin feature/y` → `R-CONTRIB`;
   - `gh pr merge 3`/`gh pr edit 3 --add-label` → `R-CONTRIB`.

   Na `develop`, o push passa. Hoje nenhum repositório do dono tem esse prefixo (`gh repo list`: só `Forge`), mas um fork do Forge com projeto de nome parecido cai nisso. Proposta: comparar o slug com fronteira, em vez de substring. Por exemplo, `re.search(rf"(^|[\s/:'\"=]){re.escape(slug)}(\.git)?($|[\s/#?'\"])", texto.lower())`, que cobre `-R <slug>`, URL https/ssh, `repos/<slug>/...` e o texto inteiro do `ilegivel`. Ou extrair `dono/repo` de cada forma e comparar com `==`. Fixtures: projeto com origin `<dono>/Forge-site` (push próprio e `gh pr merge 3` liberam na conformidade); `-R <dono>/Forge-site` libera; `-R <dono>/Forge` e `.../Forge.git` seguem barrados. Prefiro que entre neste PR, porque a regressão nasce aqui. Senão, abrir cartão antes da promoção.
2. **Remoto implícito em `proj2`.** Sem remoto, o hook considera qualquer remoto. Ele poderia imitar quem decide de fato:
   - para o `git push`: `branch.<b>.pushRemote`, `remote.pushDefault`, `branch.<b>.remote`, `origin`;
   - para o `gh`: o remoto com `gh-resolved`, senão `upstream`, `github`, `origin` e o primeiro.

   É refinamento de conforto, e o conservadorismo atual não abre brecha.
3. **`env -C <pasta>` / `--chdir`** não muda a pasta analisada: `env -C ~/Forge gh pr merge 70` e `env -C ~/Forge git push origin melhoria/outra` passam. **Já passavam na `develop`.** É dano real, mas o idioma é incomum, da mesma família do `cd`. Tratar `-C`/`--chdir` do `env` como `cd` em `separar_lancadores`. Cartão, se não entrar aqui.
4. **Remoto criado na mesma linha:** `git remote add f <URL do Forge> && git push f HEAD:melhoria/outra` passa, porque o remoto ainda não existe quando o hook roda. Em duas chamadas, é barrado. Também passam:
   - `git -c remote.x.url=<URL> push x ...`;
   - `git -c url.<URL>.insteadOf=zz: push zz:a ...`;
   - `git push --repo=<URL> ...`.

   São de baixa probabilidade. Sugestão: o remoto que não existe no repositório (ou um `-c remote.*`/`url.*` na linha) e cujo texto da linha cita o Forge falha fechado.
5. **`gh alias set m 'pr merge'` + `gh m 70 -R <forge>`** e `sh -c "$(printf '... -R <forge>')"` passam. É ofuscação, coberta pelo sandbox, conforme o limite já escrito em `R-CONTRIB`. Opcional: o subcomando desconhecido do `gh` com `-R <forge>` falha fechado.
6. **`R-MAIN` no próprio projeto, já existente:** `git push --all origin`, `git push --mirror origin` (que também força e apaga refs, ou seja, `R-VERIFY`) e `git push origin 'refs/heads/*:refs/heads/*'` passam, também na `develop`. Barrar `--mirror` sempre, e `--all` ou refspec com `*` quando houver `main`/`master`/integração local. Cartão.
7. **Write de sessão de projeto em cópia do Forge que não é a dela** (`~/Forge/hooks/...`, `~/.forge-contrib/wt/x/...`) passa, também na `develop`. O push é barrado, mas a mudança fica na árvore alheia. Hoje quem segura é o sandbox (escrita só no projeto e em `~/.forge-contrib`) e a permissão de Write fora da raiz. Sugestão: com `repositorio_do_forge(caminho)` fora do próprio clone, barrar o Write da sessão de projeto.
8. **Miúdos:**
   - `hooks/_comum.py`, docstring de `falhar_fechado`: "marcador crítico e o a sessão é vigiada" (sobra o "o").
   - `Guarda.raiz_e_projeto` repete metade de `e_projeto`; dá para reaproveitar.

## Pontos conferidos sem achado
- **`sessao_vigiada`** só depende de `raiz_declarada`/`e_projeto`/`raiz_do_projeto`/`em_contrib`, dentro de `try` que vigia na dúvida. O caso do bloqueante 1 agora cai nela, e não na pasta.
- **Ordem projeto → Forge** em `identificar_sessao` e em `e_clone_do_forge`. O Forge não versiona `.forge/`, então a sessão do Forge não muda. `.forge/versao` é protegido (Write e `rm`/`echo >`), o que impede despir o projeto para depois forjar o manifesto.
- **`parecer.merge_de_pr`** usa o `e_clone_do_forge` comum, e projeto nunca passa por Forge.
- **Neutralidade:** o slug vem do `plugin.json`. As fixtures repetem o slug já usado na `develop`. O teste de neutralidade passa.
- **`CHANGELOG.md`:** linha nova em `## [Não publicado]`, sem subir a versão (ADR 0006).

## Parecer
**Aprovado.** Os três bloqueantes da review do #84 e os dois recomendados de aninhamento estão fechados, com fixture para cada um, e os testes passam. A sonda não achou vetor novo de dano com probabilidade realista. O que passa é ofuscação, idioma incomum ou já existia na `develop` (recomendações 3 a 7), e fica para cartões. A recomendação 1 é regressão de falso positivo, de correção pequena, e deve entrar neste PR ou virar cartão antes da promoção para a `homolog`. Continua obrigatório o rótulo `afrouxa-regra` do dono, porque o PR toca `hooks/conformidade.py` e `docs/regras/`.
