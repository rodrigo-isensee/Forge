---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: 700a2fc497a0ea79e47961794a0fb76f0c3d655d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E32.23, #929, F6 no CI), voltas 4 e 5 por delta

Delta lido (H3): `forge-check parecer delta` de `ac8202d0..700a2fc4`. No domínio há 2 arquivos: `tests/test_suite_partes.py` e `tests/mutantes/v0481-f6-ci-uma-vez-2.json`; o resto do intervalo é parecer (`docs/qa/`, `docs/reviews/`, `docs/security/`). Nada fora do delta foi relido.

- ci: 700a2fc497a0ea79e47961794a0fb76f0c3d655d verde

## Parecer
**Aprovado.** A volta 4 (`e8998527`) e a volta 5 (`700a2fc4`) não trazem bloqueante novo.

**CI (G3):** `gh pr checks 929` lido no run 45941299117, com head `700a2fc4`. Estão verdes as 5 partes da suíte 3.12, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `teto de pulados (python 3.12)` e `árvore já provada na develop`. Ficam fora da conta `bateria`, `bateria (pareceres)` e `catraca`, que esperam os pareceres e o rótulo.

**O delta:**
- **Testes de comportamento do diário (A1 e A2 do QA):** `rodar_passo` roda o `run` real do passo no bash com `-e -o pipefail`, com ambiente limpo (PATH, HOME, RUNNER_TEMP e GITHUB_STEP_SUMMARY montados no teste), como o GitHub faz.
  - Passo dos mutantes: as 30 specs falsas fazem cair na fatia exatamente uma, seja qual for o dia, e o teste fica determinístico. O `forge-mutante` falso decide o rc, e o teste confere rc 0 e rc 1 e a linha do aviso.
  - Cartão: o `gh` falso registra as chamadas e o teste confere o número exato da issue (`issue comment 42`), não um prefixo. Isso atende o item 12 do checklist.
- **Jobs do diário:** o teste afirma o conjunto exato dos 4 jobs, `ref: develop` em cada checkout, a matriz `1, 2, 3, 4, 5` casando com `--parte "$PARTE/5"` e com o rótulo, e `timeout-minutes` em todo job.
- **Fumaça do 3.14:** o teste lê o texto do `run`. A linha é uma linha de execução, não uma guarda (`if`, `||`, `exit`), e o mutante CI-M15 (`run: true`) morre.
- **Spec dividida (V2):** `v0481-f6-ci-uma-vez.json` ficou com CI-M1 a CI-M8, e o diff dela em `ac8202d0..700a2fc4` é vazio. `-2.json` tem CI-M9 a CI-M15, os mesmos que o `e8998527` declarou, só mudados de arquivo.

**Verificado local** (com o flock da trava b):
- `tests.test_suite_partes.FiacaoDoCI`: 17 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-f6-ci-uma-vez-2.json --processos 1` em `700a2fc4`: morreram os 7 (CI-M9 a CI-M15). São eles diario.yml:128, :32, :72, :95, :28 e :154, e ci.yml:318.
