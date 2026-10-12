---
name: software-architecture
description: Padrões de arquitetura do projeto - visão C4 em Mermaid, modelo de ADR, plano técnico de feature, modelo de dados e checklist de requisitos não funcionais. Use ao desenhar sistemas, avaliar tecnologias ou planejar features que cruzam front-end e back-end.
---

# Arquitetura de Software

## Arquitetura de referência (até haver motivo para mudar)
- Monólito modular: `server/` (Node + TypeScript, módulos por domínio) e `web/` (React SPA).
- Banco relacional (PostgreSQL por padrão; o projeto decide em ADR) com camada de acesso tipada.
- Comunicação front ↔ back via REST/JSON versionado (`/api/v1`).
- Autenticação com sessão em cookie httpOnly (ou JWT de curta duração + refresh, via ADR).
- Monorepo com pnpm workspaces: `server/`, `web/`, `e2e/`, `packages/shared` (tipos e schemas zod compartilhados).

## Visão geral (`docs/architecture/overview.md`)
Diagramas C4 nível 1 (contexto) e 2 (containers) em Mermaid:

```mermaid
flowchart LR
  user([Usuário]) --> web[Web SPA - React]
  web -->|REST/JSON| api[API - Node.js]
  api --> db[(PostgreSQL)]
```

## ADR (`docs/architecture/adr/NNNN-titulo.md`)
```markdown
# NNNN - Título da decisão
- Status: proposta | aceita | substituída por NNNN
- Data: AAAA-MM-DD

## Contexto
Qual problema ou força motivou a decisão.

## Decisão
O que foi decidido.

## Alternativas consideradas
Opção, prós, contras — para cada uma.

## Consequências
O que fica mais fácil, o que fica mais difícil, riscos.
```

## Plano técnico de feature (`docs/architecture/features/<feature>.md`)
1. Resumo e link para a especificação de UX.
2. Módulos afetados (back e front).
3. Mudanças no modelo de dados (entidades, relacionamentos, migrações).
4. Endpoints necessários em alto nível (o detalhe fica com `node-backend`).
5. Riscos, dependências e decisões em aberto.
6. Divisão de tarefas: `node-backend`, `react-frontend`, `qa-engineer`, com a ordem e o que pode rodar em paralelo.

## Modelo de dados (`docs/architecture/data-model.md`)
Diagrama ER em Mermaid (`erDiagram`) e, para cada entidade: campos, chaves, índices e regras de integridade.

## Checklist de requisitos não funcionais
- **Segurança:** autenticação, autorização por recurso, validação de entrada, segredos, OWASP Top 10.
- **Performance:** metas de latência (ex.: p95 < 300 ms), paginação, índices, cache quando justificado.
- **Escalabilidade:** API sem estado; jobs pesados em fila.
- **Observabilidade:** logs estruturados, correlation id por requisição, health check, métricas básicas.
- **Confiabilidade:** migrações reversíveis, backups, timeouts e retentativas em integrações externas.
- **Testabilidade:** fronteiras claras entre camadas, dependências injetáveis.
- **LGPD:** dados pessoais mapeados, mínimo necessário, possibilidade de exclusão.
