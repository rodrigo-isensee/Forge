# Como o Forge funciona?

Propósito: dar a visão geral (big picture) da fábrica: quem faz o quê, em que ordem, que guardas vigiam o trabalho e como fábrica e projetos se integram. Público: dono do Forge, quem adota o Forge num projeto e agentes que precisam do contexto geral. Revisão: 2026-11-08.

O texto das regras e o papel de cada agente ficam nas fontes: [`agents/`](../agents/), [`agents/jarvis.md`](../agents/jarvis.md) ("Triagem de cada pedido", "Como conduzir um pedido"), [regras com ID](regras/README.md) e [ADRs](adr/README.md). Aqui só o mapa.

## 1. Fluxo de um pedido

### Do pedido à entrega (fluxo do Jarvis, 0.43.1)

```mermaid
flowchart TB
  U([Dono]) <-->|pedido, decisões uma a uma, merge na main| J[Jarvis orquestrador]
  J --> T{Triagem}
  T -->|orquestração, quadro, comunicação| F[Jarvis faz]
  T -->|todo o resto| D["1-3 Discovery e desenho: ux-designer, software-architect, tech-lead"]
  D --> B["Brief gerado do pedido e selado: forge-check brief selar"]
  B --> V["4 Desenvolvimento: agentes da stack"]
  V --> E["forge-check entrega: grava a entrega conferida"]
  E --> C{"forge-check classe"}
  C -->|T| G1["review + CI"]
  C -->|N| G2["review e QA em paralelo + CI"]
  C -->|C| G3["review, segurança e QA em paralelo + CI"]
  G1 --> DV["develop: entra quando fica pronto"]
  G2 --> DV
  G3 --> DV
  DV --> REL["versão: tag e release sobre a develop; o dono mescla na main"]
  REL --> U
  DV --> AC["9 agile-coach: retrospectiva"]
  AC -.->|melhorias, inclusive remover regra| J
  H["Guardas: hooks, ferramentas e CI (seção 4)"] -.-> B
  H -.-> E
```

Legenda: retângulo = etapa ou agente; losango = decisão; arredondado = pessoa; tracejado = apoio ou vigilância.

<details open>
<summary>Alternativa em lista</summary>

- Dono -> Jarvis: pedido; Jarvis -> Dono: decisões uma a uma, pendentes até a resposta (`R-DECISAO`), e o PR da `main`.
- Jarvis -> Triagem: faz sozinho (orquestração) ou passa a `forge:<agente>`, dizendo qual e por quê.
- Discovery e desenho (`R-DISCOVERY`) -> brief gerado do pedido e selado pela ferramenta (`R-BRIEF`) -> desenvolvimento.
- A ferramenta confere a entrega e grava a linha `entrega conferida` (`R-PROVA`); o conferente agente é opcional, só para dúvida de conteúdo.
- Portões numa passada, pela classe do diff: T (review e CI), N (review e QA em paralelo e CI), C (review, segurança e QA em paralelo e CI, mais devops com infra) (`R-REVIEW`, `R-QA`, `R-SEGURANCA`). Só bloqueia achado com evidência; o parecer vale enquanto o seu domínio não muda.
- Cada item aprovado entra na `develop` quando fica pronto; a versão é uma tag e release sobre a `develop` (`R-FLUXO`).
- `agile-coach` devolve melhorias ao Jarvis; uma melhoria pode remover regra, e toda regra tem `Revisar em:` e `Medida:`.

</details>

## 2. Fábrica e projetos

### Integrações entre o Forge, os projetos e a fonte externa

```mermaid
flowchart LR
  NP["forge novo-projeto, 1o uso"] --> PJ["Jarvis do projeto"]
  DOC["forge doutor (proposta)"] -.-> PJ
  PJ -->|feature/*| PM["main do projeto: merge do dono"]
  PJ -.->|só propõe, R-CONTRIB| FC[("clone de contribuição")]
  FC -->|PR| FD
  F1[("fonte de práticas F1, consulta diária")] -.->|ideias| FM
  subgraph FORGE["Forge, a fábrica"]
    FM["melhoria/*"] -->|review e CI| FD[develop] --> FH[homolog] -->|merge do dono| FMAIN[main] --> REL["release vX.Y.Z"]
  end
  CAT["Catraca do CI e token sem escopo workflow"] -.-> FD
  REL -->|"claude plugin update, forge-upgrade"| PJ
```

