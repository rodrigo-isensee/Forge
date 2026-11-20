---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-m1-medida
commit: 580fea97a00363ac78560eae7a875e80cad7159b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.7, PR-VERDE M1 no head 580fea97)

Escopo lido: `git diff 5ccac0bf..580fea97` (`bin/forge-placar` +115, `tests/evals/test_placar.py` +121, 4 specs de mutante, fragmento). Contra o desenho `docs/propostas/v0479-pr-verde-de-primeira.md` (M1, D7, R1) da branch `melhoria/v0479-pr-verde-de-primeira`, aceito pelo dono em 20/11. Tamanho (H1): 115 linhas de código, dentro do teto. Suíte não rerrodada (brief: sem suíte local); mutação e suíte do item ficam com o PQ do autor e o CI (`R-REVIEW`).

## Achados
- A1 (bloqueante) bin/forge-placar:829 · Catraca tem cancel-in-progress por ref e reage a labeled/edited: o run do opened, cancelado por rótulo ou edição no MESMO head, vira PR `cancelado` e sai da taxa. D7 só tira a cancelada por envio novo. Use o próximo run do mesmo head antes de declarar cancelado (S1).
- A2 (recomendado) bin/forge-placar:75 · R1 do desenho pede o vermelho por job, mas `gh run list --json` não traz `jobs`: com a fonte documentada a quebra por job nunca aparece. Documentar a fonte dos jobs (`gh run view --json jobs`) ou registrar a lacuna na saída.
- A3 (recomendado) bin/forge-placar:834 · `jobs` não lista (ex.: número) derruba com TypeError e rc 1, fora do contrato "ilegível sai lacuna, rc 2". Validar o tipo de `jobs` em `lista_do_gh` junto dos outros campos.
- A4 (recomendado) tests/evals/test_placar.py:749 · `CiPrimeira`, `run` e `pr` vêm depois do `if __name__ == "__main__": unittest.main()`: rodando o arquivo direto, a classe nova não roda. Mover o bloco para antes do `if __name__`.

## Sondas
- S1 · runs: CI success head a 10:01:00; Catraca cancelled head a 10:01:00; Catraca success head a 10:01:20; PR aberto 10:00 · espera: estado verde (taxa 1.0) · obtido: estado cancelado, taxa None

## Parecer
Reprovado por A1. A estrutura (fonte gerada fora, sem rede; falha fechada em `lacuna` com rc 2; 1.º head pelo 1.º run depois da abertura; rerun como vermelho; dependabot fora) segue a D7 e os testes cobrem os riscos listados no desenho. O defeito do A1 é de definição: a Catraca roda em `labeled`, `unlabeled` e `edited` com `cancel-in-progress` no grupo `catraca-${{ github.ref }}` (`.github/workflows/catraca.yml:6-15`), então um rótulo ou edição do corpo logo depois do `gh pr create` cancela a 1.ª execução sem envio novo. Esses PRs (justamente a fatia da catraca que o critério de reversão lê) saem da taxa. Correção esperada: em `primeira_execucao`, uma execução cancelada do workflow que tem outra execução no mesmo `headSha` dá lugar à seguinte; só fica `cancelado` quando a seguinte é de outro head. Teste do ramo: o caso da S1 e o caso com a seguinte em outro head (continua `cancelado`), com mutante na guarda nova (`R-REVIEW`). A2 a A4 não devolvem; viram cartão depois do merge.
