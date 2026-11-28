---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: 5f26b0f9c0071209726aba5e89ad04acc177eb42
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-27
---
# Review de devops: v0481-f6-ci-uma-vez (#929, F6), delta das voltas 2 e 3

## Detalhes
- ci: 5f26b0f9c0071209726aba5e89ad04acc177eb42 verde

Delta lido: e85793a8..5f26b0f9. Nenhum arquivo de `.github/` mudou neste delta (só testes, `tests/config.json`, a spec de mutantes e os pareceres), então a revisão de segurança do pipeline da volta 1 segue valendo: `permissions`, SHAs, `timeout-minutes` e `concurrency` intactos, sem escrita na `main` (`R-MAIN`) e sem custo novo (`R-CUSTO`).

Os três achados bloqueantes da volta 1 estão sanados:
- A1 e A2: `tests/test_catraca.py` agora espera os 13 `timeout-minutes`, `(2, 1)` agregadores e 3 jobs com `always()`, o que o `ci.yml` novo tem. `tests.test_catraca.Workflows` passa local.
- A3: exceção de neutralidade do `diario.yml` em `tests/config.json` (`excecoes`, igual à do `ci.yml`, mesmo padrão por arquivo); o JSON é válido e a exceção é por arquivo, não global.

Novidades do delta, todas conferidas:
- Mutantes CI-M4 a CI-M8 (fatia do `diario.yml`): `forge-mutante tests/mutantes/v0481-f6-ci-uma-vez.json` local, CI-M1 a CI-M8 todos mortos.
- Teste da fatia com dia fixo: o programa lido do `diario.yml` tem a chamada do dia atual substituída por uma data de dia do ano conhecido (331), sem depender do relógio; o teste confere antes que o trecho existe.
- Sonda S1 gravada como teste (`tests/test_arvore_testada.py`): check `bateria` de PR não vale como prova e o script não lê `check-runs`; passa local.
- Testes locais (com `flock`, poucos segundos): `FiacaoDoCI`, `test_arvore_testada` e `Workflows`, 42 testes, OK.

CI do `5f26b0f9` (`gh pr checks 929`): partes 1, 2, 4 e 5 da suíte, `bateria (passos)`, verificações longas, instalação na versão nova, árvore e a bateria da versão nova verdes. Vermelhos: `bateria (pareceres)`, `bateria` e `catraca` (esperam parecer ou rótulo, não contam) e `suíte` parte 3/5. Esta última, pela anotação do check-run, falha só em `test_nucleo_sem_termos_de_stack`, por causa do texto do parecer de devops anterior (o nome do instalador do cliente escrito solto em `docs/devops/`); este parecer reescrito tira o termo e é o conserto. Nenhum defeito de código ou de pipeline.

`actionlint` e `zizmor`: não rodei (A2 recomendado); o `ci.yml` e o `diario.yml` não mudaram neste delta e o CI os executa.

Duração: partes da suíte entre 5 e 8 minutos; a medida de minutos por release fica para o fechamento do pedido.

## Achados
- A1 (recomendado) .github/workflows/diario.yml:1 · o `schedule` só vale com o arquivo na `main`; até a release o diário roda só por `workflow_dispatch`. Medir os minutos da primeira execução contra a franquia.
- A2 (recomendado) .github/workflows/ci.yml:1 · `actionlint` e `zizmor` ausentes nesta estação; instalar pelo `scripts/preparar-estacao.sh`.

## Custo e rollback
Sem custo novo de dinheiro. Rollback: reverter o merge do PR na `develop`.
