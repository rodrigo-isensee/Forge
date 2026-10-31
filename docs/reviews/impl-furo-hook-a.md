---
tipo: review
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a1
commit: e30cbd10157b4e595b11f892bf5f51abd081df6d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-furo-hook-a, branch a1 (A1 TESTE-MATRIZ-CRITICO)

Escopo: `234dbe0..e30cbd1` (base 234dbe0fb90b005450d7c2eb59e6241ea9779155), commits `88d7d67` (teste e spec de mutantes) e `e30cbd1` (fragmento). Revisor em instância diferente do autor (D-ETAPAS-INST = A).

## Item entregue
E1, item A1 TESTE-MATRIZ-CRITICO do pedido, pelo desenho `docs/propostas/lotes-1030/furo-hook.md` §2.4: o T6 `test_t6_a_leitura_ve_a_acao_sem_marcador_com_cada_variante` cruza as ações do corpus sem o marcador `CRITICO` do conformidade, e mais o merge reprovado do parecer, com `VARIANTES_QUE_O_BASH_IGNORA`. Ele roda pelo hook real (`executar_em_lote`) e exige saída 2 sem o texto da rede (`stderr_sem`, chave nova do fixture, documentada na docstring do módulo). As asserções estruturais do desenho estão lá: pelo menos 2 ações sem marcador, e `MECANISMOS_DO_COMENTARIO` contido nas variantes. Os mutantes m1 (laço da crase) e m2 (`atribuicoes +`) estão em `tests/mutantes/impl-furo-hook-a.json`, como manda §2.4(c).

## M14
Linhas que contam (`git diff --numstat --no-renames 234dbe0 e30cbd1`): só `tests/test_hooks.py`, com 26+1 = 27. A spec de `tests/mutantes/` e o `changelog.d/` ficam fora. São 27 linhas, abaixo do teto de 150, e não há mudança em `hooks/` nem em `PROTEGIDOS`. Há um comportamento só, o teste T6: cumpre.

## Conferido
- Rodado no HEAD revisado: `python3 -m unittest tests.test_hooks.Hooks.test_t6_a_leitura_ve_a_acao_sem_marcador_com_cada_variante` deu `Ran 1 test in 17.458s` e `OK`. A máquina estava com carga 15.
- Não refiz a mutação: o histórico do pedido registra que os 5 mutantes do lote morreram na E1.1.
- O teste não tira caso da matriz nem cria lista de pendentes, então nada afrouxa (§2.4 d). R-NEUTRO e R-CUSTO: nada a apontar.
- Não há `docs/engineering/praticas.md` no Forge, então não há regra de ferramenta a citar. Não houve shell tocado, e o shellcheck não se aplica.
- Commits em Conventional Commits, em português, com os trailers.

## Achados
- A1 (recomendado) tests/test_hooks.py:1850 · o desenho §2.4(d) pede que o autor meça o tempo do T6 e o registre no PR; registre a medida no corpo do PR (aqui foram 17,5 s com carga 15).

## Parecer
Aprovado. A branch entrega o A1 como o desenho pede e cumpre a M14. A recomendação não devolve.
