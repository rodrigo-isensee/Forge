---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-m1-medida
commit: c5c0a232123312a20f5de27be913d57741377a55
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.21, PR-VERDE M1, revalidação no head c5c0a232)

Revalidação (H3, `R-REVIEW`): lido só `forge-check parecer delta docs/reviews/v0479-pv-m1-medida.md`, intervalo `580fea97..c5c0a232`, domínio código e testes: `bin/forge-placar`, `changelog.d/v0479-pv-m1-medida.md`, `tests/evals/test_placar.py`, `tests/mutantes/v0479-pv-m1-medida-5.json`. Suíte inteira não rerrodada (brief: sem suíte local; fica com o CI do PR).

## Delta lido
- A1 (bloqueante anterior) resolvido: em `primeira_execucao` (`bin/forge-placar:829-833`), execução cancelada do workflow dá lugar à seguinte do mesmo `headSha`; a de outro head não entra, e o PR segue `cancelado`, fora da taxa (D7). Execução seguinte não troca a 1.ª não cancelada. Docstring e fragmento atualizados.
- A3 resolvido: `jobs` que não é lista sai `lacuna`, rc 2, em `lista_do_gh` (`bin/forge-placar:806`).
- A4 resolvido: o `if __name__ == "__main__"` foi para o fim de `tests/evals/test_placar.py`.
- A2 não mexido; segue recomendado (cartão depois do merge).
- Rodado pelo revisor: `python3 -m unittest tests.evals.test_placar.CiPrimeira` → 15 testes OK; `bin/forge-mutante --processos 1 tests/mutantes/v0479-pv-m1-medida-5.json` → M30, M31 e M32 morreram (`bin/forge-placar:806`, `:833`, `:833`).

## Achados
- A2 (recomendado) bin/forge-placar:75 · R1 do desenho pede o vermelho por job, mas `gh run list --json` não traz `jobs`: com a fonte documentada a quebra por job nunca aparece. Documentar a fonte dos jobs (`gh run view --json jobs`) ou registrar a lacuna na saída.

## Sondas
- S1 · runs: CI success head a 10:01:00; Catraca cancelled head a 10:01:00; Catraca success head a 10:01:20; PR aberto 10:00 · espera: estado verde (taxa 1.0) · obtido: verde, taxa 1.0 (caso coberto por `test_cancelada_sem_envio_novo_da_lugar_a_seguinte_do_mesmo_head`, mutante M31 morto)

## Parecer
Aprovado. O bloqueante A1 foi corrigido como a S1 pedia, com teste do ramo de falha (seguinte em outro head continua `cancelado`) e mutante por guarda nova. O A2 vira cartão depois do merge.
