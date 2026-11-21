---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae4-ordens
commit: 18d6d2f4d2afd939cf66ca5f22bc3c7a2a87c8f6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-ae4-ordens (AE4.1, etapa E58.72)

Escopo: diff `821db42e..18d6d2f4` (`bin/forge-check`, `bin/forge-testes`, `agents/jarvis.md`, `tests/test_ordens.py`, `tests/test_anotar.py`, mutantes, pesos, changelog). Novo subcomando `forge-check ordens` (só leitura, rc 0) e `anotar --tipo ordem` passa a exigir `--cartao <ID|E<n>>`, conferido por `recusa_do_apontador` (`bin/forge-check:5028`) contra o KANBAN.md da raiz do pedido e o `## Etapas` do pedido, e grava `· cartão: <ID>` na linha.

## Gatilhos
Gatilhos: controle do Forge (guarda de gravação do registro do dono no `bin/forge-check`), mudança no `bin/forge-check` sujeita à catraca `afrouxa-regra`.

## Só aperta (confirmação escrita para a catraca)
Confirmo por escrito: a mudança **só aperta**. Não há caminho que antes era recusado e agora passa.
- `anotar` de `decisao`, `pergunta` e `historico`: a nova condição `(tipo == "ordem") != (cartao is not None)` (`bin/forge-check:5062`) é falsa sem `--cartao`, e os outros blocos novos estão sob `tipo == "ordem"` (`:5080`, `:5098`); comportamento idêntico ao da base. `--cartao` com outro tipo é recusado (rc 2).
- `anotar --tipo ordem`: antes gravava qualquer ordem; agora só grava com apontador no formato fechado (`APONTADOR`, ASCII, `fullmatch`) e conferido; a única mudança na linha gravada é o sufixo `· cartão: <ID>` vindo do formato fechado.
- `decisoes` (com e sem `--sem-cartao`): o refactor usa parâmetros padrão iguais aos de antes (`linhas_de_decisao`, `registro_da_frase`, `linhas_sem_cartao(etapas=None)`). Saída byte a byte igual entre base e head em três leituras do registro real (só leitura): `decisoes --pedido v0478`, `decisoes --pedido v0478 --sem-cartao`, `decisoes --sem-cartao --desde 2026-11-15` (`cmp` igual nas três).
- `ordens` é novo, só leitura, rc sempre 0 e informativo (nenhum portão o lê); a saída passa por `sem_controle` e o ID impresso vem de regex de formato fechado.

## Achados
- A1 (recomendado) bin/forge-check:5033 · KANBAN conferido por is_symlink e depois aberto seguindo link (quadro_por_coluna, :4512): troca link/arquivo no meio passou 12 de 60 vezes; FIFO no lugar do KANBAN trava o anotar. Abrir uma vez com O_NOFOLLOW, exigir arquivo regular (fstat) e teto de bytes.
- A2 (recomendado) bin/forge-check:5039 · o cartão do KANBAN não é conferido contra o pedido: ordem do pedido X aceita cartão aberto do pedido Y (sonda O, rc 0). Exigir que a coluna Pedido do cartão seja o pedido anotado, ou registrar o aceite disso no desenho AE4.

## Sondas

## Detalhe dos achados
Sondas rodadas em fixture própria (`/root/.forge-contrib/wt/sec-E5872-sondas/`, KANBAN e pedido de `tests/test_ordens.py`), forge-check do head, ambiente limpo, sem tocar a pasta de controle (`git status` dela vazio ao fim; nenhum `docs/pedidos/ordens-teste.md` lá). Resultado do pedido do brief:
- **ID parecido:** `ABC-10`, `ABC-1-2` recusados (fora do KANBAN; a conferência é por igualdade, não por família); `ABC`, `abc-1`, `ABC-1 ` (espaço), `АBC-1` (A cirílico), `ABC‐1` (hífen Unicode) e `ABC-1 · cartão: E1` recusados pelo formato; `E1.1b`, `E1.10`, `E11`, `E01.1`, `E١.١` (dígitos não ASCII) recusados (fora do `## Etapas`).
- **Fechado sem entrega:** `FECH-1` recusado; cabeçalho `## Fechado sem entrega (3)` e `## Fechado Sem Entrega` também. Passam `## Fechado sem entrega — arquivado` e `## **Fechado sem entrega**`, e o cartão duplicado em outra coluna: exigem editar o KANBAN, cujo nome de coluna é o da fábrica; sem caminho de ataque além de quem já escreve o quadro, fica como dimensão da matriz, sem achado.
- **Etapa de outro pedido:** `E2.1`, `E9.9` e `E5` (com `E51.1` no pedido) recusados; a etapa vem só do `## Etapas` do próprio pedido lido antes da gravação.
- **KANBAN trocado:** link recusado (teste existente), diretório recusado (ilegível), ausente recusa o ID e aceita a etapa. Troca contínua link/arquivo durante 60 chamadas: 12 gravaram com o cartão lido pelo link (A1).

A1 · evidência `bin/forge-check:5033` (checagem) e `:4512` (`read_text` segue link) · caminho: um processo com escrita na raiz do pedido troca KANBAN.md por link entre a checagem e a leitura, ou põe um FIFO (o `anotar` fica parado até o tempo do chamador) · severidade baixa: quem consegue isso já escreve o KANBAN e poderia pôr o cartão direto, então não há ganho de privilégio; é a promessa "link não confere" que não vale sob corrida, e um travamento local · correção mínima: em `recusa_do_apontador`, abrir com `os.open(..., O_RDONLY|O_NOFOLLOW|O_NONBLOCK)`, `fstat` regular, teto de bytes, e passar o texto lido a quem monta o quadro (sem segunda abertura) · esforço P · dono: tech-lead (autor do AE4.1).

A2 · evidência `bin/forge-check:5039` (só a coluna ID é comparada) · caminho: o Jarvis, por engano, anota a ordem do pedido X com o cartão aberto do pedido Y; o `ordens` conta `com-cartao` e a auditoria AE6 não acusa ordem sem cartão do próprio pedido · severidade baixa (integridade do registro, sem atacante externo) · correção mínima: recusar quando `id_do_pedido(c[2])` difere do pedido anotado, ou registrar no desenho AE4 que o cartão de outro pedido vale · esforço P · dono: tech-lead.

Casos de abuso do desenho AE4.1 (`docs/propostas/v0479-melhorias-anti-erro.md`, tabela, linha AE4.1): `--cartao` inventado (`test_cartao_inventado_e_recusado`, `test_etapa_inventada_e_recusada`) e cartão fechado sem entrega (`test_cartao_fechado_sem_entrega_e_recusado`): cobertos.

## Suíte e ferramentas
Sem PR e sem CI no head (o brief pede sem suíte local). Rodei os testes do item e os que tiram dúvida do refactor: `tests.test_ordens tests.test_anotar tests.test_decisoes tests.test_forge_dono`, 121 testes OK com `TMPDIR` numa pasta própria com git próprio. Com `TMPDIR` dentro da pasta de controle, 5 falham porque `raiz_principal` sobe ao repositório da pasta de controle e lê o KANBAN real (ambiente, não defeito do item; ver o relatório). Ferramentas: leitura estática, sondas locais, `cmp`. Riscos aceitos: nenhum.
