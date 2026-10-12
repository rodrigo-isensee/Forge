---
name: ux-design
description: Padrões de UX/UI do projeto - Design Thinking no upstream das demandas, formato de especificação de telas, checklist de acessibilidade (WCAG 2.2 AA), heurísticas de usabilidade e microcopy. Use ao desenhar ou revisar telas e fluxos.
---

# UX Design

## Design Thinking (upstream de toda demanda com interface)
Estrutura em `docs/ux/<demanda>/`:

| Etapa | Arquivo | Conteúdo mínimo |
|---|---|---|
| Empatizar | `01-empatia.md` | Personas (objetivo, contexto, dores, frequência de uso); mapa de empatia (pensa, sente, vê, ouve, faz, dores, ganhos); jornada atual com momentos de atrito; hipóteses e perguntas abertas |
| Definir | `02-definicao.md` | Declaração do problema: "[persona] precisa de [necessidade] porque [insight]"; 3 a 5 perguntas "Como podemos...?"; critérios de sucesso mensuráveis |
| Idear | `03-ideacao.md` | ≥ 3 alternativas (esboço em texto ou ASCII), prós, contras, esforço; matriz impacto × esforço; alternativa escolhida e por quê |
| Prototipar | `04-prototipo/index.html` | HTML + CSS estáticos, sem build e sem dependências externas; fluxos principais navegáveis; dados de exemplo realistas; aviso "protótipo" visível |
| Validar | `05-validacao.md` | Roteiro: tarefas que o usuário deve conseguir fazer e perguntas; registro do retorno; decisão: aprovado, ajustar (voltar à etapa X) ou descartar |
| Especificar | `especificacao.md` | Formato da seção "Formato da especificação" abaixo, referenciando as etapas anteriores |

Regras:
- Diverge antes de convergir: nunca uma única alternativa.
- Hipótese não validada fica marcada como hipótese até o usuário confirmar.
- **A validação do usuário no protótipo é o ponto de compromisso** do quadro Kanban: só então a demanda passa para "Pronto para fazer".
- Correções e tarefas técnicas sem impacto de interface não passam pelo upstream de UX.

## Formato da especificação (`docs/ux/<demanda>/especificacao.md`)

```markdown
# <Nome da feature>

## Objetivo
Problema do usuário e resultado esperado (1-3 frases).

## Personas / contexto de uso
Quem usa, em que dispositivo, com que frequência.

## Fluxo
1. Passo a passo da jornada principal.
2. Fluxos alternativos e de erro.

## Telas
### <Tela>
- Wireframe (ASCII ou descrição estruturada da hierarquia)
- Componentes usados (reaproveitar os existentes)
- Estados: carregando | vazio | erro | sucesso | sem permissão
- Interações: o que acontece em cada clique/submit
- Validações de formulário e mensagens

## Necessidades de dados
O que a tela precisa ler/gravar (para o back-end).

## Microcopy
Textos de botões, títulos, mensagens de erro e confirmação.

## Critérios de aceite
Lista verificável usada pelo front-end e pelos testes.
```

## Checklist de acessibilidade (WCAG 2.2 AA)
- Contraste mínimo 4.5:1 para texto, 3:1 para texto grande e elementos de UI.
- Tudo operável por teclado; foco visível; ordem de foco lógica.
- Alvos de toque ≥ 24×24px (ideal 44×44px).
- Todo campo tem label visível; erros associados ao campo e anunciados.
- Não depender só de cor para transmitir informação.
- Imagens informativas com texto alternativo.
- Respeitar `prefers-reduced-motion`.

## Heurísticas (Nielsen)
Visibilidade do status · correspondência com o mundo real · controle e liberdade · consistência · prevenção de erros · reconhecer em vez de lembrar · flexibilidade · design minimalista · ajudar a recuperar de erros · ajuda e documentação.

## Microcopy
- Português do Brasil, tom direto e cordial, voz ativa.
- Botões com verbo de ação ("Salvar alterações", não "OK").
- Mensagens de erro dizem o que aconteceu e como resolver; nunca culpam o usuário.
- Ações destrutivas pedem confirmação nomeando o que será afetado.

## Layout
- Mobile-first; breakpoints: 640, 768, 1024, 1280px.
- Espaçamento em múltiplos de 4px.
- Uma ação primária por tela/seção.
