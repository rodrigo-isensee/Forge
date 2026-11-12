---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/diretriz-20-texto
commit: bad4f5aaab7776ab2efaeec2c5e52c05b6ac3564
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: diretriz 20 no texto (E26.10)

## Gatilhos
Nenhum gatilho da `R-SEGURANCA` tocado: só texto de agente e de skill (classe C), sem hook, analisador, workflow nem segredo. Revisado por segurança a pedido do brief: nenhum corte removeu controle, invariante ou regra com ID, e o texto novo não abre caminho para contornar portão.

## Achados
- A1 (recomendado) skills/kanban-scrum/SKILL.md:41 · o texto afirma que `forge-check kanban` recusa destino divergente, mas `cmd_kanban` (bin/forge-check:420) só confere colunas, ID, responsável e WIP; falta a ressalva "até o comando existir, o agente confere com a última triagem" da diretriz 20.

## Sondas

## Detalhe dos achados
A1. Evidência: skills/kanban-scrum/SKILL.md:41 contra bin/forge-check:420-470 (sem comparação com triagem). Caminho de ataque: nenhum realista; é falsa garantia (quem lê acredita que a ferramenta barra o quadro divergente e deixa de conferir à mão). Severidade: informativa. Correção mínima: no mesmo item, "o `forge-check kanban` recusará" ou "até o comando existir, o agile-coach confere com a última triagem"; some quando o cartão de `bin/forge-check` da 0.46 entrar. Esforço: P. Dono: tech-lead.

Cortes conferidos (diff c340c322..bad4f5aa):
- agile-coach: "sem burocracia que não gere decisão", "as duas de estabilidade pesam tanto quanto as de velocidade" e "mais de 30% de itens `delegado`" são orientação, não controle; ausentes de `invariantes` e sem ID de regra. A linha dos dois relógios mantém `D-4`, `relogios:` e a meta de 30 min.
- skill: saiu "Dois relógios" (continua no agile-coach, que é o dono da medição); vazão, idade do WIP e bloqueio foram só condensados, sem perda de definição. `R-WIP`, `R-DECISAO` e o resto seguem.
- Todos os trechos de `tests/config.json` `invariantes` para `agents/agile-coach.md` e `skills/kanban-scrum/SKILL.md` seguem presentes no head (conferido, 0 faltas).
- Texto novo: não afrouxa portão, não cria isenção nem dispensa parecer; manda atualizar o quadro e arquivar plano substituído.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados do head: tests.test_clareza, tests.test_sobreposicao_quadro, tests.test_medidas_m14b (OK). Sem ferramenta faltando para texto.
