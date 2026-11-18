---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: b989773a2ae7276692081441ff72c05d26d0f8da
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.17, revalidação)

Volta por delta, volta 2 de 3 do A5. Rodada anterior: `commit 56bb90b5`, no git (E3.13). Delta lido (`forge-check parecer delta`, `56bb90b5..b989773a`): no domínio, `hooks/parecer.py` (`CARREGA_ARQUIVO`, `NOMEIA`, `LE_COM_VALOR`, `nomes_dinamicos`, `mexidas_na_linha`, `remotos` por `git remote -v` e `gh-resolved`, a mensagem de `pasta_do_gh`), 15 fixtures `incidente-r-copia-alheia-*` e `pasta-barra-home-*`, `tests/test_hooks.py` e `tests/test_hooks_parecer_repo.py`. Fora do domínio, não relido: changelog, `docs/hooks-fixtures.md` e `tests/mutantes/*`.

Gatilhos: hook de controle (`hooks/parecer.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A5 (bloqueante) hooks/parecer.py:624 · Fechado em S10, S11 e vizinhas, segue aberto: `command -p . ./env.sh`, `command -- source`, `builtin -- source`, `c=source; $c env.sh` e `env $(cat vars) gh pr ready|merge` dão 0 na cópia alheia, e o PR do Forge sai do rascunho sem parecer (S14 a S18).
- A6 (recomendado) hooks/parecer.py:936 · Fechado com o config gravado antes (S12, S13 dão 2). Aberto pelo ambiente que troca o config que o git do gh lê: `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_COUNT`/`KEY`/`VALUE`, `GIT_CONFIG_PARAMETERS`, `HOME`, `XDG_CONFIG_HOME` na linha dão 0 (S19 a S22).
- A7 (bloqueante) hooks/parecer.py:936 · `remotos` lê os remotos antes de a linha rodar: `git remote add upstream <forge> && gh pr ready feature/x`, `git remote set-url origin <forge>;` ou `git config remote.origin.gh-resolved <forge>;` na mesma linha dão 0 na cópia alheia (S23 a S25).

## Sondas
- S10 · `source env.sh; gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S11 · `. ./env.sh && gh pr ready feature/x` · espera: 2 · obtido: 2 (fechado)
- S12 · `gh pr ready feature/x` com `remote.origin.gh-resolved dono/forge` gravado antes · espera: 2 · obtido: 2 (fechado)
- S13 · `gh pr ready feature/x` com `url.git@github.com:dono/forge.git.insteadOf git@github.com:outro/coisa.git` gravado antes · espera: 2 · obtido: 2 (fechado)
- S14 · `command -p . ./env.sh; gh pr ready feature/x` · espera: 2 · obtido: 0
- S15 · `command -- source ./env.sh; gh pr ready feature/x` · espera: 2 · obtido: 0
- S16 · `builtin -- source ./env.sh; gh pr ready feature/x` · espera: 2 · obtido: 0
- S17 · `c=source; $c env.sh; gh pr ready feature/x` · espera: 2 · obtido: 0
- S18 · `env $(cat vars) gh pr ready feature/x` e `env $(cat vars) gh pr merge feature/x` (vars = `GH_REPO=dono/forge`) · espera: 2 · obtido: 0
- S19 · `GIT_CONFIG_GLOBAL=g.cfg gh pr ready feature/x` (g.cfg com o `insteadOf` de S13); também `export GIT_CONFIG_GLOBAL=g.cfg;` · espera: 2 · obtido: 0
- S20 · `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.gh-resolved GIT_CONFIG_VALUE_0=dono/forge gh pr ready feature/x` · espera: 2 · obtido: 0
- S21 · `export GIT_CONFIG_PARAMETERS="'remote.origin.gh-resolved'='dono/forge'"; gh pr ready feature/x` · espera: 2 · obtido: 0
- S22 · `HOME=$PWD/h gh pr ready feature/x` (h/.gitconfig com o `insteadOf`) e `export XDG_CONFIG_HOME=$PWD/x;` (x/git/config) · espera: 2 · obtido: 0
- S23 · `git remote add upstream git@github.com:dono/forge.git && gh pr ready feature/x` · espera: 2 · obtido: 0
- S24 · `git remote set-url origin git@github.com:dono/forge.git; gh pr ready feature/x` · espera: 2 · obtido: 0
- S25 · `git config remote.origin.gh-resolved dono/forge; gh pr ready feature/x` (e o `insteadOf` pela mesma via) · espera: 2 · obtido: 0

Cenário de todas: cwd `{tmp}/alheio` (remoto `outro/coisa`, `env.sh` = `export GH_REPO=dono/forge`), sessão no clone `dono/forge` sem parecer, montado pela fixture `incidente-r-copia-alheia-source-gh-repo-ready-bloqueia.json`.

## Estado dos achados anteriores
- **A5:** fechado nas formas da rodada (S10, S11) e em vizinhas que dão 2: `\source`, `'.'`, `builtin .`, `time`, `!`, `if source`, `{ source; }`, `set -a; . ./vars`, `source /dev/fd/3`, `declare -x $(cat vars)`, `export $(...)`, `read "$n"`, `declare -n`, `local -n`, `readonly "$n"=`, função que exporta, `eval "$(cat env.sh)"` (recusa do eval), `BASH_ENV=`/`--rcfile` com `bash -c` (recusa do `bash -c`), `env -S`. Aberto por S14 a S18.
- **A6:** fechado nas formas S12 e S13. Aberto pelo ambiente de config (S19 a S22); segue recomendado pelo mesmo critério (forma pouco natural).
- **A1 a A4:** fechados antes; sem delta que os toque.
- Corpus de legítimos, todos 0: cópia alheia sem repositório indicado; `gh-resolved base`; `source env.sh; gh pr view feature/x`; `git -c remote.origin.gh-resolved=dono/forge status; gh pr ready feature/x` (o `-c` vale só para aquele git).

## Detalhe dos achados
**A5 (alta, bloqueante).** Evidência: `hooks/parecer.py:624-626` tira só a palavra `builtin` ou `command`, sem as opções (`-p`, `--`), e então `comando[0]` é `-p` ou `--`, não `source`. `nomes_dinamicos` (`hooks/parecer.py:603-612`) não cobre `env`, e o nome do comando por expansão (`$c`) não é lido. Provado no bash: as cinco formas exportam `GH_REPO=dono/forge`; o gh 2.105.0 usa o GH_REPO. Caminho de ataque, o do A5: depois da recusa, o agente grava `env.sh` numa pasta com `git init` e usa uma dessas formas para tirar o PR do Forge do rascunho ou mesclá-lo sem parecer. Correção mínima, por dimensão (não caso a caso): (1) depois de `builtin`/`command`, pular também as opções (`-p`, `-v`, `-V`, `--`) antes de olhar o comando; (2) palavra de comando que expande (`$c`, `${c}`, `$(...)`, crase) numa linha com gh pr conta como mexer em todos os `SENSIVEIS`; (3) `env` com argumento que expande antes do comando (`env $(...) gh`, `env "$x" gh`) é GH_REPO incerto, como o `export $(...)`. Fixtures: S14 a S18 com recusa. Esforço P. Dono: tech-lead.

**A6 (média, recomendado).** Evidência: `hooks/parecer.py:936-942` roda `git remote -v` e `git config` com o ambiente do hook, não com o que a linha dá ao gh. Provado sem rede: com `GIT_CONFIG_COUNT/KEY_0/VALUE_0` de `remote.origin.gh-resolved dono/forge`, `gh repo set-default --view` imprime `dono/forge`; com `GIT_CONFIG_PARAMETERS` de `insteadOf`, `git remote -v` mostra `dono/forge`. Correção mínima: na cópia alheia, mexidas na linha de qualquer destas variáveis tornam os remotos desconhecidos e o hook recusa: `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG`, `GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`, `HOME`, `XDG_CONFIG_HOME` (as duas últimas já estão em `SENSIVEIS`; basta usá-las aqui). Fixtures S19 a S22. Esforço P. Dono: tech-lead.

**A7 (alta, bloqueante).** Evidência: `hooks/parecer.py:936`, `remotos(copia)` lê o estado do git no momento do hook; um comando anterior da mesma linha muda os remotos antes de o gh rodar. É a mesma classe do GH-API-ARQUIVO-TROCADO (`hooks/parecer.py:1042`), que o hook já trata para o arquivo da consulta. critério mudou: na rodada anterior a mesma linha só aparecia com `gh-resolved`/`insteadOf` à mão (A6, pouco natural); `git remote add` e `git remote set-url` são a forma comum de apontar uma cópia para outro repositório, e numa linha só abrem o portão. Caminho de ataque: na cópia alheia recusada, o agente roda `git remote add upstream <forge> && gh pr ready <branch>`. Correção mínima: na cópia alheia, linha com gh pr que também roda `git remote` (add, set-url, rename, remove), `git config` (qualquer escrita, ou só `remote.*` e `url.*`), `git init`, `git clone` ou `cd` para outra cópia antes do gh deixa os remotos desconhecidos e recusa, com a dica de rodar o git noutra chamada. Fixtures S23 a S25 com recusa e o legítimo `git -c ... status;` com 0. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As sondas rodaram com o lançador da suíte (`tests/test_hooks.py`: `Fixture.montar`, `rodar`, `montar_proc`), por um script local fora do repositório; as formas do bash e do gh foram conferidas num repositório temporário, sem rede. Teste rodado: `python3 -m unittest tests.test_hooks_parecer_repo` (OK, 5 testes). A suíte inteira roda no CI; este head não tem CI citado (o brief diz "sem suíte local"). Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
