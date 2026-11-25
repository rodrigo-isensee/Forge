---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 9a708f86cf6018f09145073a52ce0e7480d9649a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 E11.5 (#877, D6 parte a: hook `salvar`)

## Gatilhos
Gatilhos: hook novo fora do sandbox, rede em hook (afrouxa a ADR 0003 item 2), push automático, controle do git (R-MAIN, R-VERIFY)

Lido: `hooks/salvar.py` inteiro, `hooks/hooks.json`, a emenda da ADR 0003, `ler_brief`, `caminhos_de_brief` e `de_escrita` em `hooks/agentes.py`, a classe `SalvarAoParar` de `tests/test_hooks.py` (23 testes, rodados no clone: OK) e as fixtures novas. CI do #877 no head `9a708f86`: verde nas partes concluídas na leitura, uma parte da suíte ainda pendente (`gh pr checks 877`); o merge espera o CI inteiro.

## Achados
- A1 (bloqueante) hooks/salvar.py:24 · O git do hook roda fora do sandbox lendo o `.git/config` da cópia, que o agente escreve: `filter.<x>.clean`, `remote.origin.receivepack`, `credential.helper`, `core.sshCommand` e `url.*.insteadOf` executam comando ou desviam o envio. GIT_SEGURO só neutraliza hooksPath e fsmonitor.
- A2 (bloqueante) hooks/salvar.py:115 · O envio pula a varredura de segredo do delta que o `.githooks/pre-push` faz (e o pre-commit do projeto), e o commit leva arquivo não rastreado do escopo que o agente não escolheu: segredo chega ao remoto antes do CI. A emenda diz que a guarda do pre-push está no hook; só a de branch está.
- A3 (recomendado) hooks/salvar.py:22 · Seis chamadas de git com 10 s cada mais 40 s do envio somam até 90 s, acima dos 60 s do hooks.json: o hook pode ser morto no meio, sem linha no salvar.log nem no erros.log. Prazo total único, descontado a cada chamada.

## Sondas
- S1 · sonda_salvar.py: `.git/config` da cópia com `filter.x.clean = sh -c 'touch <marca>; cat'` e `.gitattributes` `*.txt filter=x`, depois `salvar.salvar(copia, "melhoria/x", [...])` · espera: comando do config não roda · obtido: marca criada, commit feito e "enviado"
- S2 · sonda_salvar.py: `remote.origin.receivepack = sh -c 'touch <marca>; exit 1' --` no `.git/config` da cópia, depois `salvar.salvar(...)` · espera: comando do config não roda · obtido: marca criada, "envio falhou (rc=128)"
- S3 · `git remote set-url origin <url>` num clone em `~/.forge-contrib/wt/` feito de dentro do sandbox, depois `git config --show-origin --get remote.origin.url` · espera: escrita recusada pelo sandbox · obtido: `file:.git/config`, escrita aceita

## Detalhe dos achados
**A1 (alta; fuga do sandbox).** Evidência: `hooks/salvar.py:24` (GIT_SEGURO), `:31-36` (git_da_copia), `:84-90` (a cópia só precisa estar em `<contrib>/wt/` e na branch). Caminho: o agente (ou texto injetado no contexto dele) cria a cópia como clone, não worktree (a pasta das cópias e o `.git/config` do clone são graváveis no sandbox; S3), grava uma das chaves acima e para; no SubagentStop o hook roda `status`, `add`, `commit` e `push` fora do sandbox, com as credenciais do dono e acesso a `~/.ssh`, `~/.config/gh` e às configurações do Claude Code. `status` e `add` rodam o filtro (S1); `push` roda o receivepack (S2); `credential.helper=!cmd` e `core.sshCommand` rodam no envio; `remote.origin.url`, `remote.origin.pushurl` e `url.<x>.insteadOf` mandam a branch a outro host. É o mesmo motivo que a emenda dá para desligar os hooks do git (código do agente fora do sandbox), por outra porta. Correção mínima: antes de qualquer git na cópia, ler a configuração local dela sem includes (`git config --no-includes --local --list -z`, e `--worktree` quando houver) e não agir se houver chave fora de uma lista de permitidas: `core.repositoryformatversion`, `core.filemode`, `core.bare`, `core.logallrefupdates`, `core.ignorecase`, `core.precomposeunicode`, `core.symlinks`, `extensions.objectformat`, `extensions.worktreeconfig`, `remote.origin.url`, `remote.origin.fetch`, `branch.<nome>.remote`, `branch.<nome>.merge`, `user.name`, `user.email`; recusar também `include.*`, `includeif.*`, `remote.origin.pushurl` e qualquer `remote.<outro>`; exigir `remote.origin.url` igual ao da cópia principal (lida do `.git/config` protegido dela); recusar `.git` em arquivo que aponte para fora de `<cópia principal>/.git/worktrees/`. Testes: um por chave da lista negada acima (filtro, receivepack, credential.helper, sshCommand, insteadOf, pushurl, include) provando que nada roda e nada é enviado, mais um clone com config limpa que salva. Esforço M. Dono: o autor do hook (`forge:devops-engineer` ou quem fez o E11.2).

**A2 (média; vazamento de segredo).** Evidência: `hooks/salvar.py:98` (`--untracked-files=all`), `:109` (`add -A` do escopo), `:115` (push sem a varredura); `.githooks/pre-push:210-228` (`segredo_no_delta`, que o `core.hooksPath=/dev/null` desliga). Caminho: o agente deixa no escopo um arquivo de rascunho, log ou fixture com um token; ele não o commitaria, mas o hook o commita e envia; com o pre-push ligado, a varredura do delta pararia o envio. Depois do envio o segredo está no remoto e pede rotação, mesmo que o CI reprove. Correção mínima: antes do push, rodar a mesma varredura do pre-push, com o script lido de `origin/develop` (nunca da cópia), sobre `origin/<branch>..HEAD`; script ausente, recusado ou com achado: o commit fica na cópia, sem envio, e o motivo vai ao `salvar.log`. Ou, se o dono preferir, declarar a falta da varredura na seção "Afrouxa" da emenda para a decisão dele. Teste: arquivo do escopo com um segredo sintético do formato que o script reconhece; espera commit local e nenhum envio. Esforço P/M. Dono: o autor do hook.

**A3 (baixa).** `PRAZO_GIT_S` vale por chamada; no pior caso (cópia grande, disco lento) o hook passa dos 60 s e o Claude Code o mata depois do commit, sem registro, o que também esconde o critério de reversão da emenda ("passar dos 60 s no erros.log"). Correção: um prazo total (por exemplo 55 s) com o restante passado a cada chamada. Esforço P. Dono: o autor do hook.

## O que aperta, o que é neutro e o que afrouxa
- **Aperta:** nada nas regras de segurança; o item cria uma capacidade nova (commit e envio automáticos) e a cerca bem: refspec explícito sem `+` (não força), `INTEGRACAO` com `main`, `master`, `develop` e `homolog` (`salvar.py:81`), branch da cópia igual à do brief (`:89-90`), um só brief de escrita e uma só cópia, conflito e operação em andamento barrados (`:95-103`), `--only` e `--literal-pathspecs` presos ao escopo, `GIT_*` herdadas removidas, sem prompt de senha, nunca bloqueia nem escreve no stdout. Os 23 testes cobrem esses casos.
- **Neutro:** `R-MAIN` e `R-FLUXO` (o hook nunca envia às branches de integração e o CI do PR segue o portão); `R-CUSTO` (sem mudança no escopo, nem commit nem envio).
- **Afrouxa:** (1) a ADR 0003 item 2, rede num hook, declarada na emenda e à espera do dono; (2) a intenção do `R-VERIFY`, não declarada: rodar o git com `core.hooksPath` vazio não é o `--no-verify` que a regra proíbe (o agente não escolhe nada e rodar os hooks da cópia fora do sandbox seria pior, código do agente fora do sandbox), mas tem o mesmo efeito, as checagens do pre-commit e do pre-push não rodam. A guarda de branch foi reposta; a varredura de segredo não (A2). Com A2 corrigido, o conflito com o `R-VERIFY` some na prática; sem ele, é afrouxamento a declarar na emenda e a decidir pelo dono (`R-DECISAO`). (3) A1 é afrouxamento não intencional do sandbox (ADR 0009) e precisa sair antes do merge, qualquer que seja a decisão sobre a rede.

## Riscos aceitos e ferramentas
Nenhum risco aceito. O merge espera a decisão do dono sobre a emenda (rede no hook) e a correção de A1 e A2. Ferramentas: `gitleaks`, Semgrep, `zizmor` e `actionlint` ausentes no PATH (lacuna); a revisão foi manual, com a sonda local `sonda_salvar.py` (repositórios temporários em `$TMPDIR`, remoto `file://`, sem rede).
