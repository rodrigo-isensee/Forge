---
tipo: revisao-seguranca
contrato: 1
pedido: rotulo-so-dono
branch: melhoria/rotulo-so-dono
commit: 11d91963f2d951bdadad4aebc370062140491dcc
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-19
---
# Review de segurança: rotulo-so-dono

Escopo: `git diff 976a1591788eb6bd438dedafef3ab2725bf10de7...11d91963f2d951bdadad4aebc370062140491dcc` (R-CONTRIB, `hooks/conformidade.py`, fixtures, `tests/config.json`, `tests/test_hooks.py`, fragmento do changelog). Método: leitura estática e sonda local do hook (o `conformidade.py` da worktree rodado com um `gh` falso no PATH, conta `outra-pessoa`, sem rede; cerca de 60 linhas de comando). Nenhum rótulo real foi aplicado.

## Gatilhos
`R-SEGURANCA`: hook de controle (conformidade), que guarda o rótulo `afrouxa-regra`, usado pela catraca para afrouxar um portão.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1152 · `gh api user` com timeout=15 s, mas o hook tem timeout de 10 s (hooks/hooks.json:27, 89): com a rede lenta o Claude Code mata o hook antes e o comando segue (falha aberta); baixe para 5 s ou menos
- A2 (bloqueante) hooks/conformidade.py:1184 · GraphQL só é reconhecido com o endpoint exato `graphql`: `gh api /graphql` e `gh api https://api.github.com/graphql` com a mutação addLabelsToLabelable passam (sonda: saída 0); normalize o endpoint (tire esquema, host e a barra inicial)
- A3 (bloqueante) hooks/conformidade.py:1186 · endpoint REST com query string passa: `gh api 'repos/o/r/issues/70/labels?x=1' -f 'labels[]=afrouxa-regra'` sai 0 (o `$` da regex não casa); tire `?…` e `#…` do endpoint antes do teste
- A4 (bloqueante) hooks/conformidade.py:1204 · substituição por crase passa: `echo \`gh pr edit 70 --add-label afrouxa-regra\`` e `x=\`gh pr edit …\`` saem 0 (a crase sem aspas parte as palavras e o `gh` chega sem argumentos); com crase na linha e o rótulo ou a mutação no texto, exija o dono

## Detalhe dos achados

### O que foi conferido e está certo
- **Formas diretas barram com outra conta** (saída 2): `gh pr edit|issue edit --add-label` (com `=`, maiúsculas, lista por vírgula, repetida, antes do número), `gh pr create|issue create --label|-l|-l<rótulo>`, `gh -R/--repo`, `env GH_REPO=… gh`, `FOO=1 gh`, `timeout`, `nohup`, `command`, `/usr/bin/gh`, `cd … &&`, laço `for`, `if`, subshell `( )` e bloco `{ }`, `bash -c`, `bash -lc`, `eval`, `sh -c "eval '…'"`, `$(...)` (também em atribuição), heredoc para `bash`, aspas partidas (`'afrouxa''-regra'`) e barra invertida.
- **gh api REST:** POST implícito por `-f`, `-X PUT|PATCH`, `-XPOST`, `--method=POST`, `issues/<n>/labels` com e sem barra final, `issues/<n>` com PATCH; corpo ilegível (`--input -`, arquivo ausente) barra.
- **GraphQL por ID:** `addLabelsToLabelable` inline, por `--input arquivo`, com variáveis (`labelIds:$l`) e por `--input -` barra sem precisar do nome do rótulo.
- **Erro e timeout da conta:** `gh` com saída 1 barra ("conta do gh: ilegível"); `gh` pendurado barra quando o hook sobrevive aos 15 s (ver A1); `gh` ausente cai em `OSError` e barra. Conta parecida com a do dono (`<dono>-x`) barra; a do dono, em qualquer caixa, libera.
- **Dono vem do plugin.json, não do remoto:** `exigir_dono` usa `parecer.slug_do_forge()` (hooks/parecer.py:238-241), que lê `PLUGIN/.claude-plugin/plugin.json`, e `PLUGIN` é a pasta do próprio hook (hooks/_comum.py:23), a cópia instalada (protegida de escrita no sandbox), não a worktree nem o `git remote`. `repository` ausente ou ilegível dá dono vazio e barra.
- **Outros rótulos e a remoção não mudam:** `--add-label bug` e `--remove-label afrouxa-regra` saem 0; a chamada de rede só acontece quando a linha aplica o rótulo.
- **R-CUSTO:** `gh api user` é a API gratuita do GitHub (só gasta 1 das 5000 chamadas por hora da cota), feita só nas linhas que aplicam o rótulo; o custo é só tempo, limitado pelo timeout (A1 pede que esse limite fique abaixo do do hook).

