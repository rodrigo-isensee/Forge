---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-merges
commit: 590d1954d4d31881a434ef926530a0bc52e2c711
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E62.16), melhoria/v0479-entrega-merges

Base-sha 8ee73d15, head 590d1954 (4 commits: 01e57413, 3092188d, 62062b7c, 590d1954). Os dois aceites novos do `forge-check entrega` foram julgados quanto a brechas, junto com o desvio do autor (o merge-base com a develop remota em vez da ponta). Pela `R-REVIEW` e pelo brief, a suíte inteira fica no CI. Ainda não há PR, então também não há CI. Rodei as classes novas (`MergeDaBaseDepoisDoBrief` e `MergeDeParecerAninhado`: 20 testes OK), duas sondas e a classe de teste do nome que o diff reaproveita.

## vindos_da_base (ENTREGA-MERGE-DA-DEVELOP)
- **A brecha.** Não achei brecha no aceite. Um arquivo só sai do escopo se o blob dele no head for igual ao do merge-base do head com a develop lida por `git ls-remote`. Esse commit está na develop do servidor, aonde só se chega por PR com os portões, e o autor não o reescreve. O aceite do usuário e os `desfeitos` (o que a branch mudou até a conferida e devolveu à base, A1 da segurança) continuam fora do filtro. Sem rede ou sem o commit buscado, nada sai. Quando a resolução do merge fica com a versão da develop, a contribuição líquida é zero e não sobra nada a revisar.
- **O desvio.** Aceito o merge-base remoto em vez da ponta. A ponta tiraria do escopo o arquivo do autor que por acaso fosse igual a uma develop mais nova, que ele não mesclou. E deixaria à vista o que a develop mudou depois do merge. O merge-base mede só o que o merge trouxe de fato. É mais estrito e está correto.
- **O defeito.** O nome novo já existia (`bin/forge-check:877`, E7 0.45.6, usado em `commit_vale` e no `parecer delta`, linhas 915 e 3744). A definição nova, na linha 2853, sobrepõe a antiga no módulo. Os dois chamadores antigos passam um sha como `base`: o `ref_da_base` não acha a ref, a função devolve vazio e o E7 fica desligado. Isso falha fechado, mas é uma regressão provada (S1). A correção é renomear a função nova (por exemplo, `vindos_do_remoto_da_base`), o mutante D1 a D7 e a doc.

## conferidos_ancestrais (ENTREGA-MERGE-DE-PARECER-ANINHADO)
- **O caso real.** O aninhado de verdade (o merge de pareceres, outro pai cujo primeiro pai já traz o P) está coberto e não abre brecha para um arquivo fora dos P, porque o blob tem de bater.
- **A brecha.** Hoje a regra é "o último `parecer conferido` que altera o arquivo" (`parecer_trazido`, M1/T-3/S4). A nova aceita qualquer `parecer conferido` ancestral do outro pai. Assim, um merge resolvido à mão pode devolver o blob de um parecer conferido antigo (aprovado) por cima de um mais novo da mesma história (reprovado), e o escopo diz ok (S2). Antes da mudança, só o pai direto contava e isso reprovava. A correção é aceitar, por arquivo, só o blob do conferido mais novo da história do outro pai que muda esse arquivo.

## Achados
- A1 (bloqueante) bin/forge-check:2853 · Definição nova de `vindos_da_base` sobrepõe a do E7 (linha 877) com outra assinatura; `commit_vale` (915) e `parecer delta` (3744) passam a receber vazio e o E7 se desliga: 4 falhas em tests/test_forge_check_base_igual.py, que no Base-sha passa. Renomeie a função nova.
- A2 (bloqueante) bin/forge-check:2528 · `conferidos_ancestrais` aceita o blob de qualquer parecer conferido ancestral, não o do último que muda o arquivo (`parecer_trazido`, M1): o merge resolvido à mão restaura parecer aprovado antigo sobre um reprovado mais novo, sem recusa. Aceite só o conferido mais novo por arquivo.
- A3 (recomendado) bin/forge-check:2527 · `rev-list <q>` lê a história inteira do outro pai a cada merge; limite com `^<base_ref>` ou use `merge-base --is-ancestor` por sha conferido.

## Sondas
- S1 · python3 -I -m unittest tests.test_forge_check_base_igual (head 590d1954 e Base-sha 8ee73d15) · espera: OK nos dois · obtido: Base-sha OK (13); head FAILED failures=4 (test_trazido_sem_merge_nao_desatualiza e mais 3, desatualizado: bin/f)
- S2 · P1 aprovado, P2 reprovado sobre P1, os dois conferidos; merge de P2 resolvido com o blob de P1; merges_nao_conferidos · espera: recusa fora dos pareceres conferidos · obtido: [] (só com P2 na linha: recusa)
