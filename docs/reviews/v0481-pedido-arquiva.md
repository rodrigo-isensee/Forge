---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 687d97c8209f6e66cd813ce05f44423b6fb0ff87
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E9.2, #874, pedido que se arquiva sozinho antes do teto)

Diff de 8d7914bc a 687d97c8: `bin/forge-check` (+81), `bin/forge_tamanho.py` (margem de 0.9 para 0.8), testes em `tests/test_brief_tamanho.py` e `tests/test_forge_tamanho.py`, mutantes em `tests/mutantes/v0481-pedido-arquiva{,-2,-3}.json` (8 + 8 + 2) e o fragmento do changelog. Classe C (o `forge-check` e o `forge_tamanho.py` são controles).

## Achados
- A1 (bloqueante) bin/forge-check:8060 · Etapa aberta é arquivada: `entregue` ou `=aprovado` em qualquer linha do Histórico que cite o id a fecha, e o Jarvis escreve "X entregue (E7.1); review (E7.3) despachado" (v0481, linhas de 20:00 e 20:07). O --cobre da aberta some (S1). Feche só pela etapa da linha.
- A2 (bloqueante) bin/forge-check:7679 · Deixa de barrar o que barra hoje: `etapas_citadas` e o papel errado só olham `pedido["etapas"]`; o brief que delega E1.2 e cita a etapa fechada E1.1 de outro papel reprova antes e passa depois do arquivamento (S2). Use `ids_de_etapa` e o papel do arquivo.
- A3 (recomendado) bin/forge-check:8070 · `etapas_fechadas` lê o pedido antes da trava e as linhas movidas saem do texto relido sob ela; hoje só cresce o conjunto, mas a leitura das fechadas sob a mesma trava evita a corrida com o `anotar`.

## Sondas
- S1 · Histórico "item entregue no #1 (E1.1); review (E1.2) despachado" e "docs/qa/x.md=aprovado (E1.3); segurança (E1.4) despachada" · espera: só E1.1 e E1.3 fechadas · obtido: E1.1 a E1.4 arquivadas; --cobre E1.2 "não existe em ## Etapas do pedido"
- S2 · sonda_v0481.py: conferir_corte de Entregar "(E1.1)" e "(E1.2)", destino tech-lead, antes e depois de arquivar E1.1 entregue · espera: junta delegações e papel errado nos dois · obtido: antes 2 reprovas (junta delegações, papel errado E1.1); depois nenhuma

## Parecer
Reprovado. O desenho é bom e enxuto: o Histórico e as `DECISÃO DO DONO` ficam intactos (o teste confere `etapas_conferidas`, `entregas_conferidas` e `ultimos_do_historico` iguais antes e depois), as citações e o apontador `--cartao` passam a conhecer as arquivadas por `ids_de_etapa`, a escrita do pedido segue a mesma trava `flock` do `gravar_no_historico`, o arquivo vai para fora do glob de `docs/pedidos/*.md` e a etapa de várias linhas fica no pedido. A margem de 0.9 para 0.8 só avisa mais cedo; o teto do selar não muda.

Dois pontos pedidos no brief não fecham:

- A1, nenhuma etapa aberta é arquivada: `etapas_fechadas` herda o estado heurístico do `proximo` (`entregue` em qualquer linha que cite o id, `etapas_do_proximo`), feito para mostrar, não para mover. O Histórico real do v0481 tem a forma que o derruba (G2.0 entregue com "review (E6.2) despachado"; G4 com E7.1, E7.2 e E7.3 na mesma linha). Arquivada, a etapa aberta some do `proximo` e o `brief gerar --cobre` dela falha (S1). Sugestão: a fonte de verdade é a `entrega conferida` do brief selado (`etapas_conferidas`), o PR mesclado da `[branch]` e, para parecer, o `=aprovado` cujo primeiro id entre parênteses é a etapa; teste com a linha de duas etapas.
- A2, nada que barra hoje deixa de barrar: `conferir_corte` passou a aceitar o item de escopo só com arquivadas, mas o "junta delegações" e o "papel errado" (`bin/forge-check:7679` e `:7683`) seguem só nas vivas; depois do arquivamento, o Entregar que cita uma etapa fechada de outro papel junto da coberta passa (S2). Sugestão: guarde o papel das arquivadas (o arquivo tem a linha inteira) e confira as duas regras sobre vivas e arquivadas, com teste do ramo de falha.

Ferramentas: `tests.test_brief_tamanho` rodado aqui no 687d97c8, 13 testes OK. CI do #874 no head: "bateria (pareceres)" e "catraca" vermelhos pela falta dos pareceres da classe C (R-CONFORMIDADE, `bin/forge-check` sensível), suíte pendente na leitura; não rerrodei a suíte. Mutantes: 18 declarados, o autor relata 18 mortos; a volta declara os das guardas novas de A1 e A2. Segurança (E9.4): o caminho do arquivo vem de `caminho_do_pedido` e a pasta `arquivo/` não é conferida contra link; deixo a decisão ao parecer de segurança, sem refazer.

Medida do item (tempo por item, sem troca de pedido no meio): não muda até A1 e A2 fecharem.
