---
name: qa-testing
description: Padrões de QA do projeto - plano de testes, pirâmide de testes, Playwright para E2E, axe para acessibilidade, formato de relatório de bug e critérios de severidade. Use ao planejar, escrever ou executar testes e ao reportar defeitos.
---

# QA

## Pirâmide de testes
| Nível | Ferramenta | Quem escreve | Onde |
|---|---|---|---|
| Unitário | Vitest | `node-backend` / `react-frontend` | junto do código |
| Integração de API | Vitest + Supertest | `node-backend` | `server/` |
| Componente | Testing Library + MSW | `react-frontend` | `web/` |
| E2E | Playwright | `qa-engineer` | `e2e/` |
| Acessibilidade | @axe-core/playwright | `qa-engineer` | `e2e/` |

Os E2E cobrem os fluxos críticos; o restante fica nos níveis mais baixos.

## Plano de testes (`docs/qa/<feature>.md`)
```markdown
# Plano de testes - <feature>
Links: especificação de UX, contrato da API, plano técnico.

## Escopo
O que está e o que não está coberto.

## Cenários
| ID | Cenário | Tipo | Prioridade | Automatizado |
|---|---|---|---|---|
| CT-01 | Login com credenciais válidas | E2E | Alta | sim |

## Dados de teste
Usuários, permissões e fixtures necessários.

## Resultado da execução
Data, ambiente, aprovados/falhos, links para bugs.
```

Para cada critério de aceite da especificação, pelo menos um cenário. Sempre incluir: entradas inválidas, limites (vazio, máximo, caracteres especiais), usuário sem permissão, falha da API e navegação só por teclado.

## Playwright
- Seletores por papel e texto acessível (`getByRole`, `getByLabel`); `data-testid` só em último caso.
- Nada de `waitForTimeout`; use as esperas automáticas e `expect(...).toBeVisible()`.
- Cada teste cria e limpa os próprios dados (via API ou seed), sem depender de ordem.
- Padrão Page Object em `e2e/pages/` para telas reutilizadas.
- Rodar em Chromium por padrão; Firefox e WebKit no CI.

## Acessibilidade
- `AxeBuilder` em todas as telas dos fluxos principais, com as tags `wcag2a`, `wcag2aa`, `wcag22aa`.
- Zero violações críticas ou sérias para aprovar.

## Relatório de bug (`docs/qa/bugs/<id>-<titulo>.md`)
```markdown
# <id> - <título curto>
- Severidade: crítica | alta | média | baixa
- Responsável sugerido: node-backend | react-frontend
- Ambiente: branch/commit, navegador

## Passos para reproduzir
1. ...

## Resultado esperado
## Resultado obtido
## Evidência
Log, screenshot ou trace do Playwright.
```

## Severidade
- **Crítica:** perda de dados, falha de segurança, fluxo principal bloqueado sem contorno.
- **Alta:** funcionalidade importante quebrada, com contorno difícil.
- **Média:** funcionalidade secundária quebrada ou contorno simples.
- **Baixa:** cosmético, texto, alinhamento.

## Critério de pronto
Todos os cenários de prioridade alta passando, nenhum bug crítico ou alto aberto e zero violações de acessibilidade críticas ou sérias.
