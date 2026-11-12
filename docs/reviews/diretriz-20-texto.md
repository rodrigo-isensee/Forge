---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/diretriz-20-texto
commit: bad4f5aaab7776ab2efaeec2c5e52c05b6ac3564
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E26.9, diretriz 20 no texto do agile-coach e da skill kanban-scrum)

Diff lido: `c340c322..bad4f5aa` (agents/agile-coach.md, skills/kanban-scrum/SKILL.md, changelog.d/diretriz-20-texto.md). Classe C por skill.

## Achados
- A1 (bloqueante) skills/kanban-scrum/SKILL.md:41 · afirma que `forge-check kanban` recusa destino divergente, mas o cmd_kanban (bin/forge-check:420) não lê triagem; a recusa é da E25.3. Sugestão: "até a E25.3 existir, o agile-coach confere o destino com a última triagem" (diretriz 20, item 2). Sonda S1
- A2 (bloqueante) skills/kanban-scrum/SKILL.md:43 · diretriz 20 (3) diz "plano ou pedido substituído"; o texto só cobre plano, e o mesmo corte aparece em agents/agile-coach.md:12. Requisito incompleto: incluir "pedido" nos dois lugares
- A3 (recomendado) agents/agile-coach.md:9 · o corte de "sem burocracia que não gere decisão" e de "por release" (linha 17) não aparece no brief nem no fragmento; declare no corpo do PR, junto com os outros cortes

## Sondas
- S1 · KANBAN.md do modelo com C-1 em Entrada e docs/kanban/triagem-2026-11-10.md dizendo "C-1: fechar"; `bin/forge-check --raiz <tmp> kanban` · espera: recusa do destino divergente · obtido: saída vazia, rc=0

## Parecer
Reprovado por A1 e A2.

- **Efeito da diretriz 20:** o item 1 (triagem aplicada no quadro) e o item 2 provisório (conferir com a última triagem, corrigir a divergência antes) estão no texto. O A1 mostra que a recusa do `forge-check kanban` está escrita como se já existisse. Hoje ela não existe, e o agente que confiar no texto vai pular a conferência do destino. O A2 é a metade "pedido" do item 3, que ficou de fora. A parte do `agents/jarvis.md` e do `forge-check kanban` fica na E25.3, fora deste diff.
- **R-NEUTRO:** o texto é neutro. Não cita projeto, nome nem stack, e `arquivo/` é genérico.
- **Cortes (nenhuma regra viva saiu):**
  - estabilidade com o mesmo peso que velocidade: continua em skills/kanban-scrum/SKILL.md:83;
  - dois relógios: continuam em agents/agile-coach.md:17, e a definição está na ajuda do `forge-check voltas` (bin/forge-check:53) e em tests/test_voltas.py;
  - "Mais de 30% de `delegado`": ninguém mais cita (grep em agents, skills, templates, docs/regras e tests);
  - vazão, idade do WIP e bloqueio: juntados num item, sem perda de definição.
- **Invariantes:** os de `tests/config.json` para os dois arquivos continuam presentes.
- **Ferramenta:** a partir de `bin/forge-testes --listar`, rodei os testes de texto e orçamento (test_orcamento_instrucao, test_forge, test_metricas_texto, test_textos_034, test_textos_dono_f10, test_textos_dono_f7, test_clareza, test_medidas_m14b, test_changelog, test_citacao). Resultado: 752 testes, 1 falha, `PesosDaSuite.test_no_maximo_20_por_cento_dos_modulos_sem_peso`, que vem da develop e não deste diff. Os orçamentos de texto passaram.
- **PA-7:** nenhum AR-1 a AR-12 alcança um diff só de texto. O A1 é de uma classe nova (texto descreve como existente uma trava que ainda não existe), por isso não entra linha AR.
- **Volta:** as correções de A1 e A2 cabem no mesmo orçamento: a do A1 troca a frase e a do A2 acrescenta "ou pedido".
