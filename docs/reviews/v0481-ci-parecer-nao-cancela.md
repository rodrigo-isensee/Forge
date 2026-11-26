---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-parecer-nao-cancela
commit: b04f02200f86582e114a45fe233dbb900a184083
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E22.3, #913, 1ª rodada completa)

Diff lido: `b4ae1755..b04f0220` (merge-base com a develop), 4 arquivos, +130 -2; 47 linhas de código no `ci.yml` (H1 dentro do teto). Classe C (`forge-check classe`: protegido da catraca, `.github/workflows/ci.yml`).

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:41 · o `if:` do job obsoletas usa `github.event.pull_request.head.repo.full_name`, que o avaliador do scripts/ci-local (linha 274) recusa: ValueError em 3 testes de test_ci_local; ensinar o contexto ao ci-local ou pular o job lá (rodado local, cancelaria runs com o token do dono)
- A2 (bloqueante) tests/test_ci_local.py:479 · o marcador `run: |` + `set -euo pipefail` da sonda do lint passa a aparecer 2 vezes (o script do obsoletas abre igual): test_passo_novo_antes_do_lint_reprova falha em :483 (esperado 1, obtido 2); tornar o marcador único
- A3 (bloqueante) tests/test_falhas_no_resumo.py:241 · a trava "nenhuma permissão de escrita no ci.yml" reprova com o `actions: write` (ci.yml:45); restringir a trava ao resto do arquivo exige o rótulo e o destaque afrouxa-regra no título do PR, com o motivo, e o teste aceitar o write só no job obsoletas
- A4 (bloqueante) tests/test_catraca.py:4253 · a lista de timeouts do ci.yml não traz o 3 do job novo: test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore falha; incluir o "3" na posição do job e o job no comentário do teto
- A5 (bloqueante) tests/mutantes/v0481-ci-parecer-nao-cancela.json:1 · classe C sem mutantes declarados para as guardas novas (ci.yml:41, 60, 61, 62, 65, 68, 75 e o `||` da 75); um mutante por linha, cada um morto por teste de comportamento (o -le da 75 já é o A1 do QA)
- A6 (recomendado) .github/workflows/ci.yml:62 · `[ -n "$arquivos" ]` é redundante: lista vazia cai no `*` do case e já cancela; o mutante que a remove sobrevive como equivalente; tirar a guarda ou declará-la equivalente

## Parecer
Reprovado. O desenho atende o pedido: concurrency por run só em `pull_request` (push em develop, homolog e main e o `workflow_dispatch` seguem no grupo `ci-<ref>` com cancelamento), o job obsoletas não tem `needs` e não entra em agregador nem em check exigido, falha fechada nos cinco casos (sem `before`, outra ação, diff vazio, erro do compare, 300 arquivos ou mais), `actions: write` só no job, `timeout-minutes: 3`, só PR do próprio repositório. Entradas do evento só por `env:` e sempre entre aspas; nomes de arquivo só passam pelo `case`; o id do run vem do `--jq` numérico: sem injeção. O efeito já aparece no próprio PR: o envio só de parecer do QA (b2222c4a, run 45843905956) não cancelou o run 45843502262 do b04f0220, que seguiu até o fim.

O bloqueio é a suíte: o CI do head revisado está vermelho em 4 partes, por três módulos de teste existentes que o diff quebra (A1 a A4) e não ajustou, e falta a declaração de mutantes da classe C (A5). Correção numa volta única com o QA e a segurança.

Provas do review:
- CI do b04f0220 (run 45843502262), causa de cada vermelho lida no log: parte 3.12 5/5 e 3.14 5/5, test_ci_local (A1, A2); parte 3.14 3/5, test_falhas_no_resumo.Fiacao.test_leitor_nao_muda_permissoes_nem_afrouxa_o_ci (A3); parte 3.12 2/5, test_catraca.Workflows.test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore (A4). `bateria (pareceres)` e `catraca` (rótulo do dono por ser ci.yml, R-CONFORMIDADE) esperam o parecer ou o rótulo.
- Local, no clone: `python3 -m unittest test_ci_local` na base b4ae1755: 74 testes OK; no b04f0220: 1 falha e 3 erros, os mesmos do CI. `test_ci_nao_cancela_parecer`: verde.
- Sem linha ci: o CI do head não está verde.
