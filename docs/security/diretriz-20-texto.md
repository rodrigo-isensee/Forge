---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/diretriz-20-texto
commit: 29fa5da070a90c0a2b492621f73df5fc5cf271c4
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: diretriz 20 no texto (E26.10)

## Gatilhos
Nenhum gatilho da `R-SEGURANCA` tocado: só texto de agente e de skill (classe C), sem hook, analisador, workflow nem segredo. Revisado por segurança a pedido do brief: nenhum corte removeu controle, invariante ou regra com ID, e o texto novo não abre caminho para contornar portão.

## Achados
- A1 (recomendado) skills/kanban-scrum/SKILL.md:42 · RESOLVIDO na volta E26.12 (666010d6, 29fa5da0): o texto afirma que `forge-check kanban` recusa destino divergente, mas `cmd_kanban` (bin/forge-check:420) só confere colunas, ID, responsável e WIP; falta a ressalva "até o comando existir, o agente confere com a última triagem" da diretriz 20.

## Sondas

## Detalhe dos achados
A1. Evidência: skills/kanban-scrum/SKILL.md:41 contra bin/forge-check:420-470 (sem comparação com triagem). Caminho de ataque: nenhum realista; é falsa garantia (quem lê acredita que a ferramenta barra o quadro divergente e deixa de conferir à mão). Severidade: informativa. Correção mínima: no mesmo item, "o `forge-check kanban` recusará" ou "até o comando existir, o agile-coach confere com a última triagem"; some quando o cartão de `bin/forge-check` da 0.46 entrar. Esforço: P. Dono: tech-lead.

Cortes conferidos (diff c340c322..bad4f5aa):
- agile-coach: "sem burocracia que não gere decisão", "as duas de estabilidade pesam tanto quanto as de velocidade" e "mais de 30% de itens `delegado`" são orientação, não controle; ausentes de `invariantes` e sem ID de regra. A linha dos dois relógios mantém `D-4`, `relogios:` e a meta de 30 min.
- skill: saiu "Dois relógios" (continua no agile-coach, que é o dono da medição); vazão, idade do WIP e bloqueio foram só condensados, sem perda de definição. `R-WIP`, `R-DECISAO` e o resto seguem.
- Todos os trechos de `tests/config.json` `invariantes` para `agents/agile-coach.md` e `skills/kanban-scrum/SKILL.md` seguem presentes no head (conferido, 0 faltas).
- Texto novo: não afrouxa portão, não cria isenção nem dispensa parecer; manda atualizar o quadro e arquivar plano substituído.

## Revalidação por delta (E26.24)
Intervalo do domínio (`forge-check parecer delta`, sem o que veio da develop): bad4f5aa..29fa5da0, três arquivos no domínio: agents/agile-coach.md, skills/kanban-scrum/SKILL.md, tests/config.json (changelog.d fora). Commits da branch: 666010d6 e 29fa5da0.
- A1 resolvido: SKILL.md:42 agora diz "Até o `forge-check kanban` recusar destino divergente, o agile-coach confere com a última triagem", a ressalva pedida; SKILL.md:44 mantém plano ou pedido substituído indo para `arquivo/`. Arquivo com 133 linhas.
- agents/agile-coach.md:12 acrescenta "pedido" a "plano substituído vai para `arquivo/`": só amplia o arquivamento, não afrouxa portão nem dispensa parecer.
- tests/config.json: invariante novo para agents/agile-coach.md com `invariantes_motivo_trecho` (regra R-DECISAO, motivo escrito); só acrescenta proteção, nada removido. Conferido por script: 0 faltas nos invariantes dos dois arquivos no head.
- Os demais arquivos do intervalo bruto 473ffd09..29fa5da0 vêm do merge da develop (1fd813e6) e têm parecer próprio; fora deste delta.
- Sem novo gatilho da `R-SEGURANCA`; sem achado novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados do head 29fa5da0: tests.test_forge.Orcamento (2 OK), tests.test_forge.RegrasInviolaveis (3 OK), tests.test_clareza e tests.test_sobreposicao_quadro (70 OK); CI do PR ainda não existe (sem PR), suíte inteira só no CI. Sem ferramenta faltando para texto.
