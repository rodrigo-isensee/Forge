# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/); versões em [SemVer](https://semver.org/lang/pt-BR/).

## [Não publicado]
### Adicionado
- Núcleo neutro e pacotes de stack (ADR 0001): `stacks/node-react/` com os agentes `node-backend` e `react-frontend` (mesmos nomes, `forge:node-backend` e `forge:react-frontend` continuam valendo), as skills de mesmo nome, `seguranca.md` (checklists de API Node, front React, banco e cadeia de suprimentos) e `pronto.md` (comando "pronto" sugerido, convenções de código, pirâmide de testes e arquitetura de referência). Sem migração: projeto sem a seção "Stack" no `CLAUDE.md` é tratado como `node-react`.
- `plugin.json` lista cada agente (`agents`) e cada skill de stack (`skills`); a lista de `agents` substitui a varredura de `agents/`, e um teste confere que nada fica de fora.
- `forge-init --stack <nome>` (padrão `node-react`): preenche a seção "Stack" do `CLAUDE.md` e usa o "pronto" sugerido pela stack quando `--pronto` não é informado.
- Testes `ManifestoDoPlugin`, `PacotesDeStack` e `NeutralidadeDoNucleo` (sem linguagem, framework ou ferramenta fora de `stacks/`, com exceções explícitas em `tests/config.json`).
- Skill `contribuir-com-o-forge` e `scripts/verificar-contribuicao.sh`: qualquer agente de qualquer projeto contribui com o Forge por PR na `develop` (branch ou fork, clone em `~/.forge-contrib/<projeto>`), com varredura de segredos e caminhos pessoais no diff (ADR 0006).
- `CONTRIBUTING.md` e `.github/pull_request_template.md`.
- `docs/regras/`: uma fonte por regra, com ID (`R-MAIN`, `R-FLUXO`, `R-WIP`, `R-TETO`, `R-QA`, `R-REVIEW`, `R-DISCOVERY`, `R-CUSTO`, `R-NEUTRO`, `R-COPIA`, `R-VERIFY`) e índice (ADR 0002).
- Testes `AntiDuplicacao` (trecho de 12 palavras de uma regra fora da fonte falha) e `RegrasComId` (ID citado existe, frontmatter com `verificada_por`, índice completo).
- **Requer migração (0.5.0):** `bin/forge-upgrade` e `migrations/0.5.0/`: o projeto traz a si mesmo para a versão atual, numa branch `forge/upgrade-<versão>` com um commit por migração, sem push nem merge (ADR 0005). Projetos anteriores (sem `.forge/`) ganham `.forge/versao`, `.forge/config.json` e `.forge/run/` no `.gitignore`.
- `forge-init` grava `.forge/versao` e `.forge/config.json` e ignora `.forge/run/`.
- `bin/forge-check` (`docs`, `kanban`, `pr <pedido>`): valida o contrato entre agentes; modelos com frontmatter para review, QA e plano técnico em `templates/projeto/docs/` e nas instruções do `tech-lead`, `qa-engineer` e `software-architect` (ADR 0004). Testes `ForgeCheck`.
### Alterado
- Núcleo sem stack: `cyber-security`, `engineering-practices`, `software-architecture`, `qa-testing`, `iniciar-projeto`, `qa-engineer`, `software-architect`, o modelo de projeto e `R-TETO` dizem "conforme a stack do projeto" e apontam para `stacks/<stack>/`. O Jarvis lê a stack declarada e delega só aos agentes do pacote. Nenhuma regra, invariante ou termo proibido foi afrouxado.
- `tests/e2e-instalacao.sh` confere os agentes pela lista de `--agent` (o `plugin details` não lista agentes registrados no manifesto).
- Job `versao` do CI: PR para a `develop` exige linha nova em `[Não publicado]` em vez de subir a versão; PR para a `main` exige versão maior e changelog fechado.
- Agentes e "Fábrica × projeto" do Jarvis apontam para a skill, sem o passo a passo duplicado.
- Agentes, skills e modelo de projeto citam as regras pelo ID em vez de repetir o texto (`jarvis.md` 99 → 90 linhas). **Invariantes** de `tests/config.json`: os trechos protegidos passam a ser verificados em `docs/regras/`, e os agentes precisam citar os IDs; nenhum trecho deixou de ser verificado.
- Divergências resolvidas pela redação mais restritiva: QA com WIP 2 no modelo de `KANBAN.md` (era 3); cartão de correção passa por QA com suíte completa; `--force` proibido em qualquer push; branch de trabalho a partir da branch de integração.

## [0.4.1] - 2026-10-12
### Adicionado
- `docs/adr/`: sete ADRs que guiam a evolução da fábrica: núcleo neutro e pacotes de stack (0001), uma fonte por regra com IDs (0002), hooks determinísticos e silenciosos (0003), contrato verificável entre agentes e `forge-check` (0004), migração iniciada pelo projeto (0005), contribuição de qualquer projeto com versão só na release (0006) e verificação de comportamento sem custo (0007).

## [0.4.0] - 2026-10-12
### Adicionado
- `scripts/preparar-estacao.sh`: prepara do zero uma estação WSL (Ubuntu 24.04) para o Forge: pacotes, Node 24 via nvm, pnpm, Claude Code, clone, plugin e atalhos; idempotente, com `--simular`.
- `scripts/jarvis-forge`: atalho versionado para abrir o Jarvis no próprio `~/Forge`; `instalar-atalho.sh` instala os dois.
### Alterado
- Os atalhos `jarvis` e `jarvis-forge` rodam dentro do tmux (sessão `jarvis-<projeto>`), que sobrevive ao fechamento do terminal e se acessa pelo claude.ai/code; `--sem-tmux` mantém o comportamento antigo.

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
