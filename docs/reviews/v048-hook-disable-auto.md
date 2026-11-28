---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-hook-disable-auto
commit: 897d2036179082df5f238d938e182316a13b307c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 · HOOK-DISABLE-AUTO (E13.2), 1.ª rodada (E13.34)

PR #969, head 897d2036, base develop a1971853. Rodada completa.

## Achados
- A1 (bloqueante) bin/forge-testes:153 · o módulo novo test_hooks_desarma_auto falta em FORGE_CHECK (:153) e em REAPROVEITAM_O_LOTE (:163); o CI do head fica vermelho na suíte parte 1/5 (test_testes_tocados, 2 falhas, reproduzidas na cópia). Incluir o nome nas duas tuplas.
- A2 (recomendado) hooks/parecer.py:493 · desarma_o_auto lê só o que vem depois de `merge`: a opção --admin=true posta entre `pr` e `merge`, com --disable-auto depois, sai como leitura (S2); hoje não mescla porque o gh recusa --admin com --disable-auto, mas o hook fica dependendo do gh.

## Sondas
- S1 · python3 -m unittest tests.test_testes_tocados (MapaDoForgeCheck e CaminhoFiltroEAviso, os dois testes do CI) · espera: OK · obtido: FAILED (failures=2), faltam no mapa FORGE_CHECK ['test_hooks_desarma_auto']
- S2 · analisar() dos tokens [gh, pr, --admin=true, merge, x, --disable-auto] · espera: ('prmerge', None, 'x') · obtido: None

## Verificação
- ci: 897d2036179082df5f238d938e182316a13b307c vermelho: suíte (python 3.12, parte 1/5) falhou (test_testes_tocados, A1); partes 2 a 5, instalação, bateria (passos, verificações longas, python 3.14) e árvore provada verdes; catraca e catraca (conferência) esperam o rótulo (R-CONFORMIDADE, hooks/parecer.py protegido), como previsto.
- Teste do diff: `python3 -m unittest tests.test_hooks_desarma_auto` OK (2 testes, 9 fixtures).
- Mutantes declarados: `bin/forge-mutante tests/mutantes/v048-hook-disable-auto.json --processos 1`: M1 a M8 morreram; `--cobertura --base a1971853`: as três linhas de guarda (359, 361, 493) cobertas.
- Tamanho (H1): 14 linhas de código, um comportamento.

## Parecer
Reprovado só por A1. A lógica do desarme está correta: nenhuma forma lida depois de `merge` que mescla passa como desarme. Conferi as formas duvidosas (valor de opção com valor, `=true` sozinha, `=false` por último, `--auto`, `--admin`, grupo curto, depois de `--`) pelas fixtures e por sondas (`-b --disable-auto` e `--admin=t --disable-auto` seguem como merge; `--disable-auto=0 --disable-auto` vale a última, como no gh). O `in` antes da chamada deixa o merge comum sem passo a mais; os testes de custo do corpus passaram no CI (partes 2 a 5 e o resto da parte 1, onde só falharam os dois testes do mapa).

A1: bin/forge-testes:153 e :163 · problema: módulo de teste novo fora do mapa do forge-testes · sugestão: incluir `test_hooks_desarma_auto` nas duas tuplas · severidade: bloqueia. A2 é recomendação e vira cartão depois do merge.
