---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-q0-ameacas
commit: 954cae597f2d7f6901da94cd2058c65e69b7ae53
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E37.47, modelo de ameaças da quarentena BP1 Q0)

Diff de 954cae59 sobre a base 004ce869: `docs/security/ameacas/bp1-quarentena.md` (108 linhas) e o fragmento `changelog.d/v0479-bp1-q0-ameacas.md`. Só documento: sem código, sem guarda, sem mutante; sem suíte local (brief). `forge-check docs` sem erro na árvore (a pasta `docs/security/ameacas/` não é de parecer e não pede frontmatter).

Referências conferidas na árvore do head: `tests/catraca.py:1130` (`VIGIADOS_DO_ROTULO`), `tests/catraca.py:747` (`regra_teto_pulados`), `hooks/_comum.py:2866` (`executar` com `relogio`/`armar` só por palavra-chave) e `:2880`, `tests/test_hooks_volta_corpus.py:127` e `:150`; ADR 0018 e as regras citadas existem.

## Achados
- A1 (bloqueante) docs/security/ameacas/bp1-quarentena.md:82 · C11 manda barrar vencida presente com teto elevado, mas M11.1 (linha 47) aceita teto = fixos + presentes, vencidas incluídas: requisito contraditório para a Q3, e a folga de T11 segue aberta enquanto a vencida fica. Escolher uma regra e alinhar T11, M11.1 e C11.
- A2 (recomendado) docs/security/ameacas/bp1-quarentena.md:66 · T20/M20.1 dão getattr, partial e importlib como não cobertos, mas test_hooks_volta_corpus.py:202 (E37.36, referencias_ao_executar_fora_de_chamada) já os reprova; o cartão fica só com chamadas a executar fora de hooks/. Ajustar S9 (linha 102).

## Sondas

## Parecer
Reprovado por A1 (`R-REVIEW`: requisito provado contraditório pela leitura das linhas 47 e 82). O modelo é a entrada da Q3 (catraca) e dos casos de abuso do `qa-engineer`; com M11.1 e C11 opostos, o teste de C11 reprova a implementação fiel a M11.1, ou o contrário, e T11 não fecha. A correção é de texto: decidir se a vencida conta no teto até o PR que a remove (então C11 passa e T11 vira risco aceito com prazo) ou se não conta (então M11.1 muda e o PR de remoção deixa de ser opcional). A2 não bloqueia: vira cartão depois do merge. O restante (fronteiras, T1 a T19, sondas S1 a S10) é coerente com a D6 = a e com a ADR 0018.
