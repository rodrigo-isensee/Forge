---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: ed21f2bd663c730ab23446ac2554504ad2e91319
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s2-container (BP3 S2, v0478 E39.15, revalidação)

Volta por delta. A rodada anterior (reprovado no head 14c69010) está no git (`b4f4274d`). Delta lido: `forge-check parecer delta`, intervalo `14c69010..ed21f2bd`. No domínio: `.devcontainer/devcontainer.json`, `docs/engineering/v0479-bp3-s2-container.patch`, `hooks/conformidade.json`, `tests/test_conformidade_vscode_container.py`. Também lidos, por tocarem controle: a linha nova de `tests/test_forge.py` e o texto de aplicação em `docs/engineering/v0479-bp3-s2-container.md`. Rodei só o teste novo de abuso (2 testes, OK). A suíte inteira fica para o CI.

## Gatilhos
Gatilhos: execução automática de comando do work tree ao abrir a pasta, arquivo de controle do Forge (`hooks/conformidade.json`), sandbox do modelo de projeto (patch do dono), ciclo de vida do container.

## Veredito
**Aprovado**, com um recomendado (A3). Ele volta ao autor e é corrigido antes do merge (`R-REVIEW`).

A mudança só aperta. `hooks/conformidade.json:33-34` só acrescenta duas entradas com `quem: []` e não remove nem afrouxa nenhuma das que já existiam. O patch `docs/engineering/v0479-bp3-s2-container.patch` (blob `7cb8abfffbe4c1e09efdaa44a632dc63cff4f16f`) só cria `sandbox.filesystem.denyWrite` com os dois caminhos. Conferi o patch numa cópia descartável: `git apply --check` passa, e o resultado é `denyWrite: ['.vscode/tasks.json', '.devcontainer/devcontainer.json']`. `denyRead`, `network` e `permissions` ficam intactos. O formato dos caminhos é o mesmo do `denyWrite` da A3 (`melhoria/v0479-sandbox-controle`). Se a A3 entrar antes, a junção à mão descrita em `docs/engineering/v0479-bp3-s2-container.md:19` só acrescenta linhas. O dono deve aplicar o patch com o blob acima, idêntico ao revisado (caminho PP1-APLICADO-PELO-DONO, decisão de 09:43). `tests/test_forge.py:1996` só acrescenta uma asserção. `shutdownAction: none` no `.devcontainer/devcontainer.json:21` do Forge é a D2 do dono: muda o ciclo de vida, não aperta nem afrouxa controle e não abre fronteira nova (já avaliado na rodada anterior para o modelo).

Estado dos achados anteriores:
- A1 (bloqueante): **resolvido**. Entrada no hook em `hooks/conformidade.json:33`, segunda camada no patch do dono. Prova: S1, S2 e o teste `tests/test_conformidade_vscode_container.py` (3 papéis × Write, Edit, `printf`, `cp`, `tee`, mais os vizinhos graváveis).
- A2 (recomendado, aceito pelo dono para correção): **resolvido** em `hooks/conformidade.json:34` e no patch.

## Achados
- A3 (recomendado) templates/projeto/.vscode/tasks.json:7 · a tarefa folderOpen resolve tmux pelo PATH e roda no shell de automação do VS Code, ambos ajustáveis por .vscode/settings.json (terminal.integrated.env.linux, automationProfile.linux), que segue gravável pelo agente: protegê-lo como o tasks.json

## Sondas

## Detalhe dos achados
**A3 (média, recomendado, achado novo que a rodada anterior deixou passar).** Evidência: `templates/projeto/.vscode/tasks.json:7` chama `tmux` sem caminho absoluto, e `:10` roda a tarefa ao abrir a pasta. `tests/test_conformidade_vscode_container.py:17` deixa `.vscode/settings.json` gravável de propósito (sondado: `Write` por `forge:dev` dá rc=0).

Caminho de ataque: um agente sob injeção de prompt grava em `.vscode/settings.json` um `terminal.integrated.env.linux` com `PATH` começando numa pasta do work tree, onde põe um `tmux` próprio. Também serve um `terminal.integrated.automationProfile.linux` apontando para um script. Na próxima abertura, a tarefa protegida roda o binário do agente como root, fora do sandbox, com acesso ao login do `gh`. É o mesmo ganho da A1. São configurações de workspace marcadas como restritas, que o VS Code honra em workspace confiável, e a pasta do dev container é confiável. Não sondado: não há VS Code neste ambiente, por isso fica recomendado, não bloqueante.

Correção mínima (esforço P):
1. Em `hooks/conformidade.json`, a entrada `{"caminho": ".vscode/settings.json", "quem": [], "motivo": "arquivo em vigor (.vscode/settings.json): ambiente e shell da tarefa que o VS Code roda ao abrir a pasta"}`.
2. A mesma linha `.vscode/settings.json` no `denyWrite` do patch do dono.
3. No teste, mover `.vscode/settings.json` de `LIVRES` para `PROTEGIDOS` e usar `.vscode/extensions.json` como vizinho gravável.

Alternativa mais simples: proteger `.vscode/` inteira, já que o modelo só traz `tasks.json`. Ela tira dos agentes a edição das configurações do editor no projeto, então a escolha é do dono (`R-DECISAO`).

Lista completa de arquivos do work tree que mudam o que o VS Code ou o container executam sozinhos: `.vscode/tasks.json` (protegido), `.vscode/settings.json` (A3) e `.devcontainer/devcontainer.json` (protegido). `.devcontainer/preparar-ambiente.sh` roda de um clone novo da `main`, nunca do work tree, e fica de fora.

Dono: `tech-lead` (o hook) e `devops-engineer` (o patch e o teste).

Sondas refeitas no head ed21f2bd, com `hooks/conformidade.py` como `forge:dev` sobre um projeto descartável em `$TMPDIR` (provam a correção, não um bloqueante; por isso ficam fora do bloco):
- S1: Write em `.vscode/tasks.json` deu rc=2 (`R-CONFORMIDADE: arquivo em vigor (.vscode/tasks.json)`); também rc=2 com Write em `.devcontainer/devcontainer.json`.
- S2: `printf x > .vscode/tasks.json` deu rc=2; também rc=2 com `./.vscode/tasks.json`, com caminho absoluto, `mv`, `sed -i`, `cd .vscode && printf x > tasks.json`, `rm -rf .vscode`, `mv .vscode .v2` e `printf` em `devcontainer.json`.
- Vizinhos `.vscode/settings.json` e `.devcontainer/preparar-ambiente.sh` deram rc=0, como o desenho quer.
- O modelo `templates/projeto/.vscode/tasks.json` no Forge deu rc=2, consequência declarada em `docs/engineering/v0479-bp3-s2-container.md:23`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A camada `denyWrite` só vale depois que o dono aplicar o patch revisado (blob acima). Até lá, a proteção é a do hook, provada pelas sondas.

Ferramentas: `hooks/conformidade.py` local, `git apply --check` e o teste novo. Faltaram no ambiente `gitleaks`, `zizmor`, `actionlint` e `semgrep`. Não instalei nada (`R-CUSTO`).
