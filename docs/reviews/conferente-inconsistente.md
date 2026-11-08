---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/conferente-inconsistente-reval
commit: 8225a91331c904d7c142fd287a2c8814a07cad3a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-07
---
# Review: versao-035 (E4 CONFERENTE-INCONSISTENTE), revalidação na develop

Revalidação do parecer anterior (reprovado em 4c13fe4, 2026-11-06, bloqueante A1), feita sobre a develop em 8225a91 (release-0.42.0, E1.6c). O código do E4 entrou na develop pela branch única 0.35-0.42 (PR #462): commits dd996f2 (volta 2, A1 e A2), 3e815ee e 6caf595 (teste e mutante K8). Revisor: outra instância do tech-lead, que não é autora do E4. Lidos: `agents/conferente.md` (item 4, linha 50), `bin/forge-check` (`agente_no_plugin` em :3162-3169, linha `destino:` em :6393-6394, `PLUGIN` em :156), `tests/test_conferente_estavel.py` (120 linhas) e o adendo de review do desenho (`docs/arquitetura/versao-035-desenho.md:54`, na área do Jarvis).

## Achados

## Revalidação dos achados anteriores
- A1 (era bloqueante): **fechado**. Em agents/conferente.md:50, o item 4 lê `tools:` só no `<caminho>` da linha `destino: forge:<nome> (agente: <caminho>)` do `forge-check brief` (`ls -l '<caminho>'` e `grep -n '^tools:' '<caminho>'`), e não cita mais `agents/<nome>.md` (`grep -n 'agents/<nome>.md' agents/conferente.md` não acha nada). Esse caminho é absoluto e resolvido a partir do plugin do próprio `forge-check` (`PLUGIN = Path(__file__).resolve().parent.parent`, bin/forge-check:156), não da pasta corrente. Rodado de `/workspaces`, saiu `destino: forge:tech-lead (agente: /root/.forge-contrib/wt/conferente-inconsistente-reval/agents/tech-lead.md)`. Com o `forge-check` antigo (sem `(agente:`), o caso (c) dá `não verificável`, que não reprova. Ele não cai mais em `destino não encontrado`.
- A2 (era recomendado): **fechado**. `agente_no_plugin` (bin/forge-check:3162) procura também em `stacks/<stack>/agents/`. Rodado de `/workspaces`, saiu `destino: forge:node-backend (agente: .../stacks/node-react/agents/node-backend.md)`. Arquivo ausente, link ou nome fora de `[a-z0-9-]+` dão `não encontrado no plugin`, e isso mantém a falha fechada do C-5.
- A3 (era recomendado): **fechado**. O adendo de review do desenho (`versao-035-desenho.md:54`, "Teto do teste") registrou a mudança de teto de 40 para 120 linhas no arquivo inteiro. O `tests/test_conferente_estavel.py` tem 120 linhas, no limite.

## Parecer
Aprovado: nenhum bloqueante ficou aberto. O defeito do A1 (caminho relativo à pasta corrente, que reprovaria todo brief com PQ `cmd` fora do clone do Forge) foi corrigido do jeito que o adendo do desenho define. O `forge-check` passou a dizer onde está o agente. A linha `destino:` não reprova, e quem lê `tools:` continua sendo o conferente. A lista de comandos permitidos ficou igual (C-7, o hash está no teste).

Testes: rodei só o módulo do arquivo tocado (`python3 -I -m unittest discover -s tests -p test_conferente_estavel.py`, ambiente limpo, load1 0,20): "Ran 10 tests ... OK". Não rodei a suíte inteira (D-5 e R-TETO do brief). O push de 7a189d4 rodou os testes afetados (log `/root/.claude/forge-scripts/push-release-7a189d41.log`), e a suíte inteira fica no CI do PR.

Citados, não refeitos: o review e a segurança por grupo da branch única estão em `docs/reviews/uniao-035-042.md` e nos pareceres de segurança dela. O QA da branch única (`docs/qa/uniao-035-042.md`, A1 recomendado: o E4 sem parecer de QA próprio) é do `qa-engineer`. O rótulo `afrouxa-regra` (C-9) fica com o dono.