Legenda: retângulo = etapa ou branch; cilindro = repositório ou fonte (externo); tracejado = consulta ou vigilância; seta cheia = fluxo de código.

<details open>
<summary>Alternativa em lista</summary>

- `forge novo-projeto` -> Jarvis do projeto: cria o repositório e conduz o primeiro uso; o `forge doutor` (proposta) confere a instalação.
- Jarvis do projeto -> clone de contribuição -> PR na `develop` do Forge: o projeto só propõe (`R-CONTRIB`).
- Fonte F1 -> `melhoria/*`: ideias de prática, verificadas por dia ([fontes de práticas](fontes-de-praticas.md)).
- `melhoria/*` -> `develop` -> `homolog` -> `main` -> release (`R-FLUXO`, `R-MAIN`); a catraca e o token valem nos PRs.
- Release -> projetos: só a `main` do Forge chega a eles, por `claude plugin update` e `forge-upgrade`.

</details>

O Jarvis do Forge roda sobre uma cópia vigente da `develop`, não sobre a cópia em edição ([ADR 0009](adr/0009-conformidade-dos-agentes.md)).

## 3. O time

| Agente | Papel |
|---|---|
| Jarvis | Única interface com o dono: triagem, planejamento, delegação, quadro e resumo de entrega ao dono; não implementa |
| `ux-designer` | Design Thinking até o protótipo validado; revisão da interface pronta |
| `software-architect` | Arquitetura, modelo de dados, integrações, requisitos não funcionais, ADRs |
| `tech-lead` | Boas práticas, code review (`R-REVIEW`), versionamento, integração, release e PR |
| agentes da stack | Implementação, em `stacks/<stack>/agents/` (back-end e front-end do pacote) |
| `qa-engineer` | Plano de testes, E2E, acessibilidade, portão de QA (`R-QA`) |
| `agile-coach` | Quadro Kanban, métricas de fluxo e de qualidade, retrospectivas, validade das regras |
| `conferente` | Opcional, só leitura: dúvida de conteúdo sobre um brief ou uma entrega |
| `devops-engineer` | CI/CD, containers, IaC, ambientes; parecer de devops |
| `security-engineer` | Modelo de ameaças e parecer de segurança quando há gatilho |

## 4. Guardas

| Guarda | Onde age | O que garante |
|---|---|---|
| Hooks (`hooks/`, [guia](hooks.md)) | Em chamadas de ferramenta e em eventos de sessão e subagente | Papéis e caminhos (`conformidade`), pareceres antes do PR, teto e quadro, aviso do que escapou (`vigia`) |
| `forge-check` (selo do brief, entrega, classe, parecer delta) | Em cada delegação e entrega | Forma do brief, entrega conferida, portões da classe, revalidação só do domínio |
| Catraca do CI (`tests/catraca.py`) | Em cada PR do Forge | Regras invioláveis, custo zero, neutralidade, pareceres; mudar arquivo protegido pede o rótulo do dono |
| Sandbox do Bash ([README](../README.md#sandbox-do-bash)) | Em cada comando | Escrita só nas pastas de trabalho, credenciais ilegíveis, APIs de modelo negadas |
| Token da conta de máquina | No GitHub | Sem escopo `workflow`: workflows só o dono muda |

Regras por tema: [`R-MAIN`](regras/R-LIMITES.md), [`R-FLUXO`](regras/R-FLUXO.md), [`R-CONTRIB`](regras/R-LIMITES.md), [`R-CONFORMIDADE`](regras/R-CONFORMIDADE.md), [`R-CUSTO`](regras/R-LIMITES.md), [`R-NEUTRO`](regras/R-NEUTRO.md). Decisões: [0003 hooks](adr/0003-hooks-deterministicos-e-silenciosos.md), [0006 contribuição](adr/0006-contribuicao-de-qualquer-projeto.md), [0008 governança](adr/0008-governanca-de-contribuicoes.md), [0009 conformidade](adr/0009-conformidade-dos-agentes.md).
