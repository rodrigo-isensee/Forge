---
name: node-backend
description: Convenções de back-end Node.js/TypeScript do projeto - estrutura em camadas, validação com zod, tratamento de erros, padrão de contrato de API, testes e segurança. Use ao criar ou alterar código do servidor.
---

# Back-end Node.js

## Stack padrão (quando o projeto ainda não definir outra)
- Node.js LTS + TypeScript (`strict: true`)
- Fastify (ou Express, se já estiver em uso)
- zod para validação
- Prisma como ORM
- Vitest + Supertest para testes
- ESLint + Prettier

## Estrutura
```
server/src/
  modules/<recurso>/
    <recurso>.routes.ts      # registra rotas e schemas
    <recurso>.controller.ts  # traduz HTTP <-> service
    <recurso>.service.ts     # regra de negócio (sem HTTP)
    <recurso>.repository.ts  # acesso a dados
    <recurso>.schemas.ts     # schemas zod (entrada/saída)
    <recurso>.test.ts
  shared/ (errors, middlewares, config, logger)
  app.ts / server.ts
```

## Convenções de API
- REST, recursos no plural, kebab-case: `GET /api/v1/order-items/:id`.
- JSON em camelCase.
- Paginação: `?page=1&pageSize=20` → `{ data: [...], meta: { page, pageSize, total } }`.
- Erros sempre no formato:
  ```json
  { "error": { "code": "VALIDATION_ERROR", "message": "Mensagem legível", "details": [] } }
  ```
- Status: 200/201/204 sucesso · 400 validação · 401 não autenticado · 403 sem permissão · 404 · 409 conflito · 422 regra de negócio · 500 inesperado (sem detalhes internos na resposta).

## Contrato (`docs/api/<recurso>.md`)
Para cada endpoint: método e rota, autenticação/permissão, parâmetros, body (com tipos), respostas de sucesso e erros possíveis, com exemplo.

## Erros
- Classe `AppError(code, message, status)` lançada pelos services.
- Um error handler global converte para o formato acima e loga erros 5xx.

## Configuração
- Variáveis de ambiente validadas com zod na inicialização (falhar rápido).
- `.env.example` sempre atualizado; `.env` nunca versionado.

## Testes
- Services: testes unitários com repositório mockado.
- Rotas: testes de integração com Supertest cobrindo sucesso, validação e autorização.

## Segurança
- Validação de toda entrada; queries parametrizadas.
- Hash de senha com argon2 ou bcrypt.
- Rate limiting em autenticação; CORS restrito às origens conhecidas; helmet.
- Logs estruturados (pino) sem dados sensíveis (senhas, tokens, documentos).
