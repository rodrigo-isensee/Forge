# Forge

Fábrica de software com agentes para o Claude Code. Um plugin com o **Jarvis** (orquestrador) e o time completo — tech lead, arquiteto, UX, back-end Node, front-end React, QA e agile coach —, o processo de desenvolvimento e os modelos para iniciar projetos.

## O que vem na fábrica
- **Fluxo:** discovery com Design Thinking (UX + arquiteto) → validação do protótipo pelo usuário → desenho técnico → desenvolvimento em paralelo → code review → QA obrigatório → revisão de UX → PR validado pelo usuário → retrospectiva.
- **Regras:** a `main` é do usuário; QA e code review em toda entrega; teto de recursos da máquina; quadro Kanban visível; reuniões de alinhamento; melhoria contínua com autonomia, separando fábrica e projeto.
- **Modelo de projeto:** `CLAUDE.md`, `KANBAN.md`, pastas de pedidos, Kanban, retrospectivas e alinhamentos, práticas, configuração do Claude Code e hook que protege a `main`.

## Usar num projeto
Pré-requisito: acesso ao repositório (privado) pelo git da máquina — chave SSH no GitHub ou `gh auth login` + `gh auth setup-git`.

```bash
cd meu-projeto
claude plugin marketplace add rodrigo-isensee/Forge --scope project
claude plugin install forge@forge --scope project
claude
```
Na sessão, peça: *"inicie este projeto no Forge"* (skill `forge:iniciar-projeto`). Ela cria a estrutura sem sobrescrever o que existe e configura o Jarvis como agente principal (`"agent": "forge:jarvis"` em `.claude/settings.json`).

Atalho opcional para abrir o Jarvis retomando a conversa, com chat remoto e Telegram (se instalado):
```bash
bash ~/.claude/plugins/marketplaces/forge/scripts/instalar-atalho.sh   # ou a partir de um clone do Forge
jarvis            # no diretório do projeto
```

## Branches
Os projetos usam **só a `main`**. Melhorias entram por `develop` (testes rápidos), passam pela `homolog` (bateria completa, com avaliações de comportamento) e chegam à `main` por PR mesclado pelo dono do Forge.

## Atualizar
Cada versão está no `CHANGELOG.md`. Num projeto: `claude plugin update forge@forge` (numa branch, com PR se houver ajuste local).

## Desenvolver o Forge
Ver [`.claude/CLAUDE.md`](.claude/CLAUDE.md): regras, testes, avaliações e versionamento.
