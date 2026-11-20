---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s2-container
commit: c0087a7a92a4a349b39c9063b321d42b94429653
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-bp3-s2-container (BP3 S2, v0478 E39.15, revalidação da A3)

Volta por delta. As rodadas anteriores estão no git: reprovado no head 14c69010 (`b4f4274d`) e aprovado com A3 recomendado no head ed21f2bd (`6995df56`, nunca enviado sozinho, trazido aqui por merge). Delta lido: `forge-check parecer delta`, intervalo `ed21f2bd..c0087a7a`. No domínio: `docs/engineering/v0479-bp3-s2-container.patch`, `hooks/conformidade.json`, `tests/test_conformidade_vscode_container.py`. Também lidos, por tocarem controle: o mutante M5 em `tests/mutantes/v0479-bp3-s2-container.json` e o texto de aplicação em `docs/engineering/v0479-bp3-s2-container.md`. Rodei só o teste novo de abuso (2 testes, OK). A suíte inteira fica para o CI.

## Gatilhos
Gatilhos: execução automática de comando do work tree ao abrir a pasta, arquivo de controle do Forge (`hooks/conformidade.json`), sandbox do modelo de projeto (patch do dono), ciclo de vida do container.

## Veredito
**Aprovado**, sem achado aberto.

A mudança só aperta. Contra a `origin/develop`, `hooks/conformidade.json` só ganha as linhas 33 a 35, todas com `quem: []`; nenhuma entrada anterior sai ou afrouxa. No delta desta volta, só entra a linha 34 (`.vscode/settings.json`). O patch do dono (blob `5ed6008b186ca4ae0f7e70a690b9c7a0484bd018`, um único `diff --git`) só cria `sandbox.filesystem.denyWrite` com três caminhos. Numa cópia descartável do head, `git apply --check` passa. O resultado é `denyWrite: ['.vscode/tasks.json', '.vscode/settings.json', '.devcontainer/devcontainer.json']` e `denyRead` fica intacto. O `templates/projeto/.claude/settings.json` do head é idêntico ao da `origin/develop`, então o patch aplica sobre a base. O dono deve aplicar o patch com o blob acima, idêntico ao revisado (PP1-APLICADO-PELO-DONO). No teste, `.vscode/settings.json` passa de `LIVRES` para `PROTEGIDOS`. O vizinho gravável passa a ser `.vscode/extensions.json`, que o VS Code não executa. O fragmento de changelog muda de seção, fora do domínio.

Estado dos achados anteriores:
- A1 (bloqueante): **resolvido** (rodada de ed21f2bd), sem regressão (S1 e S2 abaixo).
- A2 (recomendado, aceito pelo dono para correção): **resolvido**, sem regressão.
- A3 (recomendado): **resolvido**, pela correção mínima 1 a 3 da rodada anterior: `hooks/conformidade.json:34`, a linha no patch, e `tests/test_conformidade_vscode_container.py:17-18`. O mutante M5 tira a entrada e é morto pelo teste: 15 falhas, 3 papéis × 5 formas.

Sondas no head c0087a7a, com `hooks/conformidade.py` sobre um projeto descartável em `$TMPDIR` (com `.forge/versao`, `CLAUDE_PROJECT_DIR` apontando para ele). Provam a correção, não um bloqueante:
- S1: Write em `.vscode/settings.json` deu rc=2 como `forge:dev` e como `forge:tech-lead`, e Edit deu rc=2 como `forge:devops-engineer`. A mensagem é `R-CONFORMIDADE: arquivo em vigor (.vscode/settings.json)`.
- S2 (Bash, `forge:dev`): rc=2 para `printf x > .vscode/settings.json`, para `./.vscode/settings.json` e para o caminho absoluto. Também rc=2 para `sed -i`, `mv src/app.js .vscode/settings.json`, `cd .vscode && printf x > settings.json`, `rm -rf .vscode` e `mv .vscode .v2`.
- Regressão: `tee .vscode/tasks.json` e Write em `.devcontainer/devcontainer.json` seguem em rc=2.
- Legítimos: Write em `.vscode/extensions.json` e em `src/app.js` deram rc=0.

Lista completa de arquivos do work tree que mudam o que o VS Code ou o container executam sozinhos, todos protegidos agora: `.vscode/tasks.json`, `.vscode/settings.json` e `.devcontainer/devcontainer.json`. `.devcontainer/preparar-ambiente.sh` roda de um clone novo da `main` e fica de fora.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A camada `denyWrite` só vale depois que o dono aplicar o patch revisado (blob acima). Até lá, a proteção é a do hook, provada pelas sondas.

Ferramentas: `hooks/conformidade.py` local, `git apply --check`, o teste novo e o mutante M5 numa cópia descartável. Faltaram no ambiente `gitleaks`, `zizmor`, `actionlint` e `semgrep`. Não instalei nada (`R-CUSTO`).