### A1: timeout da consulta maior que o do hook
Evidência: hooks/conformidade.py:1152 (`timeout=15`) contra `"timeout": 10` do conformidade em hooks/hooks.json:27 e 89. Caminho de ataque: numa sessão do Forge com conta que não é a do dono, com a rede lenta ou a API do GitHub degradada (ou um `gh` que espera por um prompt), a consulta passa de 10 s; o Claude Code encerra o hook por tempo e trata isso como erro que não bloqueia, e o `gh pr edit --add-label afrouxa-regra` executa. O requisito "erro e timeout barram" do pedido só vale se a consulta terminar antes do hook. Na sonda, com um `gh` que dorme, o hook levou cerca de 22 s para decidir. Severidade: média (a outra conta aplica o rótulo que afrouxa um portão, sem o dono). Correção mínima: `timeout=5` (ou menos, deixando folga para o resto do hook) e um fixture que prove que a decisão sai antes dos 10 s. Esforço: P. Dono: tech-lead.

### A2: GraphQL por caminho alternativo
Evidência: hooks/conformidade.py:1184 (`if endpoint == "graphql"`). O `gh` aceita como endpoint um caminho ou uma URL completa; `/graphql` e `https://api.github.com/graphql` mandam os campos `-f query=…` como corpo JSON `{"query": …}` para o mesmo endpoint, que o GitHub executa como GraphQL. Sonda: as duas formas, com `addLabelsToLabelable`, saem 0 com a conta `outra-pessoa`. Caminho de ataque: um agente na sessão do Forge, a pedido de outro contribuidor (ou por injeção de instrução num texto lido), aplica o rótulo por ID global sem a conta do dono; é a forma "GraphQL por ID" que o brief pede para barrar. Severidade: média. Correção mínima: normalizar o endpoint uma vez (tirar `https://<host>/`, `api/v3/` e a barra inicial, e o que vem depois de `?`) antes de comparar, em `aplica_afrouxa_regra`. Esforço: P. Dono: tech-lead.

### A3: endpoint REST com query string
Evidência: hooks/conformidade.py:1186 (`re.search(r"/issues/[^/]+(/labels)?/?$", endpoint)`). O GitHub ignora a query string num POST; `gh api 'repos/o/r/issues/70/labels?x=1' -f 'labels[]=afrouxa-regra'` sai 0 na sonda. Curiosamente `issues/70?a=b` com `-X PATCH` barrou só porque o texto cita o rótulo e a regex cai em outro ramo; o caminho `/labels?…` não. Caminho de ataque e severidade: como A2. Correção mínima: a mesma normalização do A2 (tirar `?…` e `#…`). Esforço: P. Dono: tech-lead.

