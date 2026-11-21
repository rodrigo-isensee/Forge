---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-defeitos
commit: 5d383ebfa624c7eabd7ea02fdd2909091c50d29e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E75.3, melhoria/v0479-fechar-defeitos)

Diff `65de25ce..5d383ebf`: `bin/forge-fechar` (passos 1c, 6a e 6), testes dos três cartões, mutantes declarados, fragmento do changelog.

## Achados
- A1 (bloqueante) bin/forge-fechar:870 · a recusa conta toda execução de mesmo nome; com o rótulo de exceção a catraca velha fica cancelled ao lado da nova verde (filter=latest devolve as duas, S1) e o merge direto para; o cartão FECHAR-CHECKS-ANTES-DO-MERGE manda ressalvar o rótulo (R-REVIEW).
- A2 (bloqueante) tests/test_fechar_checks_do_head.py:56 · o teste da duplicata fixa como recusa justamente o caso do rótulo (catraca cancelled ao lado da verde); falta o teste do rótulo aplicado mesclando no merge direto (R-REVIEW).

## Sondas
- S1 · check-runs do head 9441c447 (PR 745, MERGED, rótulo afrouxa-regra) com filter=latest, passados ao awk da linha 870 · espera: catraca verde (rótulo aplicado, PR mesclado) · obtido: duas linhas catraca (success e cancelled, suítes distintas), awk rc=1 para catraca

## Parecer
Reprovado, só pelo passo 6 (FECHAR-CHECKS-ANTES-DO-MERGE).

- 1c (FECHAR-1C-ANTES-DO-2B): confere o commit solto com a árvore do merge-tree com a base; com conflito ou falha confere o head, e a mensagem diz qual árvore foi conferida. Atende o cartão.
- 6a (FECHAR-6A-DEVELOP-ANDOU): com a base local velha busca a base uma vez e segue pela conferência do merge-tree de sempre; a busca que falha para. Atende o cartão.
- 6 (FECHAR-CHECKS-ANTES-DO-MERGE): a leitura dos check-runs do head e a ressalva do `--armar` estão certas, mas a regra "toda execução de mesmo nome verde" recusa o caminho do rótulo já previsto. Sugestão: por nome, julgar a execução mais recente (maior `started_at`/`completed_at`, ou a da suíte mais nova), ou ignorar `cancelled` quando há outra execução do mesmo nome em `completed/success` mais nova; teste com a forma real da S1 (catraca cancelled e success) passando e catraca failure mais nova recusando.

Verificações: `bash -n bin/forge-fechar` ok; `bin/forge-testes` com test_fechar, test_forge_fechar, test_fechar_base_andou e test_fechar_checks_do_head: 194 testes, OK (1 pulado). Suíte inteira fica no CI do PR.
