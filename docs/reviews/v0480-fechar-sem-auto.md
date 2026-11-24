---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-sem-auto
commit: f5143cea54012131715eeac79681695e39c23d5e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E171.4, PR #855, FECHAR-NUNCA-AUTO)

## Achados
- A1 (bloqueante) tests/mutantes/v0478-fechar-checks.json:52 · FCK-M5 e FCK-M6 (linha 62) ficaram fora da fonte: o `de` do M5 casa agora as duas linhas 948 e 956 de bin/forge-fechar, e o do M6 cita "o check obrigatório $falta", que virou "o $falta_q $falta" (961). test_forge_mutante.ConferirTodas vermelho no CI (parte 4/5) e aqui.
- A2 (bloqueante) bin/forge-testes:213 · o mapa de bin/forge-fechar não lista test_fechar_sem_auto, que lê esse arquivo; test_testes_tocados.MapaCobreOQueOsTestesLeem vermelho no CI (python 3.14, parte 1/5). Acrescente o módulo à tupla.
- A3 (recomendado) bin/forge-fechar:939 · "todo check-run do head" depende de per_page=100 sem paginação: acima de 100 check-runs, um vermelho na página 2 não é lido. Hoje o head tem uns 30; pagine (`--paginate`) ou pare quando total_count > 100.
- A4 (recomendado) bin/forge-fechar:1386 · o texto do --dry-run do P6 ainda diz "check-runs obrigatórios", mas checks_do_head_verdes agora exige todo check-run também na promoção; alinhe ao texto do passo 6 (1412).

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (head f5143cea) · espera: OK · obtido: FAIL, specs fora da fonte FCK-M5 e FCK-M6
- S2 · CI do PR #855, job 138494993122 (suíte python 3.14, parte 1/5) · espera: verde · obtido: FAIL test_todo_arquivo_lido_por_um_modulo_roda_esse_modulo (modulo=test_fechar_sem_auto, caminho=bin/forge-fechar)

## Parecer
Reprovado por dois defeitos provados, ambos com a suíte vermelha no CI do head (A1, A2). A1: alinhe o `de` do FCK-M5 ao trecho único da linha 948 (por exemplo, incluindo `falta_q="check obrigatório"`) e o do FCK-M6 ao novo texto da linha 961, no mesmo commit. A2: inclua `test_fechar_sem_auto` no mapa de `bin/forge-fechar` em `bin/forge-testes`.

O mérito está certo. Os dois `gh pr merge` do script (passo 6, linha 1714, e P6, linha 1344) passam por `mesclar_direto`, sempre depois de `checks_do_head_verdes`. Agora essa função exige completed/success na execução mais recente de todo nome do head, não só dos obrigatórios: terminado fora de success para, pendente espera até o prazo e skipped não conta, como já valia. O merge segue preso ao head por `--match-head-commit`. Nenhum caminho mescla com check pendente ou vermelho. O lote roda cada item pelo mesmo `$eu`, então cada item também confere a cópia.

`copia_da_develop` roda antes do log e de qualquer passo. Ela compara o blob do próprio arquivo (`hash-object --no-filters`) com o da origin/develop depois de um fetch forçado. Fetch que falha, arquivo ausente ou blob diferente param sem nada feito. A dispensa exige `FORGE_FECHAR_TESTE=1` e `FORGE_FECHAR_COPIA_LIVRE=1` juntos, e o modo de teste já permitia trocar o `gh`, então ela não abre bypass novo.

Os testes cobrem o ramo de falha de cada guarda, e as duas specs declaram 10 mutantes, um por linha de guarda. Testes rodados aqui: `tests.test_fechar_sem_auto` (13 OK) e `test_fechar...test_1c` (OK). A suíte completa fica no CI, hoje vermelho nas partes 1/5 e 4/5 pelos achados acima. O `bateria (pareceres)` vermelho é esperado antes dos pareceres. A3 e A4 viram cartão depois do merge.
