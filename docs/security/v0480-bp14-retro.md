---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-retro
commit: dbc33e5ab8c11b08e9f14faee40f78e64aa8baeb
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E145.4, BP14 tabela pedido x não entregue, PR #833)

Lido o diff inteiro `0ed441e9..dbc33e5a` (3 arquivos: `changelog.d/v0480-bp14-retro.md`, `skills/kanban-metricas/SKILL.md`, `templates/projeto/docs/retrospectivas/_modelo.md`).

Gatilhos: modelo de projeto copiado pelo `bin/forge-init` (`templates/projeto/`), portão `forge-check retro --pendentes` (`bin/forge-check:6069-6085`) que lê as seções desse modelo.

## Só aperta ou neutro, por escrito
- `skills/kanban-metricas/SKILL.md:34`: **neutro**. Só pede uma tabela a mais na seção 1 da retro; não toca regra, permissão nem portão.
- `changelog.d/v0480-bp14-retro.md`: **neutro** (fragmento de changelog).
- `templates/projeto/docs/retrospectivas/_modelo.md:11-13`: **afrouxa**. O portão da retro (`bin/forge-check:6080-6085`) conta como corpo de seção toda linha não vazia que não começa por `<!--`. A tabela-modelo entra fora do comentário, então a seção 1 de uma retro copiada do modelo e não preenchida passa a ter corpo: a retro cobre a tag sem nenhum dado do pedido (sonda S1). Antes do PR, a mesma cópia saía `secao sem corpo: dados do pedido` (o teste `test_retro_so_com_o_cabecalho_do_modelo_nao_cobre` prova isso sobre o modelo da raiz, que o PR não mudou).

## Achados
- A1 (bloqueante) templates/projeto/docs/retrospectivas/_modelo.md:11 · tabela-modelo fora do comentário HTML conta como corpo no portão da retro (bin/forge-check:6080): retro com a seção 1 só copiada do modelo cobre a tag (S1). Correção: descrever a tabela dentro do comentário de uma linha (:9), sem linha de tabela solta.
- A2 (bloqueante) docs/retrospectivas/_modelo.md:8 · o modelo da raiz não ganhou a tabela e diverge do de templates/projeto: tests.test_retro_pendentes.RetroPendentes.test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais falha no head (S2). Correção: os dois modelos com o mesmo texto.

## Sondas
- S1 · retro gravada a partir de templates/projeto/docs/retrospectivas/_modelo.md com Cobre: v0.1.0, v0.2.0, seções 2 a 5 com texto e a seção 1 só com a tabela-modelo, em forge-check retro --pendentes · espera: secao sem corpo: dados do pedido; nao cobre · obtido: código 0, retro: pendentes=0, sem aviso
- S2 · python3 -m unittest tests.test_retro_pendentes tests.test_medidas_m14b no head dbc33e5a · espera: OK · obtido: FAILED (failures=1), test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais; no 0ed441e9 o mesmo teste dá OK

## Detalhe dos achados
- **A1.** Evidência: `templates/projeto/docs/retrospectivas/_modelo.md:11-13`, `bin/forge-check:6080` (`not linha.strip().startswith("<!--")`). Caminho: o agente que escreve a retro (ou que quer fechar `retro --pendentes` sem fazer a retro) copia o modelo, escreve uma linha nas seções 2 a 5 e deixa a 1 como está; o portão aceita e a tag sai da lista de pendentes sem dados do pedido. Não é ataque externo: é contorno de um controle de processo da fábrica (`R-CONFORMIDADE`), aberto pelo próprio modelo que todo projeto recebe. Severidade: baixa (controle de processo, sem segredo nem dado pessoal), bloqueante porque o item tinha de ser só aperta ou neutro e o afrouxamento está provado. Correção mínima: tirar as três linhas da tabela do corpo e pôr a descrição dela no comentário de uma linha da seção 1 (`:9`), por exemplo acrescentando "Mais a tabela pedido × não entregue (Pedido, Situação: parado ou discovery sem código, Idade, Marca `medido`/`estimado`/`não medido`); sem nenhum, `nenhum`." Comentário de várias linhas não serve: o portão só ignora a linha que começa por `<!--`. Esforço: P. Dono: agile-coach (autor de E145.1).
- **A2.** Evidência: `docs/retrospectivas/_modelo.md:8-9` sem a tabela; `tests/test_retro_pendentes.py:113-115` exige os dois modelos iguais. Defeito provado (o CI do PR fica vermelho). Severidade: baixa. Correção mínima: aplicar no modelo da raiz a mesma mudança de A1, deixando os dois arquivos idênticos. Esforço: P. Dono: agile-coach.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: leitura do diff e de `bin/forge-check:6069-6090`; no head, `python3 -m unittest tests.test_retro_pendentes tests.test_medidas_m14b` (93 testes, 1 falha, S2) e o mesmo teste com o modelo da base (OK); a sonda S1 é uma subclasse de `RetroPendentes` no rascunho da sessão, fora do repositório. A suíte inteira não rodou (o brief pede sem suíte local); vale o CI do PR #833.
