---
tipo: revisao-seguranca
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: b458a5752c1e4eb3406b02c7bf9f960580d4ff81
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-19
---
# Review de segurança: rotulo-so-dono (revalidação do delta da volta 1)

Escopo: o delta da volta 1, `git diff 4120acb13b5d5c88578230c850a559007bbebd07 b458a5752c1e4eb3406b02c7bf9f960580d4ff81` (`hooks/conformidade.py`, `tests/test_hooks.py`, `tests/config.json`, `docs/regras/R-CONTRIB.md`, `docs/adr/0009-conformidade-dos-agentes.md`). Este parecer substitui o anterior (reprovado sobre 11d9196). Método: leitura estática e sonda local do hook da worktree pelo próprio harness dos testes (`dados_da_sessao_do_forge` e `rodar_dados`: sessão do Forge, `gh` falso no PATH, sem rede), com cerca de 60 linhas de comando; e os 5 testes novos da volta rodados isolados (OK, 9 s). Nenhum rótulo real foi aplicado.

## Gatilhos
`R-SEGURANCA`: hook de controle (conformidade), que guarda o rótulo `afrouxa-regra`, usado pela catraca para afrouxar um portão.

## Achados
- B1 (bloqueante) hooks/conformidade.py:1275-1280 · crase escapada entre aspas duplas dentro de `bash -c`, `sh -c` ou `eval` passa com outra conta: `` bash -c "echo \`gh pr edit 70 --add-label afrouxa-regra\`" ``, `` sh -c "x=\`gh pr edit …\`" `` e `` eval "echo \`gh pr edit …\`" `` saem 0 na sonda (o shell externo tira a barra e o interno executa a crase; o hook recebe o argumento com `` \` `` e `conteudos_de_crase`, :238, pula a crase escapada); antes de recorrer no argumento de `-c` ou do `eval`, trate `` \` `` como crase (ou, com `` \` `` na linha e o rótulo ou a mutação no texto, `exigir_dono()`)

## Detalhe dos achados

### Os bloqueantes anteriores (A1 a A4): fechados
- **A1 timeout.** `conta_do_gh` (hooks/conformidade.py:1198-1214) usa `TIMEOUT_DA_CONTA = 5` (:101), abaixo dos 10 s do hooks.json, mata o grupo de processos no limite (`start_new_session` e `killpg`, inclusive o filho que segura a saída) e devolve vazio, que barra. O teste `test_rotulo_so_dono_gh_pendurado_decide_antes_do_timeout_do_hook` prova a decisão antes do limite, e `test_timeout_de_rede_dos_hooks_abaixo_do_hooks_json` impede que um subprocesso de rede de qualquer hook volte a passar do timeout. Sonda: `gh` com saída 1, com saída vazia e com conta parecida (`<dono>-x`) barram.
- **A2 GraphQL por caminho.** `endpoint_normalizado` (:219) tira query, fragmento, esquema e host, a barra inicial e o prefixo `api/` ou `api/v3/`. Sonda, todas barram: `/graphql`, `/GraphQL`, `graphql/`, `//graphql`, `https://api.github.com/graphql`, `https://ghe.exemplo/api/graphql`, `graphql?x=1`; `addLabelsToLabelable` inline, por variável (`labelIds:$l`), `--input -` e `-F query=@arquivo`; e também `labelIds` em `updatePullRequest` e `createIssue`.
- **A3 REST com query.** `issues/70/labels?x=1#y`, URL completa em maiúsculas, prefixo GHE `api/v3/`, barra final e o nome em percent-encoding (`afrouxa%2Dregra`, `urllib.parse.unquote` em :1246) barram.
- **A4 crase.** `` echo `gh …` ``, `` x=`gh …` ``, crase entre aspas duplas, crase aninhada por escape no nível de cima e `` bash -c 'echo `gh …`' `` barram; crase sem par que cita o rótulo cai no `ValueError` e barra. A forma que sobra é o B1.

### Os itens extras da volta: conferidos
- **R2 criar ou renomear.** `gh label create|edit` com o nome (`-n`, `--name=`, maiúsculas), `gh api` em `labels` e `labels/<nome>` (POST, PATCH, com query) e as mutações `updateLabel` e `createLabel` (qualquer uma, pelo ID) barram; `gh label create bug` e `edit bug --name defeito` seguem.
- **Erro inesperado (R3 e o item 4 do review).** O `try` em `principal` (:1635-1642) barra quando a linha cita o rótulo ou a mutação e repassa o erro quando não cita; `test_rotulo_so_dono_erro_inesperado_falha_fechado` cobre os dois lados, inclusive com a conta do dono.
- **R4 sessão de projeto.** `gh_contrib` usa `e_graphql` (:1332); `test_contrib_graphql_por_caminho_na_sessao_de_projeto` cobre `/graphql`, a URL completa e `graphql?a=1` com mutação de PR e de rótulo.
- **O que não mudou e segue certo:** formas diretas (`gh pr|issue edit|create` com `--add-label`, `--label`, `-l`, lista por vírgula, `-R`, `env GH_REPO=`, `timeout`, `/usr/bin/gh`, laço, subshell), `bash -c` e `eval` sem crase, `$(...)` (também `\$(...)` dentro de `bash -c "…"`), `bash -c` aninhado e heredoc para `bash` (`bash <<X`, `cat <<X | bash`) barram com outra conta; a conta do dono, em qualquer caixa, libera.
- **Dono vem do plugin.json, não do remoto.** `exigir_dono` (:1295-1303) usa `parecer.slug_do_forge()` (hooks/parecer.py:238-241), que lê `PLUGIN/.claude-plugin/plugin.json`, e `PLUGIN` é a pasta do próprio hook (hooks/_comum.py:23); `repository` ausente ou ilegível dá dono vazio e barra. O texto do E2 do pedido ("dono lido da URL do remoto") diverge; o código está do lado mais seguro e o review já pediu o registro no corpo do PR.
- **R-CUSTO.** `gh api user` é a API gratuita do GitHub (1 das 5000 chamadas por hora), feita só nas linhas que aplicam, criam ou renomeiam o rótulo, uma vez por chamada do hook (`lru_cache`); o custo é só tempo, limitado a 5 s.

### B1: crase escapada em `bash -c`, `sh -c` e `eval`
Evidência: hooks/conformidade.py:1275-1278 (argumento do `-c`) e :1279-1280 (`eval`) recorrem com o texto como o `shlex` o devolve; entre aspas duplas o `shlex` do Python mantém `` \` ``, enquanto o shell real o troca por crase antes de passar ao shell interno. Na recursão, `conteudos_de_crase` (:238) trata `` \` `` como escape e não acha substituição, e as palavras partidas não chegam a um `gh` com subcomando. Sonda, com a conta `outra-pessoa`: `` bash -c "echo \`gh pr edit 70 --add-label afrouxa-regra\`" ``, `` sh -c "x=\`gh pr edit 70 --add-label afrouxa-regra\`" `` e `` eval "echo \`gh pr edit 70 --add-label afrouxa-regra\`" `` saem 0; a mesma linha com `\$(...)` barra, e `` echo "\`…\`" `` sair 0 está certo (ali a crase é literal). Caminho de ataque: um agente na sessão do Forge, a pedido de outro contribuidor ou por injeção de instrução num texto lido, aplica o rótulo com a conta errada; é a combinação de crase (A4) com `bash -c`/`eval`, formas que o brief manda conferir, e é a escrita normal de crase dentro de aspas duplas, não ofuscação deliberada. Severidade: média (a outra conta aplica o rótulo que afrouxa um portão). Correção mínima: no argumento de `-c` e do `eval`, trocar `` \` `` por crase (e `\$` por `$`, `\"` por `"`, `\\` por `\`) antes da recursão, como faz o shell em aspas duplas; ou, mais simples e conservador, com `` \` `` na linha e `CITA_ROTULO` no texto, `exigir_dono()`. Um caso de teste por forma (as três acima barram; `` echo "\`…\`" `` segue). Esforço: P. Dono: tech-lead.

### Recomendações (não bloqueiam)
- **R1 (baixa) Rótulo por variável, `xargs`, alias e escape JSON.** Continua como antes e já virou o cartão ROTULO-VARIAVEL (decisão técnica do Jarvis no pedido); a R-CONTRIB admite o limite ("um script ou uma ofuscação passa").
- **R5 (baixa) A mesma falta na sessão de projeto.** O `bash -c`/`eval` da sessão de projeto (hooks/conformidade.py:742 e :815) tem o mesmo modelo de recursão; vale conferir a crase escapada ali no mesmo cartão do B1, se a correção ficar numa função comum. Não sondado nesta volta.
- **R6 (informativa) Profundidade.** Acima de `PROFUNDIDADE = 3` a recursão para em silêncio (:1258-1259) e libera; exige aninhamento deliberado (quatro níveis), que é ofuscação. Correção barata, se o dono quiser: no limite, com `CITA_ROTULO` no texto, `exigir_dono()`.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática, sonda local com `gh` falso pelo harness de `tests/test_hooks.py` e os 5 testes novos (`python3`, `git`). `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna; o delta não traz dependência, workflow nem segredo). O login do dono nos `gh` falsos dos testes não é segredo.
