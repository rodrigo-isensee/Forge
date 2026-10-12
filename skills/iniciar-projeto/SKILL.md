---
name: iniciar-projeto
description: Prepara um repositório para ser desenvolvido pela fábrica Forge - cria CLAUDE.md do sistema, quadro KANBAN.md, pastas de docs (pedidos, kanban, retrospectivas, alinhamentos), práticas do projeto, configuração do Claude Code com o Jarvis e o hook que protege a main. Use quando o usuário pedir para iniciar, configurar ou adotar o Forge num projeto.
---

# Iniciar um projeto no Forge

1. Confirme com o usuário: **nome** do projeto, **descrição** em uma frase, a **stack** (pacotes em `${CLAUDE_PLUGIN_ROOT}/stacks/`; padrão `node-react`) e o **comando de pronto**. Se ele não souber o comando, use o sugerido em `stacks/<stack>/pronto.md` e registre como pendência.
2. Confira que o diretório é um repositório git e que você está numa branch de trabalho (`R-MAIN` a main é do usuário). Se a branch atual for `main`, crie `chore/adotar-forge`.
3. Rode o inicializador da fábrica (ele não sobrescreve arquivos existentes):
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/bin/forge-init" --nome "<nome>" --descricao "<descrição>" --stack "<stack>" --pronto "<comando>" .
   ```
4. Leia a saída: arquivos **mantidos** já existiam. Para cada um (ex.: `CLAUDE.md`), compare com o modelo em `${CLAUDE_PLUGIN_ROOT}/templates/projeto/` e proponha ao usuário só as seções que faltam — não sobrescreva conteúdo do projeto.
5. Se o projeto tiver `.claude/agents/` ou `.claude/skills/` com cópias de agentes do time (jarvis, tech-lead, ux-designer...), aplique `R-COPIA` não copiar agentes e skills para o projeto.
6. Preencha com o usuário as seções "Regras invioláveis do sistema" e "Fonte da verdade" do `CLAUDE.md`.
7. Commit (`chore: adota a fábrica Forge`) na branch de trabalho e PR para o usuário validar.
8. O `forge-init` grava `.forge/versao`; projetos antigos (sem ela) se atualizam depois com `forge-upgrade` (ver README, "Atualizar um projeto").
