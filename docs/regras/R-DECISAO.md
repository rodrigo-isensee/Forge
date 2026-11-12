---
id: R-DECISAO
titulo: Decisões do dono uma a uma, com opções e recomendação, sem prazo que decida
verificada_por: `forge-check brief selar` (corte de escopo); vigia (`entrada-sem-registro`); revisão; retrospectiva (linhas `MELHORIA:`)
---
# R-DECISAO: Decisões do dono uma a uma, com opções e recomendação, sem prazo que decida

Propósito: texto único desta regra. Público: o time.

Revisar em: 2027-01-07
Medida: decisões aplicadas sem resposta do dono (meta 0) e espera por decisão

- Vai ao usuário: produto, escopo, prioridade, regra de negócio, custo, acesso, exceção a regra, mais tokens ou tempo de entrega. Decisão técnica é do time.
- **Uma por vez:** uma decisão por mensagem, a de maior peso primeiro; a próxima espera. Cada uma com o contexto, **as opções** (prós e contra, se afrouxa o processo, o tempo e os tokens a mais ou a menos, marcados `medido`, `estimado` ou `não medido`, e se esse custo fica maior ou menor que o das outras opções) e **a recomendação** com o motivo. Toda opção traz o custo em tokens e o ganho de velocidade. Toda decisão traz a origem do item (pedido, análise, cartão ou decisão anterior).
- **Decisão ruim não passa calada, nem a do dono:** antes de cumprir, confira: deixa o Forge mais rápido, seguro ou barato, ou mede algo? Se não, ou se soma regra ou trava sem ganho medido, leve ao dono. Leve a origem, a evidência, o custo de seguir e de não seguir e uma alternativa. Confirmada, cumpra e registre "decisão contra a recomendação".
- **Sem prazo vencido:** nenhuma decisão do dono é aplicada por prazo; sem resposta, fica pendente.
- **Corte de escopo é explícito:** a marca "Retira do escopo original", o trecho do pedido, o motivo, a consequência e a decisão do usuário; o pedido ganha "Fora do escopo". Item que some sem a marca reprova (`corte: sem marca`; `pendente:` no review).

## Complemento: o que é bloqueante e de onde vem a recomendação
- **Teste de bloqueante:** vai ao usuário só a dúvida com leituras de resultado bem distinto, que o projeto não resolve e que custa caro desfazer. Senão, vira "Suposições" (base, `muda com`, `custo de reverter`).
- **Decisão óbvia:** `forge-check decisoes registrar`.
- **O teste não se aplica** a custo, acesso, exceção a regra nem a fato de negócio declarado.
- **Escada da recomendação:** o que o usuário disse, fato do projeto, regra ou ADR, prática da fábrica, preferência do time.
- **Decisão só vale gravada:** pedido, lista ou decisão do dono vai ao pedido ou ao quadro no mesmo turno; a fala vai literal por `forge-check pedido fala --gravar` e é lida antes de perguntar de novo. Proposta aprovada leva a versão nomeada (`versão: X.Y`). Versão cheia passa para a seguinte com vaga.

## Complemento: "tanto faz" e ordem ampla
- "Tanto faz" e "decidam vocês" viram item `delegado`. Esses nunca são delegáveis assim: custo, acesso, aceite de risco, rótulo, merge na main, exceção a regra (`R-CONFORMIDADE`) e ato irreversível.
- **Ordem ampla não confirma:** "resolva" e "pode fazer" só cobrem o que já é `confirmado` ou `delegado`. Item `técnico` não depende de ordem. `Suposição` e `no-protótipo` seguem fora da ordem ampla.

## Complemento: melhoria vista e entrada direta
- **(a)** Todo relatório termina com `Melhoria vista:` (problema, evidência, mudança) ou `nenhuma`; não se inventa melhoria para preenchê-la.
- **(b)** O Jarvis a grava como `MELHORIA:` no pedido e a retro a classifica.
- **(c) Entrada direta**, sem perguntar: não custa dinheiro real, sem exceção; não é afrouxamento; não é decisão de produto; não aumenta tokens nem tempo de entrega.
- **(d) Afrouxamento** é a mudança que faz a qualidade medida cair ou tira controle sem medida. Simplificar sem queda da qualidade medida **não é afrouxamento**.
- **(e) Evoluir sem piorar:** a retrospectiva escolhe no máximo 1 causa nova pelo `forge-placar` e a corrige de preferência em código ou eval; texto só para julgamento. Toda mudança declara a métrica e a data de revisão (`forge-placar comparar` mantém ou reverte). Regra nova só com medida e diz qual sai no lugar dela.

## Complemento: painel "Aguardando o dono"
- Cartão cuja próxima ação é do usuário vai a `## Aguardando o dono` do `KANBAN.md` por `forge-check movimento`, com a Obs. `origem: <coluna>; ação: <o usuário faz>; comando: <literal ou —>; destrava: <itens>`. O comando tem um efeito, sem segredo; decisão, rótulo e aceite levam `comando: —` com `decisão: <pedido>`. O Jarvis lista o painel ao fim de cada lote.
