---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-conformidade
commit: d67b2f4ebf91b8feba0aec94070670ce6e097dbc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E1.24 (revalidação no head d67b2f4e, A8 da segurança)

Escopo lido: só o delta de `forge-check parecer delta` (40dc5f4f..d67b2f4e): changelog.d, docs/hooks.md, hooks/conformidade.py (2 guardas), specs -8 (M56 reescrito), -10 (M73) e -11 (M74, nova), tests/test_conformidade_verde.py (classe `TrocaDeBranchAtrasDoBusybox`). Fora do domínio, nada relido.

## Achados
- A1 (recomendado) tests/test_conformidade_verde.py:463 · segue do head bdbdc257: o pulo sem GNU tar também pula no CI; siga o `tests/apoio_sandbox.py`. Vira cartão.
- A2 (recomendado) hooks/conformidade.py:2292 · H1: o item soma 301 linhas em hooks/ desde a base 4182a6b9 (+2 nesta volta), acima de 150; o PR leva `teto: excedido, <n> linhas, <motivo>`. Vira cartão.

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-conformidade.md`, intervalo 40dc5f4f..d67b2f4e, 7 arquivos no domínio.
- A8 da segurança: fechado no domínio do review. `por_applet` (linha 2292) nomeia a condição que já existia e a linha 2307 deixa de registrar a troca de branch quando o programa veio do `busybox`/`toybox`, que não têm applet `git`; só aperta (registro a menos faz o comando seguinte na main recusar como na base). A contraprova `test_troca_direta_segue_registrada` mostra que a troca direta segue valendo. O aceite do A8 é da segurança.
- Mutantes: M56 reescrito para a nova forma da linha 2292; M73 (linha 2307) e M74 (linha 2293), um por guarda mudada; spec -10 com 8 mutantes, -11 aberta para o excedente.
- A1 e A2: seguem recomendados, sem mudança no código deles.

## Verificação
- Testes do delta: `python3 -m unittest tests.test_conformidade_verde.TrocaDeBranchAtrasDoBusybox`: 2 testes, OK (30,6 s).
- Cobertura: `bin/forge-mutante --cobertura --base 40dc5f4f`: rc 0; 2292 (M56), 2293 (M74) e 2307 (M73) cobertas.
- Mutantes: `bin/forge-mutante --processos 1 --base 40dc5f4f` nas specs -8, -10 e -11: rc 0, M55 a M62 e M71 a M74 mortos. Teste roda subprocesso com o ambiente do `CloneDoForge`.
- Suíte inteira: não rodada (brief); sem PR, CI do head não citável.

## Parecer
Aprovado. A correção do A8 tira o registro de troca de branch quando o pedido vem pelo applet do busybox/toybox; só aperta, com teste do ramo de falha nas 3 formas × 3 operadores × 7 ações na main, contraprova da troca direta e mutantes declarados e mortos.
