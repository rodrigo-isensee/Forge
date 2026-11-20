---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 481537335abefb88ae3b221960890585884a4ef1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E50.2 (ENTREGA-PARECER-MESCLADO-ANTES-DO-AUTOR)

Escopo lido: `git diff 8a503799..48153733` (bin/forge-check +38 -1, changelog.d, tests/test_selo_e_entrega.py, tests/mutantes/ com M1 a M11). Código dentro do teto (H1): cerca de 37 linhas, um comportamento.

## Achados
- A1 (recomendado) bin/forge-check:3020 · ramo `cod` do rev-list sem teste: trocar `if cod or` por `if False or` deixa ParecerMescladoNaVolta verde (reproduzido); com o rev-list falhando, `all([])` aceitaria. Falta teste do ramo de falha e mutante próprio dessa condição.
- A2 (recomendado) bin/forge-check:3016 · diferente de `parecer_de_portao_da_branch`, o `commit:` não fica preso a `Revisar-sha:` de brief selado (registro do Jarvis): o autor pode commitar um parecer forjado sozinho. Afrouxamento declarado; o rótulo afrouxa-regra depende da resposta do dono (PERGUNTA de 10:40, `R-DECISAO`).

## Sondas

## Parecer
Aprovado. A regra nova só vale na volta (com `valido`), exige frontmatter da pasta, da branch e do pedido, `commit:` sha40 dentro do intervalo, todo commit que muda o arquivo só de parecer ou merge que fica com a versão de um dos pais, e sem veredito trocado desde o Base-sha. O git que falha cai fechado no diff-tree e no ancestral. Os testes cobrem o caso real, o autor que edita o parecer junto com o código, a resolução de merge à mão, a ausência de conferida, frontmatter errado ou ausente, commit fora do intervalo ou abreviado e veredito trocado. A ajuda do comando e o fragmento do changelog estão atualizados. Rodei `python3 -m unittest tests.test_selo_e_entrega.ParecerMescladoNaVolta` com ambiente limpo: 9 testes, OK. A suíte inteira fica com o CI do PR (`R-REVIEW`).

A1: ajuste pequeno de teste (mock do `rev-list` devolvendo erro) e um mutante para a condição `cod`; vira cartão depois do merge. A2 não é defeito do código, é o afrouxamento que o pedido já declarou: o merge espera o OK do dono para o rótulo (`R-CONFORMIDADE`), e os três portões seguem revisando o PR.
