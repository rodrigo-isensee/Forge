---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: c460102d3d64d4f87b4367a4e5a32d365c43e759
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478-testes-prazo (E12.14, revalidação)

Revalidação (H3, R-REVIEW) do head `c460102d`. Li só o delta do `forge-check parecer delta`: `318721db..c460102d`, sem o que veio da base (`develop`, trazida pelo `forge-fechar` no merge `33291ec4`). No domínio há 1 arquivo, `tests/mutantes/v047-ci-rapido-3.json`. Fora do delta, nada foi relido. Não rodei a suíte; a prova dela é o CI do PR.

## Delta lido
- M33 e M34 (`tests/mutantes/v047-ci-rapido-3.json`): o `de` e o `para` agora incluem o passo "Recusas por carga no resumo (PRAZO-CARGA ...)", que este pedido inseriu no `ci.yml` entre "Falhas no resumo" e o upload dos pulados. Sem esse alinhamento, o `de` antigo deixava de existir no `ci.yml`.
- Conferi: cada `de` aparece 1 vez no `ci.yml` do head, e o `para` difere do `de` só em `--parte "$PARTE/5"` → `"$PARTE/4"`. A guarda declarada não mudou.
- `bin/forge-mutante --processos 1 tests/mutantes/v047-ci-rapido-3.json`: M33 morreu (`.github/workflows/ci.yml:205`) e M34 morreu (`.github/workflows/ci.yml:393`). M25 a M32 da mesma spec também morreram.

## Parecer
Aprovado. O delta é só o alinhamento do texto dos mutantes ao passo novo do CI, sem lógica nova. O A3 (recomendado) da rodada anterior segue como recomendação, porque `tests/prova_de_carga.py` não mudou no delta.
