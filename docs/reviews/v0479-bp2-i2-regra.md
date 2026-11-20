---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i2-regra
commit: 80f4bd1f2912d3222559b954eafde362e9e1a5dc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E38.9 (BP2 I2 e I5, fila e conserto na R-FLUXO), revalidação

Delta lido: `forge-check parecer delta docs/reviews/v0479-bp2-i2-regra.md`, intervalo 0ce5173b..80f4bd1f (base origin/develop 004ce86 → 8a50379), 4 arquivos no domínio: `changelog.d/v0479-bp2-i2-regra.md`, `docs/protecao-de-branch.md`, `skills/trabalho-em-paralelo/ritmo-e-corte.md`, `templates/projeto/docs/engineering/protecao-de-branch.md`; o resto do intervalo é parecer (QA, segurança e o meu). Só texto, 0 linha de código (H1 ok).

- A1 (reprovado em 0ce5173b) resolvido: `docs/protecao-de-branch.md:45` diz agora que, até a I4 entrar no `bin/forge-fechar`, a fila é à mão pelo `tech-lead` e que o passo 6a só para no conflito, sem retestar (casa com `bin/forge-fechar:937`, S1 do parecer anterior); `ritmo-e-corte.md:24` e o fragmento do changelog dizem o mesmo.
- A2 resolvido: o passo 8 dos dois documentos de proteção (`docs/protecao-de-branch.md:21`, `templates/projeto/docs/engineering/protecao-de-branch.md:30`) remete o novo teste sobre o topo à fila da `R-FLUXO` (D3) e não diz mais que a base entra uma vez; a seção "Fila de merge" citada existe (linha 48 do modelo).
- C3 e C4 do conserto ficaram mais completos (achados da segurança; o mérito é dela).

Módulos de texto rodados no head 80f4bd1f: `tests.test_modelos_projeto` e `test_forge` Neutralidade, NeutralidadeDoNucleo, RegrasInviolaveis, RegrasComId, TextosDoAgenteEDaRegra: 35 testes OK. Suíte inteira: no CI do PR.

## Parecer
Aprovado no head 80f4bd1f: A1 e A2 corrigidos, sem achado novo no delta.
