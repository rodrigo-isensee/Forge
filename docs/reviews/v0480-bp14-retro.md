---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-retro
commit: dbc33e5ab8c11b08e9f14faee40f78e64aa8baeb
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E145.2, PR #833, BP14: tabela pedido × não entregue na retro)

Base `0ed441e9`, head revisado `dbc33e5a`; diff de 3 arquivos (+7/-1): `skills/kanban-metricas/SKILL.md`, `templates/projeto/docs/retrospectivas/_modelo.md` e o fragmento `changelog.d/v0480-bp14-retro.md`.

## Achados
- A1 (bloqueante) tests/test_retro_pendentes.py:115 · o modelo de `templates/` mudou e o gêmeo `docs/retrospectivas/_modelo.md` não; o teste que exige os dois iguais falha no head (reproduzido). Aplicar a mesma mudança nos dois modelos.
- A2 (bloqueante) templates/projeto/docs/retrospectivas/_modelo.md:11 · a tabela de exemplo fora de comentário conta como corpo da seção 1: retro com a seção 1 sem preencher passa a cobrir a versão no `retro --pendentes` (AE5.1; sonda S1). Pôr a linha de exemplo no comentário HTML.
- A3 (recomendado) templates/projeto/docs/retrospectivas/_modelo.md:11 · a skill manda a linha `nenhum` quando não há pedido parado; o modelo não diz; citar no comentário da seção 1.

## Sondas
- S1 · modelo do head com `Cobre: v1.0.0`, seções 2 a 4 com uma linha e a seção 1 intacta, em `versoes_que_a_retro_cobre` · espera: secao sem corpo: dados do pedido; nao cobre · obtido: ({'v1.0.0'}, []) (o modelo da base dá o aviso esperado)

## Parecer
Reprovado. O item segue o BP14 de `boas-praticas-1911.md` (pedido parado e discovery sem código), a marca usa os valores de `R-DECISAO` e o texto é neutro (`R-NEUTRO`). Orçamento da skill `kanban-metricas`: 45 linhas, teto 133 (`limite_linhas.skill`), sem linha nova. Fragmento de changelog presente.

Testes dos arquivos tocados (`test_retro_pendentes`, `test_jarvis_nucleo`, `test_reval_delta`, `test_medidas_m14b`): 146 rodados, 1 falha (A1). CI do PR #833 no head ainda pendente na hora do parecer.

Correção sugerida, uma só para A1 e A2: a tabela de exemplo entra dentro do comentário HTML da seção 1 (com a linha `nenhum` do A3), e o mesmo texto vai para os dois `_modelo.md`; o teste `test_modelo_preenchido_cobre_e_os_dois_modelos_sao_iguais` volta a passar e o `retro --pendentes` volta a cobrar a seção 1.
