# Patch do dono: denyWrite da tarefa do VS Code e do container no modelo de projeto (BP3 S2)

Propósito: o passo a passo para o dono aplicar a segunda camada da A1, da A2 e da A3 do parecer de segurança da BP3 S2 (`docs/security/v0479-bp3-s2-container.md`). Público: o dono do Forge. Revisão: 2026-11-20.

## O que muda
O VS Code executa `.vscode/tasks.json` ao abrir a pasta (tarefa `runOn: folderOpen`) e o container roda os comandos de `.devcontainer/devcontainer.json` como root, os dois fora do sandbox do Claude Code. O `.vscode/settings.json` muda o PATH e o shell de automação dessa tarefa (`terminal.integrated.env.linux`, `terminal.integrated.automationProfile.linux`), que chama o `tmux` pelo PATH: vale como a própria tarefa (A3 do parecer). Duas camadas protegem os três:

1. O hook `conformidade` (`hooks/conformidade.json`, entradas `quem: []`) recusa a escrita por Write, Edit e Bash de qualquer agente, já nesta branch (`tests/test_conformidade_vscode_container.py`, sondas S1 e S2 do parecer).
2. O `denyWrite` do sandbox do modelo de projeto (`templates/projeto/.claude/settings.json`) cobre a escrita por Bash que o hook não reconhece. O arquivo é de configuração em vigor e os agentes não o editam: vai como patch, `docs/engineering/v0479-bp3-s2-container.patch`, para o dono aplicar, como na A3.

## Aplicar (o dono, na raiz do clone, na branch `melhoria/v0479-bp3-s2-container`)

```bash
git apply --check docs/engineering/v0479-bp3-s2-container.patch && git apply docs/engineering/v0479-bp3-s2-container.patch
python3 -I -c "import json; print(json.load(open('templates/projeto/.claude/settings.json'))['sandbox']['filesystem']['denyWrite'])"
python3 -m unittest tests.test_modelos_projeto
```

A saída esperada da segunda linha é `['.vscode/tasks.json', '.vscode/settings.json', '.devcontainer/devcontainer.json']`. O `--check` falha sem tocar em nada se o arquivo já mudou. Se a A3 (`melhoria/v0479-sandbox-controle`) entrou antes, o arquivo já tem a lista `denyWrite`: acrescente as três linhas ao fim dela à mão, em vez do patch. Commite o arquivo sozinho e envie.

## Consequências
- Nenhum agente muda a tarefa do VS Code nem o container do projeto, inclusive o `devops-engineer`: a imagem e os comandos do container passam a ser do dono (A2, aceito pelo dono em 20/11).
- A entrada do hook vale em qualquer pasta: no Forge, os modelos `templates/projeto/.vscode/tasks.json` e `templates/projeto/.devcontainer/devcontainer.json` e o `.devcontainer/devcontainer.json` do Forge também só mudam pelo dono, como já acontece com `.githooks/`.
- Nenhum agente muda as configurações do VS Code no projeto (`.vscode/settings.json`); elas passam a ser do dono, como a tarefa.
- Os vizinhos seguem graváveis (`.vscode/extensions.json`, `.devcontainer/preparar-ambiente.sh`): o preparo roda de um clone novo da `main`, nunca do work tree.
