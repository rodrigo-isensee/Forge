---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-zero-nao-medido
commit: 2cfb734c5d8e26e47cc794b4256c985a02aa7cd2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E147.3 (PR #834, nao-medido no lugar de 0)

Base 9d239dda, head revisado 2cfb734c. Diff: `bin/forge_voltas.py`, `bin/forge_governanca.py`, ajuda do `bin/forge-check`, testes em `tests/test_voltas.py` e `tests/test_governanca.py`, mutantes em `tests/mutantes/v0480-zero-nao-medido.json`, fragmento em `changelog.d/`. Cerca de 25 linhas de código, um comportamento: dentro do teto H1.

## Achados
- A1 (recomendado) bin/forge-check:63 · a ajuda diz que o metricas sai nao-medido "nas contagens do pedido sem item no Histórico", mas o resumo() vale também para o período sem item (o teste novo confere a linha `periodo`); cite o período na ajuda.

## Sondas

## Parecer
**Aprovado.**

- **Correção (voltas):** sem cartão com movimento, `voltas_do_cartao` recebe lista vazia, então `linhas` só traz tipo `brief`; o `contagem[tipo] += 1` nunca cai num `"nao-medido"` (string), e não há TypeError. Sem `--pedido`, o pedido sem linhas e sem relógio já era pulado pelo `continue`, então `nao-medidos=` só aparece com `--pedido` (um pedido só), e o ramo misto (medido e não medido no mesmo total) não ocorre. As linhas `tempo:` e `reversoes=` seguem saindo (teste novo).
- **Correção (metricas):** `resumo()` com `itens` vazio põe `None` nas 7 contagens; o texto passa todas por `_n`, que já devolve `nao-medido` para `None`. `tokens`, `reprovacoes_por_classe` e `merito_declarado` seguem medidos pelo registro, coerente com o pedido.
- **Consumidores (item do brief):** nenhum código lê as contagens do resumo de `voltas` nem `pedidos[]`/`periodos[]` do JSON do `metricas` além do próprio texto: `orcamento_de_tokens` lê só `tokens` (inalterado; `r.get("tokens") or 0`); `forge-placar` e `forge_dora.py` calculam por conta própria e só citam o `voltas` e o `metricas` em texto de ajuda; `agents/agile-coach.md`, `hooks/agentes.py`, `templates/projeto/docs/pedidos/_modelo.md` e `bin/forge_decisor.py` só mencionam os subcomandos; nenhuma skill (`kanban-metricas` incluída) analisa a saída (`grep` em bin, hooks, scripts, skills, agents, .github). Nada quebra com `nao-medido` nem com `null`.
- **Guardas e mutantes:** as 7 linhas de guarda do diff (forge_voltas.py 185, 186, 197, 207, 211, 213; forge_governanca.py 627) têm um mutante cada; `bin/forge-mutante tests/mutantes/v0480-zero-nao-medido.json` rodado aqui: 7 de 7 mortos. Os testes são de comportamento (saída do subcomando), não de leitura da fonte.
- **Testes do item:** `python3 -m unittest tests.test_voltas tests.test_governanca tests.test_metricas_texto tests.test_forge_dora` rodado aqui: 117 testes, OK (1 pulado). Suíte inteira: fica no CI do PR #834 (suítes pendentes na leitura; a `catraca` e a `bateria (pareceres)` falham por falta dos pareceres, o que este arquivo supre em parte); sem rerrodar.
- **Risco aceito:** o `pedidos=` do `total:` passa a contar só os medidos (declarado no PR, em "Riscos").
