---
tipo: revisao-seguranca
contrato: 1
pedido: v047-ambiente-sobrevive
branch: melhoria/v047-ambiente-sobrevive
commit: 680725756d94129c230f52c6401d697463f6e88d
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-15
---
# Review de segurança: v047-ambiente-sobrevive (E2.90, AMBIENTE-SOBREVIVE-RECRIACAO)

Parecer completo (não havia parecer anterior) sobre `cb45a962..68072575`: `.devcontainer/devcontainer.json`, `scripts/preparar-estacao.sh`, `templates/projeto/.devcontainer/devcontainer.json`, `templates/projeto/.devcontainer/preparar-ambiente.sh`, testes e o fragmento do changelog.

## Gatilhos
`R-SEGURANCA`: comando que roda como root fora do sandbox a cada início do container (postStartCommand), credencial do GitHub posta no ambiente do container, instalação de pacote por apt com chave baixada, e mudança no modelo de projeto (chega a todos os projetos, `R-NEUTRO` sem problema).

## Achados
- A1 (bloqueante) .devcontainer/devcontainer.json:23 · O postStartCommand (root, fora do sandbox) roda o script de refs/remotes/origin/main, ref local que o agente reescreve no sandbox (.git/refs e packed-refs graváveis) sem push nem merge: volta o B2 da 0.43.1. Mesmo defeito em templates/projeto/.devcontainer/devcontainer.json:17.
- A2 (bloqueante) .devcontainer/devcontainer.json:18 · remoteEnv põe o GH_TOKEN da máquina do dono (repo e workflow) no ambiente de todo processo do container, inclusive a sessão do agente: anula o denyRead de ~/.claude/gh e a falha fechada sem token do bot (ADR 0009). Idem templates/projeto/.devcontainer/devcontainer.json:12.
- A3 (recomendado) templates/projeto/.devcontainer/preparar-ambiente.sh:45 · A chave do repositório apt do gh é baixada e instalada sem conferir a impressão digital; vale o TLS do domínio oficial. Mesma forma de scripts/preparar-estacao.sh:64 (anterior). Conferir a digital publicada antes do install.

## Sondas
- S1 · rascunho: commit local sem push, `git update-ref refs/remotes/origin/main HEAD`, depois o postStartCommand literal (git show da ref para $f e bash $f) · espera: só roda o script mesclado na main · obtido: `PLANTADO-como-0` (o plantado rodou como uid 0)
- S2 · no sandbox desta sessão, `test -w` em /workspaces/Forge/.git/refs/remotes/origin, .git/packed-refs e .git/config · espera: refs não graváveis pelo agente · obtido: refs e packed-refs graváveis; só .git/config é protegido

## Detalhe dos achados

**A1. A âncora de confiança do postStartCommand é gravável pelo agente.**
- Evidência: `.devcontainer/devcontainer.json:23` e `templates/projeto/.devcontainer/devcontainer.json:17` leem `refs/remotes/origin/main:<script>` e o rodam como root (`remoteUser: root`, fora do sandbox). A ref de rastreamento é um arquivo local em `.git/refs/remotes/origin/main` ou em `.git/packed-refs`; S2 mostra que o sandbox do agente grava os dois. O `.claude/settings.json` só protege `.git/config` e `.forge/`. O comentário em `.devcontainer/devcontainer.json:6-7` diz "código já mesclado pelo dono", mas nada confere isso. O teste `test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree` só confere o texto do comando e não pega o caso.
- Caminho de ataque: um agente sob injeção de prompt (conteúdo de issue, de dependência ou de página lida) faz um commit local com `scripts/preparar-estacao.sh` alterado e roda `git update-ref refs/remotes/origin/main <sha>` (ou `git fetch <qualquer-url> +X:refs/remotes/origin/main`). Não precisa de push, PR nem merge. No próximo início do container, o conteúdo plantado roda como root fora do sandbox: lê `~/.claude/gh`, `~/.ssh` e `~/.claude/settings.json` (o token do bot) e grava em qualquer lugar. É exatamente o escape que o B2 da 0.43.1 fechou. Nos projetos, o mesmo vale para `.devcontainer/preparar-ambiente.sh`.
- Severidade: alta (saída do sandbox para root, com acesso às credenciais que o sandbox nega; o agente precisa estar comprometido, mas é esse o modelo de ameaça do sandbox).
- Correção mínima (esforço P): o root obtém o script por um caminho que o agente não grava. Por exemplo, `d=$(mktemp -d)`, depois `git clone -q --depth 1 --branch main "$(git -C <repo> remote get-url origin)" "$d"` (a URL vem do `.git/config`, protegido), e roda `$d/<script>`; sem rede, nada roda (falha fechada); `rm -rf "$d"` no fim. Não use `fetch` para dentro do mesmo `.git` nem confie em objeto já presente: o armazém de objetos também é gravável pelo agente. Ajustar o teste para exigir a origem remota, em vez de `refs/remotes/origin/main`, e o comentário das linhas 6-7. Vale para os dois devcontainer.json.
- Dono: `devops-engineer`.

