# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões em [SemVer](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-10-12
### Adicionado
- Plugin `forge` e marketplace no próprio repositório.
- Jarvis (orquestrador) e o time: `tech-lead`, `software-architect`, `ux-designer`, `node-backend`, `react-frontend`, `qa-engineer`, `agile-coach`, extraídos e generalizados do primeiro projeto que usou a fábrica.
- Skills: `engineering-practices`, `software-architecture`, `ux-design`, `node-backend`, `react-frontend`, `qa-testing`, `kanban-scrum`, `cyber-security` e `iniciar-projeto`.
- Regra "Fábrica × projeto": melhorias de processo vão para o Forge; o projeto guarda só o que é do sistema. Autonomia dos agentes para melhorar o Forge e os projetos, sempre por PR validado pelo usuário.
- Modelo de projeto (`templates/projeto`) e inicializador `bin/forge-init`.
- Atalho `jarvis` (retoma a conversa, chat remoto e Telegram opcional).
- Documentos de processo: melhoria contínua, economia de tokens, padrão de documentação, pesquisa de práticas com agentes.
- Fluxo de branches `develop` → `homolog` → `main` com baterias crescentes de testes; todos os projetos usam a `main`.
- Retroalimentação: melhorias descobertas em qualquer projeto viram PR na `develop` do Forge.
- Testes estruturais, teste de instalação de ponta a ponta, avaliações de comportamento e CI/CD.
