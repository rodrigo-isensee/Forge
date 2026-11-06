---
tipo: review
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-c
commit: 78cfa461c5cb23887a6d498f4ce988554c6ffedf
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
- f11234d: junta 7 fragmentos num só (changelog.d/lote-estoque-c.md), agrupado por seção; as 8 entradas dos 7 itens estão presentes. Sobra README.md e o fragmento do ancestral, que já vinham da base.
- Volta 1 (consolidação, f11234d): os 7 fragmentos removidos (doutor-034, doutor-f8-caminho, forge-testes-aviso-mapa, forge-testes-filtro-k, forge-testes-sem-mapa, hook-parecer-034, lote-fechar2-guardas) somam 8 entradas; comparei os pares seção e entrada do pai de f11234d com changelog.d/lote-estoque-c.md: os 8 iguais, texto byte a byte, sob os mesmos títulos (Corrigido 3, Adicionado 4, Alterado 1). Nada perdido nem mudado; o veredito não muda.
- Volta 2 (junção da develop 30b4453, L09, em 78cfa46): delta lido = `git show --remerge-diff 78cfa46` (um conflito, tests/test_testes_tocados.py:61) e `git diff 8a7612b 78cfa46 -- bin/forge-testes tests/test_testes_tocados.py`; já lido: o resto do lote até f11234d, e o lado da develop tem pareceres próprios (docs/reviews/lote-l09.md). bin/forge-testes juntou sem conflito com os dois lados: test_qa_doutor_034 (lote C, linha 72) e test_qa_lote_l09 (develop, FORGE_CHECK linha 76 e LEITORES_DE_TEXTO linha 82); FORGE_CHECK tem 41 entradas, 41 distintas, logo a contagem 41 do conflito (40 de cada lado com a mesma base 39, mais um de cada) está certa e o comentário cita as duas origens. `python3 -m unittest tests.test_testes_tocados tests.test_qa_lote_l09`: 97 testes, OK (29 s); a suíte inteira do push (2652 testes OK) fica com o QA. O veredito não muda.

## Testes dos módulos tocados
`python3 -m unittest` em test_testes_tocados, test_qa_doutor_034, test_doutor, test_doutor_protecao_gh, test_qa_doutor_f8, test_fechar_base_andou, test_fechar_espera_catraca, test_hooks_parecer_pasta: 256 testes, OK (193 s). A suíte inteira fica com o QA do lote (E2.5).

## Parecer
Aprovado: junção limpa, sem conflito a resolver, com um ajuste de integração correto. Ponto de atenção para o Jarvis e o E2.6, não bloqueante porque a decisão do dono de 2026-11-05 14:37 manda um PR por lote: o lote soma 519 linhas de código e teste e toca duas classes de hooks/ (parecer e doutor); o teto por PR não admite exceção em hooks/, então o `forge-check pr` pode recusar o PR e a saída seria dividir o lote ou levar a decisão ao dono (A1).

## Achados
- A1 (recomendado) hooks/parecer.py:1 · o lote tem 519 linhas de código e teste (teto 150) e duas classes em hooks/ (parecer e doutor), sem exceção possível; o E2.6 confere com `forge-check pr` e, se recusar, divide o lote ou pede decisão ao dono (R-DECISAO)
