---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: fe8607dfc22953432cf43dbf4ea4fbf2158292d2
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: travas do conformidade e vigia na sessão do Forge (v0478 E51.1, parecer E51.4)

Prioridade do dono: os agentes do Forge rodam com a conta de administrador, então a regra de proteção do GitHub não segura o envio deles; o hook é a barreira da sessão.

## Gatilhos
Gatilhos: hook de conformidade (controle que analisa comando), R-MAIN, R-VERIFY, R-FLUXO (push para a integração, tag v*), vigia.

## Achados
- A1 (bloqueante) hooks/conformidade.py:3784 · Na sessão do Forge, a recusa `com ação crítica: o hook não modela` (conformidade.py:2159) não é trava: `F=--force; git push $F`, `B=develop; git push origin $B` e `${B:-develop}` passam para todo papel no clone e em wt/*; no projeto, os três recusam.

## Sondas
- S1 · Bash `F=--force; git push $F origin melhoria/x`, cwd ~/.forge-contrib/wt/x, raiz no clone, forge:dev · espera: recusa (código 2), como no projeto · obtido: código 0 (projeto: 2, `$F com ação crítica: o hook não modela`)
- S2 · Bash `B=develop; git push origin $B`, cwd wt/x, raiz no clone, todo papel (6) e cwd no clone · espera: recusa, como no projeto · obtido: código 0 nos 12 casos (projeto: 2)
- S3 · Bash `git push origin ${B:-develop}`, cwd wt/x, raiz no clone, forge:dev · espera: recusa, como no projeto · obtido: código 0 (projeto: 2, `${ com ação crítica`)

## Detalhe dos achados
**A1.** Evidência: `trava_da_sessao_do_forge` (hooks/conformidade.py:3781-3784) só aceita `rid` R-MAIN e R-VERIFY, o texto `push direto para` e a tag v*. A recusa do alvo opaco numa linha com ação crítica (conformidade.py:2159, também 2017, 2119 e 2127) tem `rid` R-CONFORMIDADE e outro texto, e a `GuardaDaProva.barrar` (conformidade.py:3755-3765) a descarta. Caminho de ataque: um agente qualquer da sessão do Forge (dev, devops, tech-lead, a sessão principal), barrado em `git push --force` ou `git push origin develop`, repete o ato com a flag ou o ramo numa variável; com a conta de administrador o remoto aceita, e o push forçado ou direto na integração passa. O vigia o vê só depois (contorno), sem desfazer. Severidade: alta (anula a trava pedida com uma variável, e é a mesma linha que o projeto já recusa). Correção mínima: em `trava_da_sessao_do_forge`, aceitar também as recusas de linha com ação crítica que o hook não decide: o texto `com ação crítica: o hook não modela` (2159), `na chamada com heredoc e ação crítica: o hook não modela` (2127), `na chamada com ação crítica:` (2119) e `chamada com ação crítica e ` (2017); e uma fixture `e51-*` por forma (`$F` em push, `$B` no refspec, `${B:-develop}`, `$N` no commit). Esforço: P. Dono: dev (autor do E51.1). Fora do achado, igual ao projeto: `git push origin $(echo develop)` passa nos dois (lacuna antiga do hook; o sandbox é a garantia, ADR 0009).

## O que foi conferido
- **Travas para todo papel (o pedido do E51.1):** matriz de 30 linhas × 6 papéis (tech-lead, devops-engineer, o dev da stack, dev, security-engineer e a sessão principal sem `agent_type`) × 2 pastas (clone e `wt/*`), remoto `origin` apontando para o Forge. Recusam nos 12 contextos: push para develop, `HEAD:develop`, `HEAD:refs/heads/homolog`, main, `x:main`, `--force`, `-f`, `+ref`, `--force-with-lease`, `--mirror`, `commit --no-verify`, `commit -n`, `-c core.hooksPath=`, `config core.hooksPath`, `git tag v9.9.9`, push da tag, `--tags`, apagar tag, `gh pr merge --admin`, `branch -D develop`, `push --delete homolog`, `bash -c '...'`, aspas partidas (`dev''elop`), `"HEAD:develop"`, `-C .`, e `git push`/`git push origin HEAD` com a branch corrente `develop`. Passam (legítimos): `git push origin melhoria/x`, `git push origin HEAD` numa melhoria, `git tag -l`, `git commit -m x`. Falha só a forma do A1.
- **Só aperta:** o diff de `hooks/conformidade.py` acrescenta uma condição de recusa na `GuardaDaProva.barrar` e passa `na_sessao_do_forge` a `prova_fora_de_projeto`; nada que recusava deixou de recusar (a matriz E50 abaixo dá o mesmo resultado da base; o corpus legítimo segue livre). O `vigia` passa a agir no clone (`clone_do_forge=True`, `hooks/vigia.py:509`), o que só acrescenta registro; erro interno segue saindo 0.
- **Vigia grava:** sonda de `wt/*` (worktree real do clone, cwd na worktree, raiz no clone): SessionStart e Stop com um push barrado seguido de `git -C . push origin HEAD:main` aceito deram `systemMessage` de 1 violação e a linha `"tipo": "contorno"` em `<clone>/.forge/run/violacoes.jsonl`. As fixtures `e51-*` cobrem o clone.
- **Teste novo:** `python3 -m unittest tests.test_hooks.HookSessaoDoForge` na cópia: 2 testes, OK (11 fixtures do conformidade, 2 do vigia). Suíte inteira: só no CI, não rodada aqui.

## Pergunta do dono sobre o E50 (caminhos protegidos das pastas de parecer)
**Não.** Esta mudança não aplica a regra de caminhos protegidos das pastas de parecer (`docs/reviews/` só tech-lead, `docs/qa/` só qa, `docs/devops/` só devops, `docs/security/aceites/` nenhum agente, `docs/security/` só seguranca) na sessão do Forge. A matriz da sonda E50.5 (4 papéis: tech-lead, devops-engineer, o dev da stack, dev × 3 pastas: `docs/reviews`, `docs/qa`, `docs/security` × 6 formas: Write, Edit, `>`, `cp`, `git show >`, texto de interpretador), com o hook desta cópia, deu **0 de 72** escritas barradas em `wt/*`, o mesmo da base; no projeto, as mesmas linhas recusam (salvo o próprio tech-lead em `docs/reviews` por Write, Edit e interpretador). O que falta, as duas coisas juntas:
1. **O filtro:** a `GuardaDaProva.barrar` (conformidade.py:3755-3765) descarta a recusa de caminho dessas cinco entradas de `hooks/conformidade.json` (`docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/aceites/`, `docs/security/`); é preciso aceitar a recusa cujo motivo é o de uma delas, como já se faz com `motivos_do_estado` (conformidade.py:3743).
2. **A raiz do caminho:** fora de projeto, `hook.raiz` é a raiz da sessão (o clone; conformidade.py:3794), e `caminho_barrado` (conformidade.py:1553-1565) só casa `docs/...` relativo a ela ou ao home; em `~/.forge-contrib/wt/<x>/docs/reviews/...` a forma relativa é `~/.forge-contrib/wt/<x>/docs/reviews/...` e não casa. Para essas cinco entradas, a forma relativa precisa vir também do topo do repositório que contém o alvo (a worktree).
Pela leitura (não sondado em separado), uma sem a outra deixa `wt/*` em 0 de 72. Ligar isso é decisão do dono (R-DECISAO): o pedido v0478 E51.1 não o pede.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, sondas locais pelo `rodar` de `tests/test_hooks.py` (scripts no scratchpad da sessão: `sonda_hook_e514.py`, `sonda_travas_e514.py`, `sonda_var_e514.py`, `sonda_var2_e514.py`, `sonda_vigia_e514.py`). Faltaram no PATH: gitleaks, semgrep, zizmor (o diff não toca segredo nem workflow).
