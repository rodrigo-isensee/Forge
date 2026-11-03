---
tipo: revisao-devops
contrato: 1
pedido: ci-suite-no-teto
branch: melhoria/ci-suite-no-teto
commit: 1effb9e26ca8dc9956f29a1426717ef9ebae115f
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-03
---
# Review de devops: ci-suite-no-teto

## Parecer
Aprovado. O diff de `.github/workflows/ci.yml` (1b6f418...1effb9e) muda só três linhas de `timeout-minutes`: `rapida` (checagem rápida) de 10 para 20 (linha 26), `bateria-python-tres-quatorze` de 15 para 25 (linha 45) e `bateria` de 15 para 25 (linha 76). Os valores caem nos jobs certos e nenhum `if:`, `needs:`, `permissions:`, `concurrency`, ação fixada por SHA ou passo mudou. Não há `continue-on-error` nem `[skip ci]`; nenhum portão foi afrouxado (`R-VERIFY`). O YAML carrega sem erro (`yaml.safe_load`). A asserção nova em `tests/test_catraca.py:2696` (`["20", "25", "25"]`, em ordem de arquivo) confere os três valores. O fragmento `changelog.d/ci-suite-no-teto.md` descreve a mudança.

Ferramentas: `shellcheck` presente (nenhum script alterado); `actionlint` ausente do PATH (lacuna registrada, o agente não instala; o CI o roda). A sintaxe foi conferida por leitura e `yaml.safe_load`.

PA-7 (`docs/engineering/achados-recorrentes.md`): sem ocorrência neste diff, que não toca permissões, entrada não confiável, cache nem SHA de ação.

## Achados
- A1 (recomendado) tests/test_pesos_teto.py:15 · `TETO_DO_JOB_S = 15 * 60` ainda cita `timeout-minutes: 15`, agora desatualizado; a margem do teste fica conservadora, sem falha, e já está no cartão CI-TESTES-LENTOS (mesmo registro do QA)

## Custo e rollback
Custo zero (`R-CUSTO`): repositório público, runner `ubuntu-24.04` padrão gratuito; `timeout-minutes` é só um teto, não aumenta a duração da execução que passa dentro do limite e só deixa de cancelar a que passaria de 10/15 min (medido: 333 a 849 s por execução; cancelamentos em 41555432664 e 41574683587). Pior caso: um job travado consome até 20/25 min antes de cair, dentro da franquia gratuita. Rollback: reverter o commit 1effb9e (três números e a asserção).
