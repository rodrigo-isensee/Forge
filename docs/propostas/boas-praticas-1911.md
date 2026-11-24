# Boas práticas que faltam ao Forge (19/11/2026, Controlador, proposta ao dono)

Fontes:
- **Projeto em uso:** avaliação só de leitura de um projeto que usa o Forge desde 10/10, com 555 PRs.
- **Dados do próprio Forge,** de 16 a 19/11:
  - tempo por fase;
  - paradas;
  - rodadas de revisão.
- **Práticas de mercado,** pelo conhecimento do Controlador até meados de 2026. Esta parte não foi pesquisada de novo na web, porque o agente de pesquisa foi barrado pela R-BRIEF. Validar com fontes atualizadas antes de adotar o que estiver marcado (M).

Tudo neutro (R-NEUTRO) e sem custo em dinheiro (R-CUSTO), salvo indicação.

## Diagnóstico
1. **O que mais rouba tempo hoje são as paradas, não as entregas.** Em 30 horas no Forge houve:
   - 3 quedas da sessão;
   - develop vermelha 4 vezes por teste dependente de tempo ou carga;
   - promoção travada uma noite inteira;
   - um único teste instável segurando 4 PRs.
2. **As voltas de revisão:** 64% do tempo de cada item, com 3 rodadas típicas. No projeto, cerca de 48% das conferências de entrega deram "não cumpriu", muitas só por escopo ou faixa de arquivos declarada à mão.
3. **O registro do processo se descola do trabalho.** No projeto, o quadro da develop parou em 22/10, cerca de 200 commits de pedidos e retros ficaram numa branch nunca mesclada, e o cycle time ficou "não medido" em 6 retros seguidas.
4. **O produto foi construído sobre dado simulado por 3 semanas.** A primeira carga real coletou 0 itens, e 2 dos 10 escapes foram altos, no primeiro uso real.
5. **Identidade e segredos:**
   - todo merge aparece como a conta do dono, então não se separa agente de pessoa;
   - houve chave colada no chat;
   - commits com link de sessão foram para repositório que ficou público.

## Práticas propostas (ordem recomendada)
| # | Prática | Dor que resolve | Forge hoje | Custo |
|---|---|---|---|---|
| BP1 | **Quarentena automática de teste instável** com prazo e cartão (o teste é pulado, nunca apagado; o teto de pulados vale) e **relógio injetado** nos testes de tempo (testes herméticos) (M) | develop vermelha por teste alheio | não tem quarentena; varredura de testes de tempo em cartão | baixo |
| BP2 | **Fila de merge:** mescla em série, cada PR testado sobre a develop atual. A fila do GitHub exige repositório de organização; senão, a ferramenta de fechar faz a fila. O conserto da develop entra mesmo com ela vermelha, preso ao commit revisado (M) | merge com check pendente, develop vermelha, conserto que não entra | não tem | baixo/médio |
| BP3 | **Sessão durável:** o Jarvis roda sempre em `tmux` (padrão do atalho e do modelo de projeto) e, ao voltar, retoma sozinho os agentes interrompidos a partir de um registro por item | 3 quedas em 30 h com agentes perdidos | o atalho tem `tmux`, mas o uso no VS Code não; a retomada é manual | baixo |
| BP4 | **Brief gerado do estado real** (diff contra a base, arquivos pelo diff, `forge-check pr` antes de selar), nunca declarado à mão | 48% de "não cumpriu", ERRO-JARVIS, brief invertido | parcial (brief gerar compacto) | médio |
| BP5 | **Autorrevisão do autor** com a lista de achados recorrentes do papel e mutantes mortos antes da entrega (META85) | 3 rodadas por item | em andamento (META85) | baixo |
| BP6 | **Revisão por risco:** item pequeno com um parecer só, e segurança só com gatilho (META42) (M: ship/show/ask) | tempo de parecer em item trivial | caminho curto (H8) parcial | baixo |
| BP7 | **Critério de aceite executável:** o QA escreve os testes a partir do cartão antes ou em paralelo ao código; o autor entrega com eles verdes (M: spec-driven) | "teste não testa nada", desvio de escopo | não | médio |
| BP8 | **Capacidade em vez de lista de comandos:** o sandbox trava escrita e rede (A3 feita); os hooks deixam de barrar comando de leitura (`sort`, `uniq`, `$?`, `2>&1`, glob em leitura) | caça ao gato da segurança; atrito diário nos agentes de leitura | A3 feita; hooks ainda barram leitura comum | médio |
| BP9 | **Identidade separada para agentes** (conta de robô ou GitHub App com escopo mínimo; o `workflow` só sob pedido) | auditoria agente × pessoa; espera do dono por escopo | pendente com o dono | médio (sem custo em dinheiro) |
| BP10 | **Higiene de segredo:** varredura de segredo antes do commit (gitleaks já existe em projeto, como informativo), aviso quando uma chave aparece no chat e sem link de sessão em commit de repositório público | chave colada; repositório público | parcial | baixo |
| BP11 | **As 4 métricas DORA no placar automático** (lead time, frequência, falha de mudança, tempo para restaurar a develop), com o quadro movido pelos hooks de PR (aberto, review, QA, mesclado) e o registro do processo dentro da develop | "não medido"; quadro descolado | placar parcial; quadro manual | médio |
| BP12 | **Dado real cedo:** no discovery, uma prova de coleta real ou uma amostra anonimizada antes de qualquer painel com dado simulado; o QA não aprova teste de banco ou navegador que não rodou | retrabalho grande; escapes no primeiro uso | não | baixo |
| BP13 | **Atualização do Forge no projeto em lote,** com um parecer só e migração automática | 22 atualizações em 40 dias, cada uma com 4 pareceres | não | baixo |
| BP14 | **Retro com "pedido × não entregue"** (pedido parado, discovery sem código) | pedido com discovery pronto e nunca feito | não | baixo |
| BP15 | **Entrega de produto nos modelos:** preview por PR, feature flag, deploy com rollback e telemetria de uso (M) | homologação manual, flags improvisadas, nenhuma métrica de uso | skills parciais, sem modelo | alto (depois) |

## Ordem
1. **Agora, estabilidade:** BP1, BP2, BP3. Sem elas nenhuma meta de minutos se sustenta.
2. **Junto com a META85 e a META42:** BP4, BP5, BP6, BP7.
3. **Segurança e medida:** BP8, BP9, BP10, BP11.
4. **Para os projetos:** BP12, BP13, BP14; BP15 por último.

## Riscos
- **BP1** afrouxa enquanto o teste está em quarentena: precisa do OK do dono por teste e de prazo.
- **BP2** muda o merge: precisa do parecer de devops e de segurança.
- **BP8** mexe em controle: só com a confirmação escrita da segurança de que só deixa passar leitura.
