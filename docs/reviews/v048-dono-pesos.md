---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-dono-pesos
commit: 64183ee2507ebfb92ed62ea70a45cd1abf16a826
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 dono dos pesos (#959, DONO-DA-GERACAO-DOS-TEMPOS, classe C, E6.11)

Revalidação (volta 1), só o delta lido em `forge-check parecer delta` (intervalo ca3c07bb..64183ee2): scripts/pesos-do-ci.py, tests/test_pesos_do_ci.py, tests/fixtures/pesos-do-ci/ (3 arquivos), tests/mutantes/v048-dono-pesos{,-1,-2}.json. Fora disso o intervalo só traz pareceres. A 1.ª rodada (E6.6, revisado ca3c07bb) reprovou por A1; A2 e A3 eram recomendados.

- ci: 64183ee2507ebfb92ed62ea70a45cd1abf16a826 verde
- ferramenta: `bin/forge-mutante --base ae194fa9 tests/mutantes/v048-dono-pesos-1.json` e `-2.json`: M1 a M17 morreram; `--cobertura --base ae194fa9`: rc 0, toda guarda do diff com mutante declarado.
- testes do delta: `python3 -m unittest tests.test_pesos_do_ci`: 29 OK.

## Delta lido
- A1 (bloqueante, 1.ª rodada): resolvido. `pr_unico_valido` (scripts/pesos-do-ci.py:76) acha o PR por `commits/<head_sha>/pulls`, só com sha de 40 hexadecimais minúsculos (sha fora do formato nunca vira caminho), e aceita a execução só com exatamente um PR que passa em todas as guardas de `execucao_de_pr_valida`, que não mudaram. O falso de tests/test_pesos_do_ci.py dá `pull_requests: []` e responde só na rota `commits/<sha>/pulls`, com o caminho exato conferido (checklist 12). Corpus S1/S2 em tests/fixtures/pesos-do-ci/, lido por teste.
- Sonda própria na API real (S3, S4): o caminho do PR mesclado agora coleta.
- A2: resolvido; fork (M15) e sha do PR (M16) declarados, com teste de cada guarda sozinha.
- A3 (recomendado, skills/trabalho-em-paralelo/ritmo-e-corte.md:52): fora do delta, segue como cartão depois do merge.
- Specs: a antiga virou `-1` (M1 a M9, mesmas guardas; M7 a M9 reescritos para a rota nova) e `-2` (M10 a M17), pelo limite por arquivo; nenhum mutante caiu.

## Sondas
- S3 · `pr_unico_valido` do head 64183ee2 sobre `gh api repos/<dono/repo>/actions/runs/46148339685` (último head do PR 958, mesclado) · espera: True com `pull_requests` vazio · obtido: pull_requests 0, True
- S4 · `pr_unico_valido` nas 25 últimas execuções `pull_request` com sucesso do ci.yml · espera: ao menos uma válida (antes: 0 em 100) · obtido: 5 de 25

## Parecer
Aprovado. O defeito do A1 está corrigido e provado contra a API real; o resto do filtro e os testes antigos seguem iguais, com os mutantes da v047 e os 17 do item mortos.
