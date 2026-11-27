---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-arvore-envio
commit: 1567d509452159c268e52384f694a7bf3881bdda
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (PR #932, corte do envio do F6, E32.29)

1ª rodada completa sobre `11fc1867..1567d509` (14 arquivos): job `arvore-envio` e `scripts/arvore-testada.py --do-pr`.

Gatilhos: pipeline de CI (portão do push na develop), token do workflow, controle que afrouxa regra (R-FLUXO, rótulo `afrouxa-regra`).

## Resumo
Aprovado sem achado. A prova do PR exige, nesta ordem, `scripts/arvore-testada.py:139-170` e `:173-201`: push na develop do próprio `ci.yml` (`GITHUB_WORKFLOW_REF`), PR do próprio repositório mesclado exatamente neste commit (`merge_commit_sha`), base `develop`, árvore do head igual à do commit, develop anterior ancestral do head (`compare`), run de `pull_request` do `ci.yml` do mesmo repositório e do mesmo head, concluído, ligado ao mesmo número com base `develop`, o run mais recente decide, e um único job `bateria` em `success` com `run_id` e `run_attempt` iguais aos do run. Falha fechada em toda falta, em exceção de rede ou JSON e em falha do próprio job (o agregador exige `arvore-envio` em success, `.github/workflows/ci.yml:194`).

## As quatro forjas pedidas
- **Outro run:** filtro por `head_sha`, `path`, evento e número do PR; o maior `run_id` válido decide (run vermelho mais novo reprova). Teste: `tests/test_arvore_testada.py:272` (casos 1 e 4) e `:299`.
- **Outro repositório:** `repository.full_name` e `head_repository.full_name` do run e `head.repo.full_name` do PR iguais ao repositório; PR de fork nunca prova (roda a suíte). Teste: `:272` (caso 3) e `:305`.
- **Outra base:** `base.ref == develop` no PR e no run, base do run ancestral do head. A garantia de fundo é o `compare` da develop anterior com o head (`scripts/arvore-testada.py:165`): como a develop só anda para a frente, qualquer base anterior dela também é ancestral do head e a árvore testada no merge ref é a do head. Teste: `:272` (caso 1) e `:305`.
- **Tentativa antiga:** o job precisa ter `run_attempt` igual ao do run (a listagem de jobs devolve a tentativa mais recente). Teste: `:272` (caso 4).

**Check-runs:** `--do-pr` não lê check-runs nem status de commit (só `actions/runs` e `actions/runs/<id>/jobs`); conferido por grep e por `tests/test_arvore_testada.py:181`. A leitura de check-runs que existe no `ci.yml` (gate de commit só de parecer, `.github/workflows/ci.yml:462`) é anterior a este PR e não foi tocada.

**Token e execução:** o `GH_TOKEN` (`contents`, `actions` e `pull-requests` só leitura) fica só no passo da prova; checkout sem credencial persistida; o código executado é o da develop já mesclada (`python3 -I`); a saída só leva o motivo, e a exceção vira o nome do tipo, sem corpo de resposta. A saída `provada` só vale `true` ou `false` escrita pelo próprio passo.

## Observações fora do domínio (para o `tech-lead` e o `qa-engineer`)
- **Eficácia provável nula:** o campo `pull_requests` de um run aparece vazio depois que o PR é mesclado. Sonda (só leitura) no PR #851, já mesclado: o run `45388263251` do `ci.yml` no head `90f482f2` devolve `pull_requests: []`; no #932, aberto, o mesmo campo traz o PR. Se no push da develop o campo já estiver vazio, `--do-pr` nunca prova e a suíte do push sempre roda: falha fechada (sem risco de segurança), mas o corte do F6 não economiza nada. Vale conferir no primeiro push depois do merge.
- **Residual aceito pelo desenho:** se o campo fosse populado de forma dinâmica, `base.sha` seria a base atual, não a do momento do run; o ganho de um retarget seria pular a suíte do push para uma árvore cujo check `bateria` no mesmo sha a proteção de branch já aceita. Sem caminho realista além do que o portão do PR já permite.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes afetados rodados localmente: `tests.test_arvore_testada` (30 testes, OK). CI do PR: suíte e passos verdes no head; `bateria` e `catraca` vermelhas pelo que falta da integração (pareceres e rótulo `afrouxa-regra`, segundo o brief). `zizmor` e `actionlint` não foram usados (fora do PATH): lacuna registrada.
