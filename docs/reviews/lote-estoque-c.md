---
tipo: review
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-c
commit: e17d07ac96a4a48cbfdd8e079bfa8e35f966e9f4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review: junção do lote estoque C (versao-034, E2.2)

Escopo: só a junção (resolução de conflitos, commits fora dos merges, o que cada item trouxe). Os itens têm review e QA próprios e não foram relidos. Revisei até e17d07a; o f11234d (changelog.d consolidado, volta da E2.1) entrou depois e foi lido: só fragmentos.

## Os itens (`git log --first-parent d9b26bb..e17d07a`, 7 merges)
- forge-testes-filtro-k (a93a38e): entrou (bin/forge-testes, tests/test_testes_tocados.py, docs); `--remerge-diff` vazio, sem conflito.
- forge-testes-aviso-mapa (def197c): entrou (só docs de parecer e QA; o código do aviso já veio com o item anterior); sem conflito.
- forge-testes-sem-mapa (0e0a91d): entrou (só docs de parecer e QA); sem conflito.
- doutor-034 (dc5f542): entrou (hooks/doutor.py, tests/test_doutor.py, tests/test_qa_doutor_034.py, spec de mutantes); sem conflito.
- doutor-f8-caminho (289da2d): entrou (bin/forge-doutor, dois testes); sem conflito.
- lote-fechar2-guardas-v2 (e6fd0fb): entrou (dois testes, spec de mutantes, docs); sem conflito.
- hook-parecer-034 (14c5dea): entrou (hooks/parecer.py, docs/hooks.md, 7 casos de corpus, test_hooks_parecer_pasta); sem conflito.

Nenhum arquivo de código ou teste foi tocado por dois itens; a única sobreposição é bin/forge-testes (filtro-k e o ajuste e17d07a), em linhas diferentes. Sem duplicação nem contradição entre itens.

## Commits fora dos merges
- e17d07a: inclui test_qa_doutor_034 no mapa FORGE_CHECK de bin/forge-testes e sobe a contagem de tests/test_testes_tocados.py de 39 para 40. Correto: o módulo executa o bin/forge-check (importlib em test_qa_doutor_034.py:77) e o teste do mapa conta os módulos; o comentário registra a origem. Dois ajustes de uma linha, no mesmo comportamento da junção.
- f11234d: junta 7 fragmentos num só (changelog.d/lote-estoque-c.md), agrupado por seção; as 7 entradas dos itens estão presentes. Sobra README.md e o fragmento do ancestral, que já vinham da base.

## Testes dos módulos tocados
`python3 -m unittest` em test_testes_tocados, test_qa_doutor_034, test_doutor, test_doutor_protecao_gh, test_qa_doutor_f8, test_fechar_base_andou, test_fechar_espera_catraca, test_hooks_parecer_pasta: 256 testes, OK (193 s). A suíte inteira fica com o QA do lote (E2.5).

## Parecer
Aprovado: junção limpa, sem conflito a resolver, com um ajuste de integração correto. Ponto de atenção para o Jarvis e o E2.6, não bloqueante porque a decisão do dono de 2026-11-05 14:37 manda um PR por lote: o lote soma 519 linhas de código e teste e toca duas classes de hooks/ (parecer e doutor); o teto por PR não admite exceção em hooks/, então o `forge-check pr` pode recusar o PR e a saída seria dividir o lote ou levar a decisão ao dono (A1).

## Achados
- A1 (recomendado) hooks/parecer.py:1 · o lote tem 519 linhas de código e teste (teto 150) e duas classes em hooks/ (parecer e doutor), sem exceção possível; o E2.6 confere com `forge-check pr` e, se recusar, divide o lote ou pede decisão ao dono (R-DECISAO)
