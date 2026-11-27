---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: e85793a8317bf410d3b98cc7f45ad46ffed285e8
parecer: reprovado
revisor: forge:devops-engineer
data: 2026-11-26
---
# Review de devops: v0481-f6-ci-uma-vez (#929, F6), delta da volta 1

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:35 · efeito do corte do arvore-envio e do 3.14 no CI (tests/test_catraca.py:4253): test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore falha: a lista de `timeout-minutes` esperada ainda é a do ci.yml com os jobs 3.14 e `arvore-envio`; o ci.yml tem 13 valores. Atualizar o teste na volta 2.
- A2 (bloqueante) .github/workflows/ci.yml:58 · efeito do mesmo corte (tests/test_catraca.py:4267): test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde falha: espera 2 agregadores de prova do push na develop e o ci.yml tem 1 (`(2, 1) != (2, 2)`) depois do corte do 3.14 no push. Alinhar o teste ao ci.yml.
- A3 (bloqueante) .github/workflows/diario.yml:100 · o passo de mutantes novo e o diário todo (npm na linha 82, tests/test_forge.py:511): test_nucleo_sem_termos_de_stack (tests/test_forge.py:511) reprova o `npm` no núcleo. Registrar a exceção em tests/config.json (`excecoes`) ou mover a instalação do claude para um script fora da varredura.
- A4 (recomendado) .github/workflows/ci.yml:1 · `actionlint` e `zizmor` ausentes nesta estação, então não rodei o lint do YAML; o CI criou os jobs (YAML válido, o defeito do parecer anterior está sanado). Instalar pelo `scripts/preparar-estacao.sh`.
- A5 (recomendado) .github/workflows/diario.yml:1 · o `schedule` só vale com o arquivo na `main`; até a release o diário roda só por `workflow_dispatch`. Medir os minutos da primeira execução contra a franquia.

## Detalhes
Reprovado: o CI do head não está verde (PQ-3, G3); A1 a A3 são os defeitos do CI causados pelo delta e vão à volta 2. `gh pr checks 929` no e85793a8: `bateria`, `bateria (pareceres)` e `catraca` vermelhos; `suíte (python 3.12, parte 2/5)` (A1, A2) e `parte 3/5` (A3) vermelhos por esses três testes; passos, 3.14, instalação, árvore e verificações longas verdes. Os vermelhos de `bateria (pareceres)`, `bateria` e `catraca` esperam parecer ou rótulo e não contam sozinhos; as partes 2 e 3 são defeito.

Delta do ci.yml e do diario.yml lido sem defeito de segurança: `arvore-envio` e o passo `--do-pr` saíram (some o token de leitura de checks e PRs do envio na develop), `name:` do passo 3.14 agora entre aspas, `permissions`, SHAs, `timeout-minutes` e `concurrency` intactos. O diário: fatia por spec, `--ids` para os pendentes conhecidos, sem entrada não confiável em `run:`, `issues: write` só no job `cartao`. Sem escrita na `main` (`R-MAIN`) nem custo novo (`R-CUSTO`).

Duração: partes 1 a 5 entre 5m17s e 7m54s; a medida fechada fica para a volta 2 com tudo verde. Não rodei a suíte (G3).

## Custo e rollback
Sem custo novo de dinheiro. Rollback: reverter o merge do PR na `develop`.
