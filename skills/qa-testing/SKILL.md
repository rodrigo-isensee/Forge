---
name: qa-testing
description: Padrões de QA do projeto - plano de testes, pirâmide de testes, E2E, acessibilidade, formato de relatório de bug e critérios de severidade. Use ao planejar, escrever ou executar testes e ao reportar defeitos.
---

# QA

## Pirâmide de testes
| Nível | Quem escreve | Onde |
|---|---|---|
| Unitário | agentes de desenvolvimento da stack | junto do código |
| Integração de API | agente de back-end | conforme a stack |
| Componente | agente de front-end | conforme a stack |
| E2E | `qa-engineer` | conforme a stack |
| Acessibilidade | `qa-engineer` | conforme a stack |

Ferramentas, pastas e comandos: `${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md` (a stack vem do `CLAUDE.md` do projeto).

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

## E2E
- Seletores por papel e texto acessível; `data-testid` só em último caso.
- Nada de espera fixa; use as esperas automáticas da ferramenta.
- Cada teste cria e limpa os próprios dados, sem depender de ordem.
- Navegador padrão no desenvolvimento; os demais no CI.

## Acessibilidade
- Verificação automática em todas as telas dos fluxos principais, com as tags WCAG 2.2 AA.
- Zero violações críticas ou sérias para aprovar.

## Vermelho antes do verde
Todo teste novo de correção ou de regra (`R-QA`) precisa ser visto falhando sem a implementação: guarde o código de produção (`git stash`) ou rode contra o commit anterior. O parecer de QA registra o comando e a falha observada; teste que nunca falhou não prova nada.

## Mutação no código alterado
Quando a stack tiver ferramenta gratuita (`${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/pronto.md`), rode mutação só nos arquivos alterados pelo diff, nunca no projeto inteiro. A meta de pontuação é do projeto, em `docs/engineering/praticas.md`; mutante sobrevivente vira teste novo ou justificativa no parecer. Cobertura de linhas não é meta.

## Relatório de bug (`docs/qa/bugs/<id>-<titulo>.md`)
```markdown
# <id> - <título curto>
- Severidade: crítica | alta | média | baixa
- Responsável sugerido: agente de desenvolvimento da stack
- Ambiente: branch/commit, navegador

## Passos para reproduzir
1. ...

## Resultado esperado
## Resultado obtido
## Evidência
Log, screenshot ou trace da ferramenta de E2E.
```

## Severidade
- **Crítica:** perda de dados, falha de segurança, fluxo principal bloqueado sem contorno.
- **Alta:** funcionalidade importante quebrada, com contorno difícil.
- **Média:** funcionalidade secundária quebrada ou contorno simples.
- **Baixa:** cosmético, texto, alinhamento.

## Critério de pronto
Todos os cenários de prioridade alta passando, nenhum bug crítico ou alto aberto e zero violações de acessibilidade críticas ou sérias.