### A4: substituição por crase
Evidência: hooks/conformidade.py:1204. O analisador parte a crase sem aspas em palavras (`` `gh ``, `pr`, …, `` afrouxa-regra` ``); a recursão recebe só `` `gh `` e `aplica_afrouxa_regra` não acha subcomando. Sonda: `` echo `gh pr edit 70 --add-label afrouxa-regra` `` e `` x=`gh pr edit 70 --add-label afrouxa-regra` `` saem 0, enquanto `$(...)` barra. A crase é a mesma construção que o brief pede para conferir com `$(...)`. Severidade: média. Correção mínima: em `rotulo_na_sessao_do_forge`, se houver crase na linha e o texto citar `afrouxa-regra`, `addLabelsToLabelable` ou `labelIds`, chamar `exigir_dono()` (falha fechado pelo texto, como já faz o ramo do `ValueError`). Esforço: P. Dono: tech-lead.

### Recomendações (não bloqueiam)
- **R1 (baixa) Rótulo por variável, por substituição dentro do valor, por `xargs`, por alias do `gh` e por escape JSON.** Sonda, todos com saída 0: `L=afrouxa-regra; gh pr edit 70 --add-label "$L"`; `--add-label "$(echo afrouxa-regra)"`; `printf afrouxa-regra | xargs gh pr edit 70 --add-label`; `gh alias set al 'pr edit 70 --add-label afrouxa-regra'` seguido de `gh al`; `--input payload.json` com `"afrouxa-regra"` (o texto é lido cru em hooks/conformidade.py:1134 e o GitHub decodifica o escape). Exigem ofuscação deliberada, limite que a R-CONTRIB já admite ("um script ou uma ofuscação passa"). Correção barata, se o dono quiser: tratar como possível rótulo protegido o valor de `--add-label|--label` com `$` ou crase; `json.loads` do corpo do `--input` antes de procurar o nome; `gh alias set` com o rótulo no texto exige o dono. Esforço: P. Dono: tech-lead.
- **R2 (baixa) Troca de nome do rótulo.** `gh label edit afrouxa-regra --name tmp`, `gh api -X PATCH repos/o/r/labels/afrouxa-regra -f new_name=tmp` e a mutação `updateLabel` saem 0; em três passos (renomear, aplicar `tmp`, renomear de volta) o PR fica com `afrouxa-regra`. O pedido (E2) cita `gh label`. Correção mínima: `gh label edit|create|delete` e `gh api` em `labels/…` ou `createLabel|updateLabel|deleteLabel` cujo texto cite o rótulo (ou, no GraphQL, qualquer `updateLabel`) exigem o dono. Esforço: P. Dono: tech-lead.
- **R3 (baixa) Erro interno no ramo novo libera.** A chamada em hooks/conformidade.py:1569 fica fora do `try` de `principal`; uma exceção que não seja `ValueError` vai a `executar` e `falhar_fechado(…, clone_do_forge=False)`, que na sessão do Forge não bloqueia. Não achei entrada que a provoque. Correção mínima: envolver a chamada e, em exceção, `exigir_dono()` se o texto citar o rótulo ou a mutação. Esforço: P. Dono: tech-lead.
- **R4 (média, anterior a este PR) O mesmo `endpoint == "graphql"` na sessão de projeto.** hooks/conformidade.py:1266, em `gh_contrib`: `gh api /graphql` com `closePullRequest`, `updatePullRequest` ou `addLabelsToLabelable` não entra no ramo do GraphQL e não casa `CONTRIB_API`, então a barreira por ID global da R-CONTRIB não vale nessa forma. Não é deste diff; vale um cartão próprio (mesma normalização do A2). Dono: tech-lead.
- **R5 (informativa) Conta da linha diferente da conta do hook.** O hook confere a conta ativa no momento da chamada; `GH_TOKEN=<outro> gh …` ou `gh auth switch` na mesma linha mudam quem age depois da conferência. Na direção que importa (outra conta tentando passar pela do dono) o hook barra, porque vê a conta ativa, que não é a do dono; o caso inverso só acontece na máquina do dono. Sem ação.
- **R6 (informativa) Sessão com `claude --plugin-dir .`.** Aí `PLUGIN` é o clone editável, e o `repository` do plugin.json (e o próprio hook) podem ser mudados pelo agente; é o modelo de confiança de sempre da sessão de desenvolvimento do Forge, e a mudança aparece no diff do PR.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática e sonda local com `gh` falso (`python3`, `git`). `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna; o diff não traz dependência, workflow nem segredo). O fixture `rotulo-so-dono-*-conta-do-dono-libera.json` grava o login do dono num `gh` falso; não é segredo.
