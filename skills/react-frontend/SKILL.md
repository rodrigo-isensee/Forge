---
name: react-frontend
description: Convenções de front-end React/TypeScript do projeto - estrutura por feature, componentes, estado, consumo de API com TanStack Query, formulários, acessibilidade e testes. Use ao criar ou alterar código do cliente.
---

# Front-end React

## Stack padrão (quando o projeto ainda não definir outra)
- React + TypeScript (`strict: true`) com Vite
- React Router
- TanStack Query para dados do servidor
- React Hook Form + zod para formulários
- Tailwind CSS (ou a solução de estilo já existente)
- Vitest + Testing Library; MSW para mockar a API
- ESLint + Prettier

## Estrutura
```
web/src/
  features/<feature>/
    components/
    hooks/          # useXxx (queries/mutations da feature)
    api.ts          # chamadas HTTP tipadas da feature
    types.ts
    <Feature>Page.tsx
  components/ui/    # componentes genéricos reutilizáveis
  lib/              # http client, utils
  routes.tsx
```

## Componentes
- Componentes funcionais, props tipadas, um componente por arquivo, PascalCase.
- Sem lógica de negócio em componentes visuais: extraia para hooks.
- Evite `useEffect` para buscar dados — use TanStack Query.
- Estado local primeiro; estado global só quando realmente compartilhado.

## Dados
- Tipos da API espelham o contrato em `docs/api/`.
- Um http client central trata base URL, autenticação e o formato de erro padrão `{ error: { code, message } }`.
- Query keys estáveis: `['orders', { page }]`; invalide após mutations.

## Toda tela deve tratar
carregando (skeleton) · vazio (com orientação) · erro (mensagem + tentar novamente) · sucesso · sem permissão.

## Acessibilidade
- HTML semântico primeiro (`button`, `nav`, `main`, `label`); ARIA só quando necessário.
- Foco gerenciado em modais e após navegação.
- Seguir o checklist da skill `ux-design`.

## Testes
- Testar comportamento, não implementação: `getByRole`, `getByLabelText`.
- Cobrir os critérios de aceite da especificação de UX.
- Mockar a API com MSW, incluindo cenários de erro.

## Segurança
- Nunca usar `dangerouslySetInnerHTML` com conteúdo não sanitizado.
- Nada de segredos no bundle: só variáveis públicas (`VITE_*`).
- Tokens preferencialmente em cookie httpOnly, não em localStorage.
