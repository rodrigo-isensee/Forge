---
tipo: review
contrato: 1
pedido: ci-suite-no-teto
branch: melhoria/ci-suite-no-teto
commit: 1effb9e26ca8dc9956f29a1426717ef9ebae115f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: ci-suite-no-teto

## Achados

## Parecer
Aprovado. Diff lido: 1b6f418...1effb9e, 3 arquivos.

- `.github/workflows/ci.yml`: só os três `timeout-minutes` mudam (rapida 10 para 20; job python 3.14 e `bateria` 15 para 25). Nenhum job, passo, gate, `if` ou permissão a mais ou a menos; o comentário da linha 4 não está no diff. O ajuste não afrouxa portão (opção B da proposta `docs/propostas/ci-suite-no-teto.md`: o timeout não é teste nem check exigido; custo zero em repositório público, `R-CUSTO`; o custo é só detectar mais tarde um teste travado).
- `tests/test_catraca.py`: a asserção nova em `Workflows.test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore` compara `["20","25","25"]` na ordem do arquivo (linhas 26, 45, 76); com os valores antigos (10, 15, 15) falha. Rodei `tests.test_catraca.Workflows`: 6 testes, OK (load 5,2).
- `changelog.d/ci-suite-no-teto.md`: fragmento presente, tipo Alterado, sem editar o `CHANGELOG.md`.
- Teto por PR (M14): 8 linhas de código e teste (6 em ci.yml, 2 em test_catraca.py), bem abaixo de 150; um comportamento só.
- Classe de achado recorrente (PA-7): conferida a lista de `docs/engineering/achados-recorrentes.md`; nenhuma classe se repete neste diff, sem linha AR nova nesta rodada.
- Segurança e QA: pareceres próprios, não refeitos aqui.
