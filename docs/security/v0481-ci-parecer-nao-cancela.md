---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: b04f02200f86582e114a45fe233dbb900a184083
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E22.5, PR #913, 1.ª rodada completa)

Lido: `git diff b4ae1755..b04f0220` inteiro (`.github/workflows/ci.yml`, `tests/test_ci_nao_cancela_parecer.py`, `tests/pesos-d4.json`, o fragmento do changelog).

CI do head b04f0220 (run 45843502262) vermelho; a causa foi lida nas anotações de cada job e reproduzida localmente. `bateria` e `bateria (python 3.14)` reprovam porque 6 partes da suíte estão vermelhas (A1, A2, A3). `bateria (pareceres)` espera os pareceres (esperado nesta etapa). `catraca` reprova no passo de regras porque a mudança em workflow pede o rótulo `afrouxa-regra` do dono (R-CONFORMIDADE; reproduzido com `tests/catraca.py --base b4ae1755`): é decisão do usuário, não achado.

## Gatilhos
Gatilhos: workflow de CI (permissão `actions: write` nova), uso de entradas do evento `pull_request`, checks exigidos.

## Achados
- A1 (bloqueante) tests/test_falhas_no_resumo.py:241 · a guarda "nenhuma permissão de escrita no ci.yml" reprova com o actions: write novo (ci.yml:45). Correção mínima: o job num workflow próprio (ex.: obsoletas.yml), com o mesmo if e timeout, sem tocar a guarda; afrouxá-la só com decisão do dono
- A2 (bloqueante) tests/test_catraca.py:4253 · a lista de timeouts do ci.yml não prevê o 3 do job novo (ci.yml:43); com A1 por workflow próprio a lista volta a bater, e o arquivo novo cai na regra de um timeout por job (test_catraca.py:4241)
- A3 (bloqueante) scripts/ci-local:274 · o simulador do CI não conhece o contexto github.event.pull_request.head.repo.full_name do if do job novo (ci.yml:41) e 3 testes de tests/test_ci_local.py dão ValueError; some com A1 por workflow próprio, ou o simulador aprende o contexto

## Sondas
- S1 · python3 -m unittest tests.test_falhas_no_resumo.Fiacao.test_leitor_nao_muda_permissoes_nem_afrouxa_o_ci · espera: OK · obtido: FAIL, 'write' unexpectedly found
- S2 · python3 -m unittest tests.test_catraca.Workflows.test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore · espera: OK · obtido: FAIL, lista de timeouts com um 3 a mais
- S3 · python3 -m unittest tests.test_ci_local.MatrizNeedsEAgregadorTest · espera: OK · obtido: 3 ERROR, condição sem suporte (contexto desconhecido)

## Detalhe dos achados
A1 é o achado de segurança. A guarda de `tests/test_falhas_no_resumo.py:241` existe para que nenhum job do `ci.yml` ganhe escrita, e o PR a quebra sem marcar a mudança. Caminho de ataque: hoje nenhum direto, porque o job está bem contido (ver abaixo). Mas trocar a guarda deixa a próxima escrita no `ci.yml` passar sem leitura. Severidade baixa; esforço P; dono: o autor do E22.1 (`devops-engineer`). A correção preferida (workflow próprio) mantém a guarda e resolve A2 e A3 juntos. Ela também separa o token `actions: write` do arquivo que roda a suíte. A2 e A3 são defeitos provados (CI vermelho), esforço P, mesmo dono.

O resto do desenho está correto, com a evidência:

- **Permissão `actions: write`:** só no job `obsoletas` (`.github/workflows/ci.yml:44-46`). O topo segue `contents: read` e o padrão do repositório é `read`. O job roda só em PR do próprio repositório (`ci.yml:41`), sem checkout, sem ação de terceiros e com `timeout-minutes: 3` (`ci.yml:43`). Fork não recebe o job nem token de escrita. Quem abre PR do próprio repositório já pode mudar o `ci.yml` no PR, e com ele as permissões dos jobs; o ganho de um atacante com esse token é marginal.
- **Entradas do evento sem injeção:** `head_ref`, `head.sha`, `before`, `action`, `run_id` e `repository` chegam ao script só por `env:` (`ci.yml:49-56`) e são usados entre aspas (`ci.yml:61`, `ci.yml:72`). O próprio teste confere que o script não tem `${{` (`tests/test_ci_nao_cancela_parecer.py:44`). O `id` vem da API e só vai a `[ -lt ]` e ao `gh run cancel`, entre aspas (`ci.yml:75`). O script passa no shellcheck sem aviso.
- **Falha fechada:** a decisão "só parecer" exige `synchronize`, `before` não vazio, o compare sem erro, lista não vazia e menos de 300 arquivos (`ci.yml:60-62`); qualquer falha cai no cancelamento de hoje. O compare corta a lista em 300 arquivos, e com 300 o job cancela; se a paginação repetisse a lista, a contagem subiria e também cancelaria. O casamento é por prefixo com a barra (`docs/reviews/*`), e `docs/reviews-x/` não passa (teste `test_outros_docs_e_o_devops_nao_contam_como_parecer`).
- **Checks exigidos:** a regra da `develop` exige `bateria`, `bateria (python 3.14)` e `catraca` (lido pela API de rulesets). O job novo não entra no `needs` do agregador (`ci.yml:899`, inalterado) e não é exigido. Cada run de PR tem grupo próprio (`ci.yml:35`), então a suíte do head novo roda inteira sempre. Nenhum check exigido deixa de rodar.
- **Envio que se diz parecer:** quem envia só `docs/security/` (inclusive `aceites/` ou `ameacas/`) apenas evita o cancelamento do run anterior. O run do head novo roda inteiro e os portões continuam lendo o head novo. Com force-push, o compare de três pontos pode listar só docs; o efeito é o mesmo (um run antigo a mais), sem portão afetado.

Fora da segurança, para o `tech-lead` (sem caminho de ataque): `gh run list --branch` casa pelo nome do ramo, então um PR do repositório pode cancelar o run de um PR de fork com o mesmo nome de ramo. E runs em `waiting`, `pending` ou `requested` não são cancelados (só custo de minutos, e o repositório é público).

### Aperta, neutro, afrouxa
- **Aperta:** o cancelamento em PR passa a ser um job explícito, com permissão própria e mínima, falha fechada e teste com `gh` falso, em vez de efeito colateral do grupo de concorrência.
- **Neutro:** checks exigidos e agregadores; push em `develop`, `homolog` e `main` e o `workflow_dispatch` seguem cancelando (`ci.yml:36`); nenhuma entrada do evento interpolada no script.
- **Afrouxa:** como está, quebra a guarda de escrita do `ci.yml` (A1). Um job disparado por PR passa a ter `actions: write` (antes, nenhum job do `ci.yml` tinha); fica mitigado pelo filtro de mesmo repositório, sem checkout e sem ação de terceiros. E o envio só de parecer deixa o run anterior seguir (mais minutos de runner, sem custo em repositório público). A mudança em workflow exige o rótulo `afrouxa-regra` do dono na catraca (R-CONFORMIDADE), que é decisão do usuário (R-DECISAO).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Usados: leitura do diff, `shellcheck` sobre o script extraído do job, o teste novo (`python3 -m unittest tests.test_ci_nao_cancela_parecer`: 5 testes OK), os módulos vermelhos do CI (S1 a S3), a API de rulesets e de check runs. Ausentes no ambiente: `zizmor`, `actionlint`, `gitleaks` (lacuna registrada; sem segredo no diff, lido à mão).
