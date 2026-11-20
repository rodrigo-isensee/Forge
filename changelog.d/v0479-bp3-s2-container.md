### Adicionado
- Modelo de projeto: a tarefa `Jarvis` do VS Code (`.vscode/tasks.json`, `runOn: folderOpen`) só anexa à sessão tmux que já existe e nunca abre outra, o devcontainer não para ao fechar o VS Code (`shutdownAction: none`) e o preparo instala o `tmux` pelo apt (BP3 S2, v0478 E39.5).

### Segurança
- O hook `conformidade` trata `.vscode/tasks.json` e `.devcontainer/devcontainer.json` como arquivos em vigor: nenhum agente os grava por Write, Edit ou Bash, porque o VS Code e o container os executam fora do sandbox. O container do Forge também ganha `shutdownAction: none`. O `denyWrite` do sandbox do modelo de projeto vai como patch para o dono aplicar (`docs/engineering/v0479-bp3-s2-container.patch`) (BP3 S2, v0478 E39.17).
