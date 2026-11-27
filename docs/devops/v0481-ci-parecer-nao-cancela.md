---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: bb551ad698124bebf2dcb2511719913434d668a3
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-27
---
# Review de devops: v0481-ci-parecer-nao-cancela (#913, 1ª rodada)

## Parecer
Aprovado, sem achado bloqueante. Revisão por instância que não é a autora, sobre o head `bb551ad` (clone de revisão próprio, head remoto).

- ci: bb551ad698124bebf2dcb2511719913434d668a3 verde

- Permissões: `ci.yml` segue com `contents: read` e sem escrita. O `actions: write` fica só no job de `obsoletas.yml` (`:22`), com `contents: read`; o nível do workflow é `contents: read`. Sem ação de terceiros (nada a fixar por SHA), só `gh` do runner.
- Gatilho e fork: `pull_request` (nunca `pull_request_target`) e `if` do job exige `head.repo.full_name == github.repository` (`:18`); no fork o token já vem sem escrita. O laço ainda confere `origem = REPO`.
- Entrada não confiável: `HEAD_REF`, `HEAD_SHA`, `BEFORE` e os demais entram por `env:` e vão entre aspas; nada de `${{ }}` dentro do `run:`. `shellcheck -s bash` limpo no corpo do passo.
- Concorrência: grupo por `run_id` em PR e `cancel-in-progress` falso (`ci.yml:34`); push nas branches de integração e `workflow_dispatch` seguem com o grupo por ref e cancelando. Rerun mantém o `run_id`, então não duplica grupo.
- Guarda contra derrubar o próprio head: `sha != HEAD_SHA` e `id < RUN_ID` (`obsoletas.yml:53`). Cobre a corrida entre o CI e o Obsoletas do mesmo push; o teste `tests/test_ci_nao_cancela_parecer.py` e o mutante declarado estão na branch e passaram no CI.
- Falha fechada: erro do `gh api compare` (404 após reescrita de histórico, 300 arquivos ou mais, `BEFORE` vazio, lista vazia) deixa `so_parecer=false` e cai no cancelamento normal; só um envio provadamente restrito a `docs/reviews|qa|security` poupa os runs. `set -euo pipefail` faz o job falhar, não passar em falso. Não é check exigido nem entra em agregador (conferido: o agregador `bateria` não o lista).
- Custo (`R-CUSTO`): nenhum serviço novo; runner `ubuntu-26.04`, o mesmo do `ci.yml`; `timeout-minutes: 3`; job de 3 s. O custo extra é a suíte do head revisado terminar no envio só de parecer, o objetivo da mudança.
- `R-MAIN`, `R-VERIFY`: nada escreve na `main`, sem `continue-on-error`, sem `[skip ci]`. O `|| echo` no `gh run cancel` cobre só run que já terminou.
- CI do `Revisar-sha` (`gh run view 45900693971`: `pull_request`, head `bb551ad`): suíte python 3.12 e 3.14 (10 partes), passos, verificações longas, teto de pulados, instalação e `catraca`, `cancela runs obsoletos do PR`: verdes. Fora da conta, como manda G3: `bateria`, `bateria (pareceres)` e `catraca` esperam o parecer ou o rótulo (`bateria` e `bateria (pareceres)` aparecem `fail`, em 3 s e 8 s, por isso).
- Ferramentas: `actionlint` e `zizmor` ausentes do PATH desta estação (lacuna, ver A3); o job de passos do CI as roda sobre esses arquivos e passou.

## Achados
- A1 (recomendado) .github/workflows/obsoletas.yml:18 · PR de fork não tem cancelamento (o `if` o pula e o `ci.yml` não cancela mais): cada push de fork empilha uma suíte inteira. Hoje o repositório não recebe fork; se passar a receber, cobrir com cancelamento no `ci.yml` só para fork.
- A2 (recomendado) .github/workflows/obsoletas.yml:53 · Se o Obsoletas falhar (rede, API), os runs velhos não são cancelados e ninguém é avisado, pois o job não é exigido: custo de minutos some sem sinal. Medir minutos por release (`forge-cota-ci`) já cobre; considerar contar runs de PR concorrentes.
- A3 (recomendado) .github/workflows/obsoletas.yml:1 · `actionlint` e `zizmor` ausentes na estação do revisor; instalar por `scripts/preparar-estacao.sh`. A validação dos dois ficou no CI.

## Risco
Corrida residual: o `ci.yml` e o `obsoletas` correm em paralelo; um run do head antigo que entre em `in_progress` depois da listagem escapa do cancelamento e termina (custo, não correção). Aceitável.
