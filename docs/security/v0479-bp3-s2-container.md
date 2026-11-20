---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: 14c690101de2a9a0442086d9fdad2c1d8deead31
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s2-container (BP3 S2, v0478 E39.15)

Escopo: `git diff 004ce869...14c69010`, 5 arquivos: `templates/projeto/.vscode/tasks.json` (novo), `templates/projeto/.devcontainer/devcontainer.json`, `templates/projeto/.devcontainer/preparar-ambiente.sh`, `tests/test_forge.py`, `changelog.d/v0479-bp3-s2-container.md`. Desenho: `docs/propostas/v0479-bp3-sessao-duravel.md` (branch `melhoria/v0479-bp3-sessao`), tabela de riscos e decisões D2 e D3 do dono (pedido v0478, 2026-11-20 07:47). Revisão estática, com sondas sobre um projeto descartável em `$TMPDIR`; suíte inteira não rodada (fica no CI); rodei os 3 testes novos (OK).

## Gatilhos
Gatilhos: execução automática de comando do work tree ao abrir a pasta (tarefa `folderOpen`), ciclo de vida do container (`shutdownAction`), instalação de pacote como root no preparo.

## Veredito
**Reprovado**, por um bloqueante (A1, alta). O modelo de projeto já trata o work tree como gravável pelo agente e por isso não executa nada dele automaticamente: o `postStartCommand` roda o preparo de um clone raso novo da `main`, nunca do work tree (`templates/projeto/.devcontainer/devcontainer.json:4`). A tarefa nova quebra esse princípio: o VS Code executa o `command` de `.vscode/tasks.json` do work tree a cada abertura da pasta, fora do sandbox do Claude Code, e esse arquivo não é protegido nem pelo hook `conformidade` nem pelo sandbox do modelo.

O resto está correto: o nome da sessão é o mesmo do atalho (`scripts/jarvis:22-23`, `tr '.:' '__'` equivale a `${projeto//[.:]/_}`), o alvo usa `=` (casamento exato), nome de pasta hostil não é reinterpretado (sonda: pasta `x$(touch PWNED);a b` com tmux falso deu `has-session -t =jarvis-x$(touch PWNED);a b` e nenhum arquivo criado), a tarefa nunca chama `new-session` (D3) e o `tmux` vem do apt do sistema, sem chave nem repositório novo. `shutdownAction: none` (D2) mantém o Jarvis vivo sem a janela; é decisão do dono e não abre fronteira nova.

## Achados
- A1 (bloqueante) templates/projeto/.vscode/tasks.json:10 · tarefa runOn folderOpen executa o command do work tree fora do sandbox; .vscode/tasks.json não está em hooks/conformidade.json nem no denyWrite do sandbox do modelo: agente (ou injeção de prompt) a reescreve e roda como root com o login do gh na próxima abertura
- A2 (recomendado) templates/projeto/.devcontainer/devcontainer.json:17 · anterior à entrega: devcontainer.json também é do work tree e gravável pelo agente (postStartCommand e afins rodam fora do sandbox ao iniciar o container); proteger junto com o A1

## Sondas
- S1 · Write de .vscode/tasks.json por forge:dev, hooks/conformidade.py, projeto com .forge/versao, CLAUDE_PROJECT_DIR no projeto · espera: rc=2 (R-CONFORMIDADE, como .githooks/pre-push) · obtido: rc=0; controle .githooks/pre-push rc=2
- S2 · Bash `printf x > .vscode/tasks.json` por forge:dev, mesmo projeto · espera: rc=2 · obtido: rc=0; controle `printf x > .githooks/pre-push` rc=2

## Detalhe dos achados
**A1 (alta).** Evidência: `templates/projeto/.vscode/tasks.json:7` e `:10` (comando e `runOn: folderOpen`); `hooks/conformidade.json:29-83` (lista `caminhos` sem `.vscode/`); `templates/projeto/.claude/settings.json:30-36` (sandbox só com `denyRead`, sem `denyWrite`; o `~/.claude/gh` está negado à leitura justamente para o agente não alcançar o login do dono). Sondas S1 e S2.
Caminho de ataque: um agente do projeto, sob injeção de prompt (texto de issue, dependência, página lida) ou por engano, grava um `command` novo em `.vscode/tasks.json` (o hook deixa, o sandbox deixa, é uma pasta do work tree). Na próxima vez que o dono abre ou reconecta a pasta, o VS Code roda o comando no terminal integrado, como root, sem o sandbox do Claude Code: lê `~/.claude/gh` (login `repo,workflow`) e sai pela rede sem lista de domínios. A permissão de tarefas automáticas, que o desenho diz ser pedida uma vez, já terá sido dada pelo próprio modelo, então a troca do comando passa sem aviso. O mesmo vale para uma branch de terceiros trazida ao work tree. Ganho: o token do dono com escopo de workflow, ou seja, escrita nos repositórios e no CI.
Correção mínima (esforço P):
1. `hooks/conformidade.json`, em `caminhos`, a entrada `{"caminho": ".vscode/tasks.json", "quem": [], "motivo": "arquivo em vigor (.vscode/tasks.json): o VS Code o executa ao abrir a pasta"}`, igual à de `.githooks/`. Dono: `tech-lead` (o arquivo é a política; só `tech-lead` e `doc` o mudam).
2. `templates/projeto/.claude/settings.json`, `sandbox.filesystem.denyWrite` com `./.vscode/tasks.json`, para a escrita por Bash que o hook não reconhece. Dono: `devops-engineer`.
3. Teste: `forge:dev` com Write, Edit e Bash (`printf x > .vscode/tasks.json`, `cp`, `tee`) sobre `.vscode/tasks.json` dá rc=2; o `forge-init` segue copiando o arquivo no projeto novo. Dono: `devops-engineer` (com o `qa-engineer`).
Lista completa dos arquivos do work tree que o VS Code executa sozinho e que a correção deve cobrir: `.vscode/tasks.json` (bloqueante, novo nesta entrega) e `.devcontainer/devcontainer.json` (A2, anterior).

**A2 (média, anterior à entrega).** Evidência: `templates/projeto/.devcontainer/devcontainer.json:17`; o comentário de `:4` mostra que o modelo já considera o work tree gravável pelo agente. Caminho: o agente acrescenta um `postStartCommand` ou `postAttachCommand` próprio; roda fora do sandbox no próximo início do container (com `shutdownAction: none`, mais raro, não impossível). Correção: a mesma entrada em `hooks/conformidade.json` para `.devcontainer/` e o mesmo `denyWrite`, se o dono aceitar que só ele mexe no container do projeto (hoje o `devops-engineer` pode editá-lo; a escolha é do dono, `R-DECISAO`). Esforço P. Dono: `tech-lead` e `devops-engineer`.

Fora do meu domínio, ao `tech-lead`: o desenho lista `.devcontainer/devcontainer.json` do Forge no S2 (D2: "no modelo de projeto e no container do Forge"), e este commit não o toca.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: os hooks rodados localmente sobre projeto descartável e os 3 testes novos de `tests/test_forge.py`. Faltaram no ambiente: `gitleaks`, `zizmor`, `actionlint`, `semgrep`, `shellcheck` (o shellcheck roda no CI); não instalei nada (`R-CUSTO`).