**A2. O token do dono passa a estar no ambiente do agente.**
- Evidência: `.devcontainer/devcontainer.json:17-19` e `templates/projeto/.devcontainer/devcontainer.json:11-13` (`remoteEnv.GH_TOKEN = ${localEnv:GH_TOKEN}`). A mensagem de `scripts/preparar-estacao.sh:274` e de `templates/projeto/.devcontainer/preparar-ambiente.sh:31` pede um token com `repo,workflow`, ou seja, o do dono. O `remoteEnv` vale para todo processo que o devcontainer abre (terminal, postStartCommand e o Claude Code iniciado nele), e o sandbox não limpa variáveis. O desenho em vigor (ADR 0009, etapa 2; README:55) é outro: credencial do dono em `~/.claude/gh` e `~/.config/gh`, ambas em `denyRead` (`.claude/settings.json:15-16`, `templates/projeto/.claude/settings.json:33-34`), e o agente só com o token do bot, sem `workflow`. Sem o token do bot o push falha fechado (`docs/reviews/sandbox-bash.md:60`).
- Caminho de ataque: com o token do bot configurado no `env` do `~/.claude/settings.json`, ele sobrescreve o herdado e a exposição se limita aos outros processos do container (terminal do dono, scripts e testes de projeto que rodam fora do Claude). Sem ele (projeto novo, migração incompleta ou instalação em que o dono não configurou o bot), o Bash do agente herda o token do dono: `gh` e `git push` passam a funcionar com o escopo `workflow` e a identidade do dono. Um agente sob injeção, ou um script de teste ou dependência de projeto, lê `$GH_TOKEN` e o envia para fora (o github.com está na lista de rede), ou altera workflow e branch protegida em nome do dono. A falha fechada vira falha aberta.
- Severidade: alta (credencial de escrita com `workflow` exposta ao processo que o sandbox existe para conter).
- Correção mínima (esforço P): tirar o `remoteEnv` dos dois devcontainer.json. O login do gh já sobrevive à recriação, porque `scripts/preparar-estacao.sh:248` liga `~/.config/gh` a `~/.claude/gh`, que está no volume `forge-claude`. No modelo de projeto, fazer o mesmo em `preparar-ambiente.sh` (link `~/.config/gh` para `~/.claude/gh`, sem apagar dados) e manter o login manual (`gh auth login -s repo,workflow --web`) só na primeira vez. Ajustar `test_devcontainer_prepara_sozinho_sem_rodar_o_work_tree`, que hoje fixa o `remoteEnv` com GH_TOKEN, para exigir a ausência de GH_TOKEN e GITHUB_TOKEN em `remoteEnv` e `containerEnv`; ajustar também as mensagens das linhas 274 e 31 e os comentários dos dois devcontainer.json. Se o dono quiser mesmo o login por token do ambiente, é risco a aceitar por ele (`R-DECISAO`).
- Dono: `devops-engineer`.

**A3. Chave apt sem impressão digital conferida.**
- Evidência: `templates/projeto/.devcontainer/preparar-ambiente.sh:45-47` baixa a chave e a instala direto em `/etc/apt/keyrings`. A mesma forma já existe em `scripts/preparar-estacao.sh:64` (anterior a esta entrega).
- Caminho de ataque: só com o TLS de cli.github.com comprometido. É defesa em profundidade.
- Severidade: baixa. Correção: conferir a impressão digital publicada (`gpg --show-keys`) antes do `install`. Esforço P. Dono: `devops-engineer`. Não devolve.

**Conferido sem achado.** `--verificar` só lê (`git config --get`, `gh auth status`, `readlink`) e não altera nada. `container_hooks` e o modelo nunca trocam um `core.hooksPath` de outra ferramenta. O modo essencial (`FORGE_PREPARO_ESSENCIAL=1`) de fato pula `jarvis-forge --atualizar-vigente` e o dev-marketplace, que executam código do work tree. O `; true` no fim não deixa a falha travar o container. O `< /dev/null` impede prompt. Nenhum segredo literal nos arquivos. O shellcheck passa nos dois scripts. Nenhum outro comando de ciclo de vida (`initializeCommand`, que rodaria no host, `onCreate`, `postCreate` ou `postAttach`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: shellcheck (no PATH, sem aviso). Faltaram gitleaks, zizmor e actionlint (fora do PATH; registro a lacuna, não instalei). Varredura de segredo manual por padrão de token nos arquivos do diff: nenhum valor. Testes do item rodados (9, OK): os testes novos de `tests/test_forge.py` (devcontainer, essencial, hooksPath, verificar e modelo de projeto). A suíte inteira não foi rodada: a máquina está carregada e não há PR, então não há CI para citar. O CI do PR fica como condição da revalidação.
