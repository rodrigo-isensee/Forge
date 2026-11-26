---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: 8e9f5704f52b32e0419ab0b7bbc066f17e6f013a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E22.7, #913, revalidação por delta)

Delta lido: `forge-check parecer delta docs/reviews/v0481-ci-parecer-nao-cancela.md`, intervalo `b04f0220..8e9f5704`, no domínio: `.github/workflows/ci.yml`, `.github/workflows/obsoletas.yml`, `tests/mutantes/v0481-ci-parecer-nao-cancela.json`, `tests/test_catraca.py`, `tests/test_ci_nao_cancela_parecer.py`.

## Achados
- A7 (bloqueante) .github/workflows/obsoletas.yml:52 · fora do ci.yml, `RUN_ID` é o id do run do Obsoletas, criado depois do run do CI do mesmo push: `id -lt RUN_ID` cancela o CI do próprio head (S1); comparar pelo `head_sha` (cancelar só run com `head_sha` diferente do `HEAD_SHA`) e não pelo id
- A8 (bloqueante) tests/test_ci_nao_cancela_parecer.py:18 · o `gh` falso lista runs do ci.yml com ids do mesmo espaço que o `RUN_ID` (10) e sem `head_sha`: não imita o run do CI do mesmo head com id menor que o do Obsoletas; incluir esse run e afirmar que ele não cai (o teste fica verde com o A7 presente)

## Sondas
- S1 · push 8e9f5704 (synchronize, envio com código): run Obsoletas 45847608652 e run CI 45847608038, mesmo head · espera: o CI do 8e9f5704 segue até o fim · obtido: log do Obsoletas "Request to cancel workflow 45847608038 submitted."; CI 45847608038 `completed cancelled`, sem nenhum job de suíte

## Parecer
Reprovado. A1 a A6 da 1.ª rodada resolvidos no delta: o job saiu do ci.yml (o ci-local e o marcador do lint não o veem mais, A1 e A2), o ci.yml segue sem escrita e o teste o afirma (A3), o `obsoletas.yml` entra na conferência de timeout (A4), 14 mutantes declarados e mortos (A5), a guarda redundante saiu (A6). O filtro por `head_repository` e o `if:` de PR do próprio repositório estão certos; `actions: write` só no job, `contents: read` no topo, `timeout-minutes: 3`, entradas só por `env:`.

O defeito novo é o da mudança de arquivo: os ids de run são globais e o Obsoletas nasce depois do CI do mesmo evento, então o próprio head perde a suíte em todo envio com código, o contrário do que o pedido quer. O CI do head está cancelado, não verde: sem linha ci.

Provas do review:
- CI do 8e9f5704: run 45847608038 `cancelled` pelo Obsoletas (S1); os vermelhos de `gh pr checks` (suíte, bateria, instalação, teto de pulados, árvore já provada) são o cancelamento, não teste reprovado. `catraca` espera o rótulo do dono (ci.yml, R-CONFORMIDADE); `bateria (pareceres)`, este parecer.
- Local, no clone: `python3 -m unittest tests.test_ci_nao_cancela_parecer tests.test_catraca.Workflows tests.test_ci_local tests.test_falhas_no_resumo`: 129 testes OK.
- `bin/forge-mutante tests/mutantes/v0481-ci-parecer-nao-cancela.json` (rev 8e9f5704f52b): M1 a M14 morreram.
