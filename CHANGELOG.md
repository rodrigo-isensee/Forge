# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões em [SemVer](https://semver.org/lang/pt-BR/).

## [0.3.0] - 2026-10-12
### Alterado
- Higiene (onda 1): neutralidade da skill `cyber-security` e da regra de cobertura; escolha de modelo numa só fonte (`docs/economia-de-tokens.md`); fim da instrução de copiar agentes para o projeto; Telegram documentado como opcional; assimetria dos hooks pre-push documentada.
### Adicionado
- Ações do CI fixadas por SHA, Dependabot semanal e teste que exige SHA.
- Orçamento de linhas por agente (110) e por skill (133), verificado por teste.
### Corrigido
- Testes rodados dentro do hook pre-push numa worktree herdavam `GIT_DIR` e alteravam o repositório real (`core.bare=true`, `user.name=t`, commit "inicio"). Os testes agora rodam o git com ambiente limpo, os hooks descartam as variáveis `GIT_*` e um teste de regressão protege isso.

## [0.2.1] - 2026-10-12
### Alterado
- **Sem custo de dinheiro real:** removidas as avaliações de comportamento com IA (`evals/` e o workflow), que exigiam API paga. A `homolog` repete a bateria rápida sobre o conjunto da release. O CI não usa mais o segredo `ANTHROPIC_API_KEY`. Nada que custe dinheiro entra no Forge sem autorização expressa do dono.

## [0.2.0] - 2026-10-12
### Adicionado
- Fluxo de branches `melhoria/*` → `develop` → `homolog` → `main` com baterias crescentes: develop (testes estruturais, shellcheck, validação do plugin, instalação de ponta a ponta) e homolog (+ avaliações de comportamento obrigatórias, também toda noite). Todos os projetos usam só a `main`.
- Retroalimentação: melhorias descobertas em qualquer projeto viram PR na `develop` do Forge; o `tech-lead` mescla na develop e promove para a homolog; a `main` só pelo usuário.
- CI confere que nada pula degrau; hook do Forge bloqueia envio direto para `develop`, `homolog` e `main`.
- Teste de instalação de ponta a ponta (`tests/e2e-instalacao.sh`).
### Corrigido
- `forge-init` mescla um `.claude/settings.json` existente (o `claude plugin install --scope project` cria um) em vez de pulá-lo, garantindo o Jarvis como agente principal.

## [0.1.0] - 2026-10-12
### Adicionado
- Plugin `forge` e marketplace no próprio repositório.
- Jarvis (orquestrador) e o time: `tech-lead`, `software-architect`, `ux-designer`, `node-backend`, `react-frontend`, `qa-engineer`, `agile-coach`, extraídos e generalizados do primeiro projeto que usou a fábrica.
- Skills: `engineering-practices`, `software-architecture`, `ux-design`, `node-backend`, `react-frontend`, `qa-testing`, `kanban-scrum`, `cyber-security` e `iniciar-projeto`.
- Regra "Fábrica × projeto": melhorias de processo vão para o Forge; o projeto guarda só o que é do sistema. Autonomia dos agentes para melhorar o Forge e os projetos, sempre por PR validado pelo usuário.
- Modelo de projeto (`templates/projeto`) e inicializador `bin/forge-init`.
- Atalho `jarvis` (retoma a conversa, chat remoto e Telegram opcional).
- Documentos de processo: melhoria contínua, economia de tokens, padrão de documentação, pesquisa de práticas com agentes.
- Testes estruturais, avaliações de comportamento e CI/CD.
