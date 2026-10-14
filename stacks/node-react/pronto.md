# "Pronto" e convenções verificáveis — stack node-react

O `forge-init` usa o comando abaixo como padrão do "pronto" do projeto (`--pronto` sobrescreve).

Comando sugerido: `npm run pronto`

Ele precisa rodar, e falhar se algo falhar: lint (ESLint) e formatação (Prettier) · type-check (TypeScript `strict`) · testes unitários e de integração · build. Reporte o resultado real.

## Código
- `strict: true`, sem `any` (use `unknown` + validação); sem `@ts-ignore` sem comentário explicando.
- Tipos e schemas (zod) compartilhados entre front e back num pacote único; nada de tipo duplicado à mão.
- Sem `console.log` esquecido; lint e formatação automáticos, e o CI falha se não passarem.

## Pirâmide de testes
| Nível | Ferramenta | Quem escreve | Onde |
|---|---|---|---|
| Unitário | Vitest | `node-backend` / `react-frontend` | junto do código |
| Integração de API | Vitest + Supertest | `node-backend` | `server/` |
| Componente | Testing Library + MSW | `react-frontend` | `web/` |
| E2E | Playwright | `qa-engineer` | `e2e/` |
| Acessibilidade | @axe-core/playwright | `qa-engineer` | `e2e/` |

## Vermelho antes do verde, mutação e contrato
- Vermelho: `git stash push -- <arquivos de produção>` e `pnpm vitest run <teste>` precisa falhar; depois `git stash pop`.
- Mutação (Stryker, gratuito): só nos arquivos do diff, `pnpm stryker run --mutate "$(git diff --name-only origin/develop -- '*.ts' '*.tsx' | grep -v '\.test\.' | paste -sd,)"`; a meta fica em `docs/engineering/praticas.md`.
- Contrato back-front: o esquema (zod em `packages/shared`, ou o OpenAPI gerado dele) é a fonte única; um teste no `server/` valida as respostas reais da rota contra ele e outro no `web/` valida os mocks do MSW contra o mesmo esquema. Sem serviço pago: Pact só com os arquivos de contrato versionados no repositório, sem broker.

## Playwright
- Seletores por papel e texto acessível (`getByRole`, `getByLabel`); `data-testid` só em último caso.
- Nada de `waitForTimeout`; use as esperas automáticas e `expect(...).toBeVisible()`.
- Cada teste cria e limpa os próprios dados (via API ou seed), sem depender de ordem.
- Padrão Page Object em `e2e/pages/` para telas reutilizadas.
- Rodar em Chromium por padrão; Firefox e WebKit no CI.
- Acessibilidade: `AxeBuilder` em todas as telas dos fluxos principais, com as tags `wcag2a`, `wcag2aa`, `wcag22aa`.

## Arquitetura de referência (até haver motivo para mudar)
- Monólito modular: `server/` (Node + TypeScript, módulos por domínio) e `web/` (React SPA); monorepo com pnpm workspaces: `server/`, `web/`, `e2e/`, `packages/shared`.
- Banco relacional (PostgreSQL por padrão; o projeto decide em ADR); front ↔ back via REST/JSON versionado (`/api/v1`).
- Autenticação com sessão em cookie httpOnly (ou JWT de curta duração + refresh, via ADR).
- Aplicação no Mermaid do `overview.md`: `Web SPA - React` → `API - Node.js` → banco.

## CI
Insumos da skill `ci-cd` para o `devops-engineer`: toolchain Node da versão do `engines`/`.nvmrc`, com `pnpm` pela versão do `packageManager`; chave do cache de pacotes derivada do `pnpm-lock.yaml`; instalação congelada (`pnpm install --frozen-lockfile`); jobs na ordem lint e type-check, testes unitários e de integração, build, E2E (Chromium por padrão; Firefox e WebKit só no CI); imagem base `node` fixada por digest, em multi-stage, com usuário não root.
