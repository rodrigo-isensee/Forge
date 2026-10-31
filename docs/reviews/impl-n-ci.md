---
tipo: review
contrato: 1
pedido: impl-n-ci
branch: melhoria/impl-n-ci-c3
commit: 4c978e7460e4cff62a1ab6d320d52bc3f4aae6c1
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-n-ci (c3)

## Achados
- A1 (bloqueante) scripts/suite-paralela.py:418 · c3 nasceu da base, não da c2: `git merge-tree 6098608 4c978e7` conflita em 2 arquivos, e o E2 inteiro (medida da c2 com veredito protegido) não existe em branch nenhuma. Refazer a c3 sobre a c2, com C-6 a C-8 valendo para as linhas da c2.
- A2 (bloqueante) tests/test_suite_paralela.py:288 · `assertNotIn("maior unidade", resumo)` é teste de ausência vazio: nesta árvore nada escreve "maior unidade". Sobre a c2, o FAILED tem de omitir soma, maior unidade, desequilíbrio e lentas (C-7), e o teste passa a provar isso.

## Parecer
Reprovado. Li o diff inteiro de `234dbe0` a `4c978e7` (3 commits) e o cruzei com a c2 (`6098608`).

O que entrega: a segunda metade do E2 do pedido (item 55 d), o veredito protegido (C-6 a C-8), pela divisão da DECISÃO TÉCNICA do Jarvis de 2026-10-30 15:39. O desenho da proteção está certo: o veredito é decidido e impresso antes do resumo, `fechar_verde` mantém pesos e carimbo só no verde, qualquer erro ao montar ou gravar o resumo vira `resumo indisponível` no stderr sem mudar o código de saída (captura ampla comentada e justificada), módulo sem duração é listado, e `orquestrar_no_processo` impede o brinquedo de escrever no resumo real do runner (C-10). Rodei `python3 -m unittest tests.test_suite_paralela` na worktree: `Ran 27 tests`, `OK`.

Por que reprova (requisito do E2 e defeito provado no teste): a divisão do Jarvis põe a medida na c2 e a proteção na c3, mas a c3 foi feita a partir de `234dbe0`, com um `montar_resumo` próprio, de outra assinatura, sem as linhas de medida. O merge das duas conflita em `scripts/suite-paralela.py` e `tests/test_suite_paralela.py`; resolver isso na hora do merge exige escrever lógica nova (o FAILED sem as linhas do orçamento da c2, a lista "sem duração" ao lado da "sem peso"), que nem o autor testou nem este review leu, e a integração não implementa (o integrador não escreve lógica). O A2 mostra o efeito: a asserção que devia provar o C-7 passa por vazio aqui e falharia sobre a c2 sem código novo. O parecer de devops viu o mesmo conflito como recomendação (A1 de `docs/devops/impl-n-ci.md`); aqui ele é bloqueante porque o E2 do pedido só fica entregue com as duas partes juntas.

Volta (Entregar): refazer a c3 sobre o head da c2 (ou sobre a develop depois do merge da c2), aplicando C-6 a C-8 ao `montar_resumo` da c2: veredito na primeira linha, FAILED sem soma, maior unidade, desequilíbrio e lentas, "sem duração" junto de "sem peso", e o `::group::` com os módulos mantido; manter os testes de C-6, C-8 e C-10 e tornar o do C-7 uma prova real. Recontar a M14 sobre o diff da nova c3 contra a c2.

M14 (agents/tech-lead.md, Teto por PR): esta versão cumpre, por pouco. Contam 149 linhas (`scripts/suite-paralela.py` 48, `tests/test_suite_paralela.py` 101); o fragmento de `changelog.d/` fica fora. Sem `hooks/` nem `PROTEGIDOS`; um comportamento (o veredito protegido). Refeita sobre a c2, a contagem muda; acima de 150 divide de novo ou traz a linha de exceção no corpo do PR.

Ferramentas: sem `docs/engineering/praticas.md` com regras por ferramenta no Forge; a suíte roda no pre-push e no CI do PR. Segurança (E1.3) é parecer à parte.
