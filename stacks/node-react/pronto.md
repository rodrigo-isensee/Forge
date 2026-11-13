# "Pronto" e convenções verificáveis — stack node-react

O `forge-init` usa o comando abaixo como padrão do "pronto" do projeto (`--pronto` sobrescreve).

Comando sugerido: `pnpm run pronto`

Detecção: `package.json`

Pronto existente: `package.json` com `"pronto":` → `pnpm run pronto`; `package.json` com `"test":` → `npm test`

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
- Mutação (Stryker, gratuito): só nos arquivos do diff, `pnpm stryker run --incremental --mutate "$(git diff --name-only origin/develop -- '*.ts' '*.tsx' | grep -v '\.test\.' | paste -sd,)"`; a meta fica em `docs/engineering/praticas.md`, começa pela pontuação da primeira rodada e só sobe.
- Fila de pesadas (`R-TETO`): o Stryker e o teste de banco (script `test:db` do `package.json`, repositório e migrações contra um banco descartável local) estão no `pesados.json` da stack e rodam um por vez; projeto criado antes disso mantém a lista dele e acrescenta esses comandos à lista `pesados` do `.forge/config.json`.
- Contrato back-front: o esquema (zod em `packages/shared`, ou o OpenAPI gerado dele) é a fonte única; um teste no `server/` valida as respostas reais da rota contra ele e outro no `web/` valida os mocks do MSW contra o mesmo esquema. Sem serviço pago: Pact só com os arquivos de contrato versionados no repositório, sem broker.

## Veredito do vermelho em TypeScript
O `forge-testes --vermelho` do Forge só mapeia Python; em arquivo `.ts`/`.tsx` ele não dá veredito. Aqui o mapa e o veredito são os desta stack, e o uso nunca termina sem veredito:
- Mapa: `<nome>.ts` ou `<nome>.tsx` leva a `<nome>.test.ts`, `<nome>.test.tsx` ou `__tests__/<nome>.test.ts` na mesma pasta; o teste novo ou alterado no diff vale por si.
- Prova: com a árvore limpa, rode `git stash push -- <arquivos de produção>`; só se ele criar entrada (`git stash list` ganhou uma linha; sem mudança o push sai 0 sem criar nada), rode `pnpm vitest run <teste>`, que precisa falhar, e faça sempre o `git stash pop` em seguida, falhe o teste ou não, para não deixar a produção no stash nem aplicar stash alheio; com o pop feito, o teste precisa passar.
- Veredito: `veredito: provado` (falhou sem a produção, passou com ela), `veredito: sem prova` (passou nos dois) ou `veredito: não verificável` com o motivo (sem teste no mapa, teste que não roda isolado, produção que só existe no diff). O `não verificável` e o `sem prova` vão ao parecer (ou, sem parecer, ao relatório do brief) como pendência, não como aprovação.

## Playwright
- Seletores por papel e texto acessível (`getByRole`, `getByLabel`); `data-testid` só em último caso.
- Nada de `waitForTimeout`; use as esperas automáticas e `expect(...).toBeVisible()`.
- Cada teste cria e limpa os próprios dados (via API ou seed), sem depender de ordem.
- Padrão Page Object em `e2e/pages/` para telas reutilizadas.
- Rodar em Chromium por padrão; Firefox e WebKit no CI.
- Acessibilidade: `AxeBuilder` em todas as telas dos fluxos principais, com as tags `wcag2a`, `wcag2aa`, `wcag22aa`.

## Pré-requisitos do sistema
O Chromium do Playwright precisa de bibliotecas do sistema (por exemplo `libnspr4`); sem elas a primeira suíte E2E falha e custa uma rodada de QA.
- Instalação, **uma vez por máquina e feita pelo usuário** no terminal (pede `sudo`; o agente não usa `sudo`, R-CONFORMIDADE): `npx playwright install --with-deps chromium`.
- Pré-voo, só leitura, que o `qa-engineer` roda antes da primeira suíte de ponta a ponta: `ldd "$(find "${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}" -type f -name chrome -path '*chrome-linux*' | head -n 1)" | grep 'not found'`. Espera: nenhuma linha. Se o `find` não achar o binário, o navegador ainda não foi baixado: o pré-voo vale depois do download.
- Saiu alguma linha `not found`: a etapa para e o `qa-engineer` pede ao usuário, com esta frase:
> Faltam bibliotecas do sistema para o navegador dos testes. Rode no terminal: `npx playwright install --with-deps chromium` (pede a sua senha de administrador). Avise quando terminar.

## Arquitetura de referência (até haver motivo para mudar)
- Monólito modular: `server/` (Node + TypeScript, módulos por domínio) e `web/` (React SPA); monorepo com pnpm workspaces: `server/`, `web/`, `e2e/`, `packages/shared`.
- Banco relacional (PostgreSQL por padrão; o projeto decide em ADR); front ↔ back via REST/JSON versionado (`/api/v1`).
- Autenticação com sessão em cookie httpOnly (ou JWT de curta duração + refresh, via ADR).
- Aplicação no Mermaid do `overview.md`: `Web SPA - React` → `API - Node.js` → banco.

## CI
Insumos da skill `ci-cd` para o `devops-engineer`: toolchain Node da versão do `engines`/`.nvmrc`, com `pnpm` pela versão do `packageManager`; chave do cache de pacotes derivada do `pnpm-lock.yaml`; instalação congelada (`pnpm install --frozen-lockfile`); jobs na ordem lint e type-check, testes unitários e de integração, build, E2E (Chromium por padrão; Firefox e WebKit só no CI); a checagem de pareceres (`forge-check pr`) em job próprio, obrigatório para o merge e fora do `needs` dos jobs de testes, para o parecer faltando não esconder o resultado da suíte; no agregador, o job de pareceres pulado ou cancelado em PR reprova (só `success` passa; `skipped` vale fora de PR), sem `!contains(failure)`; imagem base `node` fixada por digest, em multi-stage, com usuário não root.

### Dependabot (ecossistema de pacotes)
Copie o bloco para o fim de `updates:` do `.github/dependabot.yml` do projeto (modelo em `templates/projeto/.github/dependabot.yml`). Diário às 06:00 (ajuste ao fuso do time); `cooldown` de 1 dia para minor e patch e de 7 para major; rotina só com minor e patch, e o grupo `maiores` à parte, que vira cartão de migração. `ignore` só versionado, por pacote, com o cartão no comentário.

```yaml
  - package-ecosystem: "npm"
    directory: "/"
    target-branch: develop
    schedule:
      interval: "daily"
      time: "06:00"
      timezone: "America/Sao_Paulo"
    open-pull-requests-limit: 5
    cooldown:
      semver-major-days: 7
      semver-minor-days: 1
      semver-patch-days: 1
    groups:
      producao:
        dependency-type: "production"
        update-types: ["minor", "patch"]
      desenvolvimento:
        dependency-type: "development"
        update-types: ["minor", "patch"]
      maiores:
        patterns: ["*"]
        update-types: ["major"]
    ignore: []
```
