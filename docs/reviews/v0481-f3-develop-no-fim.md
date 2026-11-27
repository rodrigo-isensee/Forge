---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f3-develop-no-fim
commit: 7de82a022ae4c7b51479a7fdc87646b580153e03
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E30.5, F3 develop só no fim, volta 1 do #924)

Revalidação por delta (H3) sobre `7de82a02`: li só `forge-check parecer delta docs/reviews/v0481-f3-develop-no-fim.md`, intervalo `fe299c72..7de82a02` (3 commits, 14 arquivos no domínio; `bin/forge-check` +27/-2, dentro do teto H1).

## Delta lido
- A1 (bloqueante da 1ª rodada) resolvido: skills/trabalho-em-paralelo/ritmo-e-corte.md:20 cita `bin/forge-fechar <pedido> --ref <branch>`; `tests.test_comando_pronto` OK; a sonda S1 entrou no corpus (tests/test_comando_pronto.py:106).
- A2 resolvido: "byte à mão em código do domínio" em ritmo-e-corte.md:21 e docs/fechamento-integrador.md:22.
- A3 resolvido: docs/regras/R-FLUXO.md:26 sem a exceção "base velha" (o rótulo `afrouxa-regra`, se couber, o time aplica na integração).
- A4 resolvido: M3 e M5 de tests/mutantes/v0481-d2-no-brief.json apontam para o teste renomeado; M5 descreve a guarda nova.
- `trouxe_a_base` (bin/forge-check:914): o head que trouxe a base (merge-base mudou) vai sempre ao merge simulado; o `-s ours` e o conflito resolvido com o lado da branch desatualizam; git que falha fecha (`desatualizado: não comparei`). Merge limpo segue valendo (controle `test_merge_limpo_segue_valendo`).
- `inicio_da_volta` (bin/forge-check:4625): a volta 3 compara com o início mais a base trazida, o que destrava o #913; ref da base num commit da branch, conflito e base ausente voltam ao `inicio`. A ref local forjada que entra como segundo pai fica com a catraca do CI, como a docstring declara.
- VA-M11 realinhado à linha nova (tests/mutantes/v0481-voltas-alinhada-2.json:30).

## Conferência
- ci: 7de82a022ae4c7b51479a7fdc87646b580153e03 verde (run 45938144589: suíte 3.12 e 3.14 partes 1 a 5, instalação, passos, verificações longas, teto de pulados, árvore já provada e `bateria (python 3.14)` em pass; fora `bateria`, `bateria (pareceres)` e `catraca`, que esperam parecer ou rótulo).
- Testes do delta, locais com a trava: `tests.test_comando_pronto`, `tests.test_volta_alinhada`, `tests.test_forge_check_base_igual.MergeQueDescartaABase`, `tests.test_fechar_forge_check_real.DevelopSoNoFim`, `tests.test_reval_delta`, `tests.test_forge_pronto.BaseVelha`: 33 testes OK.
- Mutantes declarados (`bin/forge-mutante`): F3-1 a F3-8 (tests/mutantes/v0481-f3-develop-no-fim.json) e F3-9 (-2.json) morreram; F3-5 e F3-9 por erro do teste declarado sob o mutante (a guarda evita a exceção), o que conta como morto. Cada guarda mudada tem um mutante e teste do ramo de falha.

## Parecer
Aprovado. A volta corrige o bloqueante A1, aplica os recomendados A2 a A4 e fecha o achado de segurança do merge que descarta a base com teste de comportamento e falha fechada.
