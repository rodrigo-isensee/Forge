---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-parte2
commit: 65cf916b96d6bfa7e0acb7472bfe21b2c7b91551
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047-jarvis-parte2

Code review da E4.2 (classe C) no head 1c3e34f2: diretrizes 2, 11 e 16 na `R-WIP` e nas skills `trabalho-em-paralelo` e `kanban-scrum`.

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/SKILL.md:16 · o corte tirou "cada uma com worktree e cartão"; o cartão próprio segue na `R-WIP`, então só vale lembrar que a skill ficou mais curta que a regra.

## Sondas

## Parecer
Aprovado. Diff de 5 arquivos (46 inserções, 16 remoções), sem código de controle: nenhuma guarda nova, sem mutante a declarar.

- Nenhuma regra nem invariante sumiu. Os cortes são só de redação (a âncora `anti_duplicacao.excecoes`, "AV5", "pedido do usuário", reescritas de frases iguais). Os padrões de `invariantes` de `docs/regras/README.md`, `skills/kanban-scrum/SKILL.md` e `skills/trabalho-em-paralelo/SKILL.md` seguem casando (`RegrasInviolaveis` verde). Os limites de coluna, o teto ÷ 3, o `R-TETO` inteiro e o "quem implementou não faz o review" estão intactos.
- Links válidos: as 5 âncoras de `R-LIMITES.md#...` viraram `R-LIMITES.md`, que existe; não sobrou referência a `R-LIMITES.md#` fora do parecer de segurança antigo do v0457, que é histórico. Perde-se só o salto à seção, sem link quebrado.
- As três diretrizes estão no texto com medida (propostas de abandono zero, conflitos por merge, vagas livres com fila parada). A skill `trabalho-em-paralelo` muda de "CI verde entra na hora" para "entrega conferida entra por PR próprio, com CI verde": a condição (CI verde) permanece, a forma (PR próprio, sem junção de frentes) é a diretriz 16 e bate com o `R-FLUXO`.
- Teste `DiretrizesDoDonoNaRWip` lê texto da fonte, o que cabe aqui porque o produto é o próprio texto da regra; ele pega a perda de qualquer das três frases.
- Núcleo do Jarvis: `agents/jarvis.md` não mudou neste diff (7958 bytes); o teste de orçamento passou.
- Execução (sem PR aberto, só os afetados): `DiretrizesDoDonoNaRWip`, `RegrasInviolaveis`, `AntiDuplicacao`, `RegrasComId`, `Orcamento`, `NeutralidadeDoNucleo`: 15 testes OK em 5 s, ambiente limpo, `python -I`.

## Revalidação (delta 1c3e34f2..65cf916b, E3.19)
Lido só `forge-check parecer delta`: `skills/kanban-scrum/SKILL.md`, `skills/trabalho-em-paralelo/SKILL.md` e `tests/test_reval_delta.py` (a junção com a develop fica fora do domínio).
- Aprovado. Nenhuma regra saiu: o corte da kanban-scrum junta as métricas de vazão, idade do WIP e bloqueio em uma linha, e tira só o texto dos "dois relógios (D-4)"; a medida segue em `forge-check voltas` e em `tests/test_voltas.py`, sem teste nem invariante que leia essa frase da skill. A trabalho-em-paralelo perde só redação ("serializam", "gargalo", "podem"); o PR abre com pareceres aprovados (E1.34, `R-FLUXO`). O que a kanban-scrum ganha (triagem, destino divergente) é adição.
- A2 (recomendado, E3.15) skills/trabalho-em-paralelo/SKILL.md:16 · segue o A1: skill mais curta que a regra, aceito.
- Lista do `test_reval_delta`: `tests/test_forge.py` passa a 15 citações de `README.md` (linha da R-WIP), coerente com a regra; sem guarda nova nem mutante.
- Campo `pedido:` corrigido para `v047` (instância que não fez a entrega).
- Execução (sem PR, só afetados, `python -I`, ambiente limpo): `test_reval_delta` 10 OK; `test_jarvis_nucleo` 17 OK; `RegrasInviolaveis`, `AntiDuplicacao`, `Orcamento` 7 OK.
