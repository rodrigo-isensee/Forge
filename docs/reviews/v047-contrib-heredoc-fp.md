---
tipo: review
contrato: 1
pedido: v047-contrib-heredoc-fp
branch: melhoria/v047-contrib-heredoc-fp
commit: f7e12a87a474a2e61ea2a0e621e9847c988d9ca0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047-contrib-heredoc-fp

Code review da E2.104 (classe C) no head f7e12a87, por instância que não fez a entrega. Sem parecer anterior nesta branch: parecer completo.

## Achados

## Sondas

## Parecer
Aprovado, sem achado. O commit porta para a develop do dia (base f4b0c2ae) o delta aprovado nos três portões da `melhoria/v047-hook-heredoc-fp` no head 0eee1453 (cartões HOOK-CONTRIB-HEREDOC-FP e HOOK-REVIEW-HEREDOC-TIMEOUT).

Fidelidade do porte (conferida, não suposta): o diff de `hooks/parecer.py`, `tests/test_hooks_parecer_pasta.py`, `docs/hooks.md` e da emenda na ADR 0011 contra a base é linha por linha o mesmo de `merge-base(0eee1453, develop)..0eee1453`; as 36 fixtures `tests/hooks/parecer/heredoc-interpretador-*` são idênticas às de 0eee1453; as 4 specs de mutante são as mesmas, só com o pedido renomeado (`v047-hook-heredoc-fp` para `v047-contrib-heredoc-fp`). Fora disso, só o fragmento `changelog.d/v047-contrib-heredoc-fp.md` e o índice `docs/hooks-fixtures.md` regenerado; os pareceres da branch irmã não vieram, como o commit diz. O mérito do código, as sondas e a mutação ficam os do parecer 4379efbb (review E4.12) e dos pareceres de QA e segurança da irmã; o que muda aqui é a base, e a base nova não toca `hooks/parecer.py` em conflito com o delta.

Checklist de leitura sobre o diff: faz o que os cartões pedem (o corpo de `python3 -` que só cita comando de PR em texto deixa de recusar; o que lança processo com o comando nas constantes segue recusado; o `sh` que só lê ou espera não liga a rede D). Guardas novas com mutante declarado, um por linha: `bin/forge-mutante --cobertura --base f4b0c2ae` dá toda condição mudada coberta, rc=0. Falso de git/gh: não há no diff. Teste de pasta afirma mínimo de 36 fixtures e os dois lados (item 11).

Rótulo: o PR **precisa** do rótulo `afrouxa-regra`. A emenda da ADR 0011 diz "Afrouxa; rótulo `afrouxa-regra`" (a rede D sai para o corpo de Python), e `tests/catraca.py --base f4b0c2ae` sai 1: "R-CONFORMIDADE: mudança em hooks/parecer.py ... só passa com o rótulo `afrouxa-regra` do dono, aplicado depois do último push". O título do PR deve destacar o afrouxamento e o motivo (CLAUDE.md, invariantes); o rótulo é do dono, depois do último push.

Lacuna que segue, documentada e não bloqueante: a barreira de Python é lista de nomes, não fronteira; o texto montado sem constante (`chr`, arquivo, ambiente) passa, como já passava no `python3 -c` (`docs/hooks.md`, "Heredoc a interpretador"; A2 do parecer da irmã).

Tamanho (M14): 105 linhas em `hooks/parecer.py` e 11 em `tests/*.py`, 116 no total, abaixo de 150; um comportamento só, com corpus próprio. Sem PR aberto, sem CI para citar; o CI do PR é o portão da suíte.

Verificações: teste novo `tests.test_hooks_parecer_pasta` (`-k heredoc_interpretador`) rodado no head em ambiente limpo: 1 teste, 36 fixtures, OK em 4,5 s; cobertura de mutantes rc=0; catraca rc=1 pelo rótulo.
