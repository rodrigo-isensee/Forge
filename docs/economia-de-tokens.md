# Economia de tokens (política do time, 2026-10-10)

Pedido do usuário: gastar menos tokens sem perder qualidade. Medição na sessão: ~170 execuções de agente; `jarvis.md` (11,6 KB), skill `kanban-scrum` (8,9 KB) e `CLAUDE.md` (5,9 KB) são relidos a cada agente; a spec de UX (1.259 linhas) e o plano de QA (619) são relidos por vários agentes; revisões repetidas (r1, r2, r3) por pequeno delta.

## Regras
1. **Uma rodada por entrega.** Um code review, um QA e uma revisão de UX por entrega, não por commit. Correção pequena é conferida pelo autor com o teste que a cobre; o revisor só reabre se for regra de negócio ou componente compartilhado.
2. **Modelo certo para cada tarefa** (parâmetro `model` ao acionar): `haiku` para commit, merge, mover cartão, ajuste de texto; `sonnet` para implementar, testar e desenhar; `opus` só para decisão de arquitetura, para o review principal de cada entrega (inclusive o de segurança) e para bugs de regra de negócio. `sonnet` também revisa UX. Esta é a única definição da regra.
3. **Sem cerimônia desnecessária.** Quadro e histórico atualizados em lote, uma vez por entrega (o Jarvis, sem acionar o `agile-coach`); retrospectiva só no fim de cada pedido; reunião de melhoria só se algo deu errado.
4. **Leitura dirigida.** Prompt aponta arquivo e seção; agente não relê o documento inteiro. Especificações longas (UX, plano de QA) são divididas por tela ou módulo quando forem tocadas de novo.
5. **A máquina testa, não o agente.** Com o CI, lint, tipos, cobertura exigida no `praticas.md` do projeto e testes rodam no GitHub; o agente roda só o teste do que mexeu, não o comando de pronto completo várias vezes.
6. **Trabalho sob demanda.** Nenhum protótipo ou discovery novo sem pedido; documentação técnica atualizada uma vez por entrega pelo arquiteto, junto da própria mudança.
7. **Respostas curtas**: agente ≤ 5 linhas, Jarvis só o que decide ou depende do usuário.
8. **Sem duplicar**: antes de relançar um agente, checar se está ativo; um agente por arquivo.
