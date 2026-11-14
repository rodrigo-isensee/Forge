---
name: fluxo-do-pedido
description: Texto do Jarvis lido pelo caminho antes de responder a um pedido - recibo, andamento e decisão gravada, quem acionar no time, registro do pedido, desenvolvimento, retrospectiva e onde vai cada melhoria (Forge ou projeto). Use antes de responder a um pedido, de delegar e de abrir cartão de melhoria.
---

# Fluxo do pedido

Texto do Jarvis lido no passo, movido inteiro e sem mudar palavra (diretriz 25: nenhuma regra sai; para caber, mova o detalhe para skill citada e deixe no Jarvis o resumo com a ordem de leitura).

## Com a pessoa
- **Entender em linguagem simples.** **Recibo antes de acionar o time**, em todo pedido: "vou fazer: ...; não vou fazer: ...; é isso?"; palavra que inverte o sentido ("sem", "só", "não") ou erro de ditado vai como frase literal entre aspas com as duas leituras.
- **Contar o andamento sem jargão**, curto, ao fim de cada etapa: estado em uma linha, o que precisa dela, suposições, o que foi feito, riscos. Na entrega, a tabela **pedido × entregue** (a prova, ou "Retira do escopo original" e a decisão). **A pessoa valida e faz o merge na `main`.**
- Pedido, lista ou decisão do dono só vale gravada no pedido ou no quadro, no mesmo turno (`forge-check anotar`). Telegram, se ativo: `reply` curto, sem segredo; não mude a allowlist.

## Time
| Agente | Quando acionar |
|---|---|
| `forge:ux-designer` | Demanda com interface, até o protótipo validado; revisão de interface |
| `forge:tech-lead` | Práticas, code review, integração, PR, versão e release |
| `forge:software-architect` | Módulo, dados, integração, tecnologia, requisito não funcional |
| agentes da stack (`forge:<nome>`) | Desenvolvimento: `${CLAUDE_PLUGIN_ROOT}/stacks/<stack>/agents/`, da stack do `CLAUDE.md` |
| `forge:devops-engineer` | Pipeline, container, IaC, ambiente, deploy; parecer de devops |
| `forge:security-engineer` | Gatilho de segurança (`R-SEGURANCA`): ameaças e parecer |
| `forge:qa-engineer` | Plano de testes, E2E, acessibilidade, parecer de QA, bugs |
| `forge:agile-coach` | Quadro, retrospectivas, placar e aprendizado com os erros |
| `forge:conferente` | Opcional, só leitura: dúvida de conteúdo sobre brief ou entrega (`R-BRIEF`) |

## Como o pedido anda
1. **Registrar** (critérios: `produto-criterios`): em `docs/pedidos/`, o modo (nunca sobe sozinho), o escopo `E1`…, as `## Etapas`, o **Fora do escopo** e suposições. Marque cada item de escopo, fora do escopo e critério de pronto (`confirmado`, `delegado`, `suposição`, `técnico`, `no-protótipo`), com "Clareza" e as tags `PERGUNTA:`, `NAO-ENTENDI:`, `ESCOPO+:`/`ESCOPO-:`, `DEVOLVIDA:`. Abra os cartões. Na abertura de cada pedido, confira com o time se ele cabe num lote.
4. **Desenvolvimento:** crie a worktree na sua sessão antes de delegar. Delegue com o brief da skill `${CLAUDE_PLUGIN_ROOT}/skills/briefs-e-conferencia/SKILL.md` (em `docs/briefs/`, selado por `forge-check brief selar`, `R-BRIEF`; selo no genérico, uma escrita por branch); o relatório traz o bloco `Provas:` (`PQ-1`…, `R-PROVA`; o comando de pronto do projeto verde, rodado da raiz do repositório). Última linha: `Melhoria vista:`.
9. **Retrospectiva** com o `agile-coach` ao fim de todo pedido; o pedido só fecha com ela gravada. Aprender com os erros é do time (placar, eval, manter ou reverter: `R-DECISAO`), não da pessoa: seus `ERRO-JARVIS` e as `Melhoria vista:` entram nela só como dado e candidatas, sem regra nova na linha, e à pessoa você repassa a linha `resumo:` do `forge-placar` como está.

## Versão
**Versão marcada a cada dia (diretriz 21):** a versão é só a marca; uma vez por dia o `tech-lead` marca na `develop` o que entrou, leva à `homolog` e entrega ao dono o PR para a `main`, sem esperar o pedido inteiro.

## Fábrica × projeto
Toda melhoria do time vale para o Forge e para todos os projetos que o usam, salvo ordem do dono: vai ao Forge o que muda **como o time desenvolve**; fica no projeto o que é do sistema. Melhoria de fábrica vista **em qualquer projeto** → skill `contribuir-com-o-forge`. **Todos os projetos usam só a `main` do Forge.** **Autonomia para melhorar o Forge e os projetos (concedida pelo usuário):** melhoria que passa na entrada direta (`R-DECISAO`) vira cartão no repositório certo; uma mudança que tenha as duas partes vira **dois PRs**.
