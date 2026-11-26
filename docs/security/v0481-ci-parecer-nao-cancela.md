---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: 8e9f5704f52b32e0419ab0b7bbc066f17e6f013a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E22.9, PR #913, volta por delta)

Delta lido: `forge-check parecer delta` de b04f0220..8e9f5704. No domínio: `.github/workflows/ci.yml`, `.github/workflows/obsoletas.yml` (novo) e `tests/test_catraca.py`. Fora do domínio, lidos só como prova: `tests/test_ci_nao_cancela_parecer.py` e `tests/mutantes/v0481-ci-parecer-nao-cancela.json`. A rodada anterior está no git (41f6b91a).

CI do head 8e9f5704 vermelho, e a causa é o próprio delta (A4). O workflow Obsoletas (run 45847608652) cancelou o run do CI do mesmo head (run 45847608038). Por isso `bateria` e `bateria (python 3.14)` falham nos agregadores, com as partes canceladas. Também falha `catraca` (run 45847608023), porque a mudança em `ci.yml` e em `obsoletas.yml` pede o rótulo `afrouxa-regra` (R-CONFORMIDADE). Esse rótulo é decisão do usuário, não achado.

Gatilhos: workflow de CI (`actions: write` em workflow novo disparado por `pull_request`), entradas do evento, checks exigidos.

## Achados
- A1 (bloqueante) tests/test_falhas_no_resumo.py:241 · resolvido: o job foi para obsoletas.yml, a guarda sem escrita no ci.yml ficou intacta e passa (Fiacao OK)
- A2 (bloqueante) tests/test_catraca.py:4238 · resolvido: obsoletas.yml entrou na regra de um timeout por job, e a lista do ci.yml voltou a bater
- A3 (bloqueante) scripts/ci-local:274 · resolvido: o if com head.repo.full_name saiu do ci.yml, e tests.test_ci_local passa
- A4 (bloqueante) .github/workflows/obsoletas.yml:52 · o RUN_ID é o id do run do Obsoletas, não do CI, e o CI do mesmo push tem id menor, então é cancelado (S1). Correção mínima: cancelar só run com head_sha diferente de HEAD_SHA, mantendo id < RUN_ID e a origem; o teste passa a listar um run do CI com o head atual

## Sondas
- S1 · `gh api "repos/{owner}/{repo}/actions/runs?head_sha=8e9f5704f52b32e0419ab0b7bbc066f17e6f013a" --jq '.workflow_runs[] | "\(.id) \(.name) \(.conclusion)"'` · espera: CI do head não cancelado · obtido: `45847608038 CI cancelled` (log do Obsoletas 45847608652: cancel 45847608038)

## Detalhe dos achados
A4 é um defeito provado, não uma vulnerabilidade. Os checks exigidos falham fechados: o run cancelado deixa `bateria` vermelha e não verde, então nenhum portão é contornado. Mas o workflow faz o oposto do objetivo: cancela a suíte do head que acabou de chegar, em todo envio com código. Num envio só de parecer, o script sai antes de cancelar, e por isso o run 45848951417 do head 58912106 seguiu. Os ids de run são únicos no repositório e crescem com a criação. O Obsoletas e o CI do mesmo evento nascem juntos, em ordem que não se pode garantir, então comparar com `github.run_id` de outro workflow não separa "anterior" de "atual". O teste `tests/test_ci_nao_cancela_parecer.py:22` e o mutante M12 assumem que o próprio RUN_ID aparece na lista do `ci.yml`, o que não acontece. Correção mínima (dono: `devops-engineer`, esforço P): o `--jq` passa a emitir também `.head_sha`, e só cai o run com `head_sha != HEAD_SHA`, origem igual a `REPO` e `id < RUN_ID`. A condição de id fica para que o Obsoletas de um envio antigo, se atrasar, não cancele o CI de um envio mais novo. O gh falso lista um run do CI com o head atual e id menor que o RUN_ID, e esse run não pode cair; um mutante para essa condição.

O resto do delta está correto:
- **`actions: write` isolado:** só em `obsoletas.yml:22`, no job, com o topo em `contents: read` (`obsoletas.yml:12-13`) e `timeout-minutes: 3`. Não há checkout nem ação de terceiros. O `ci.yml` volta a não ter escrita (A1).
- **Filtro de origem:** o job só roda em PR do próprio repositório (`obsoletas.yml:18`). O cancelamento exige `head_repository.full_name == REPO` (`obsoletas.yml:50-52`), então o run de um fork com o mesmo nome de ramo não cai (M11 morto). Se `head_repository` vier nulo (fork apagado), o jq imprime `null`, que difere de `REPO`, e o run não é cancelado (falha fechada).
- **Entradas do evento:** seguem só por `env:` e entre aspas. O script extraído passa no `shellcheck` sem aviso. Um id não numérico faz o `[ -lt ]` falhar dentro do `if`, e nada é cancelado.
- **Guarda redundante removida (A6 do review):** sem `[ -n "$arquivos" ]`, uma lista vazia vira uma linha vazia no `<<<`. Essa linha não casa com as pastas de parecer, então `so_parecer=false` e o job cancela. A falha continua fechada (teste `rodar("")`).
- **Guarda do ci.yml:** a guarda `test_falhas_no_resumo.py:241` não foi tocada. O teste novo também confere que só há um `actions: write`, no `obsoletas.yml`, e nenhuma escrita no `ci.yml`.

### Aperta, neutro, afrouxa
- **Aperta:** o token `actions: write` sai do arquivo que roda a suíte, e a guarda sem escrita no `ci.yml` volta a valer sem afrouxamento. O cancelamento agora filtra a origem do run, e o fork com o mesmo ramo não cai. Os 14 mutantes morreram.
- **Neutro:** checks exigidos e agregadores (o Obsoletas não é exigido); push nas branches de integração segue cancelando (`ci.yml:36`, M14); a injeção pelo evento segue fechada; a remoção da guarda redundante.
- **Afrouxa:** passa a existir um segundo workflow disparado por `pull_request` com escrita em `actions`. Fica restrito a PR do próprio repositório, sem checkout, e quem abre esse PR já pode editar workflows. Por A4, ele hoje cancela a suíte do próprio head (efeito de disponibilidade, não de portão). O rótulo `afrouxa-regra` é decisão do usuário (R-DECISAO).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Usados: o diff do delta; `python3 -m unittest tests.test_ci_nao_cancela_parecer tests.test_falhas_no_resumo.Fiacao tests.test_catraca.Workflows tests.test_ci_local` (89 testes, OK); `bin/forge-mutante tests/mutantes/v0481-ci-parecer-nao-cancela.json` (M1 a M14 morreram); `shellcheck` sobre o script extraído; a API de runs e de check runs e os logs dos runs 45847608652 e 45847608023. Não estavam no ambiente: `zizmor`, `actionlint` e `gitleaks`. É lacuna; o diff foi lido à mão e não tem segredo.
