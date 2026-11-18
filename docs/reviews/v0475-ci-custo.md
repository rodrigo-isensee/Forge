---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: d8e1b09b050f7455637234be5a9ccbc97c9d0ed5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.102, melhoria/v0475-ci-custo), revalidação

## Achados
- A4 (recomendado) tests/test_modelo_ci.py:29 · `git()` e os `bash -c` herdam `GIT_*` e `BASH_ENV`; com `GIT_DIR` herdado `Deteccao` falha (S1). Pre-push e forge-testes limpam `GIT_*`, então não bloqueia. AR-4; limpar como `tests/test_adotar.py:26`.
- A5 (recomendado) tests/test_modelo_ci.py:1 · tamanho (M14): 264 linhas contadas contra a base (`bin/forge-testes` 4, `ci.yml` 94, teste 166), um comportamento; o corpo do PR traz `teto: excedido, 264 linhas, <motivo>`.

## Sondas
- S1 · `GIT_DIR=<repo nu alheio> python3 -m unittest tests.test_modelo_ci.Deteccao` · espera: OK (teste isolado do ambiente) · obtido: `FAILED (errors=3)`

## Parecer
Aprovado (`R-REVIEW`). Delta lido: `forge-check parecer delta docs/reviews/v0475-ci-custo.md`, intervalo f59f7766..d8e1b09b, domínio código e testes (changelog.d, skills/ci-cd/SKILL.md, ci-docs.yml apagado, ci.yml, as duas specs de mutantes, tests/test_modelo_ci.py).

Achados do parecer anterior:
- **A1 (bloqueante) resolvido:** `ci.yml` usa `group: ci-${{ github.event.pull_request.number || github.ref }}`; o push na develop (`refs/heads/develop`) e o PR develop→homolog (número) ficam em grupos distintos e não se cancelam. O teste `Concorrencia` confere o grupo e a ausência de `head_ref`; o mutante M11 volta ao grupo por branch.
- **A2 (recomendado) resolvido:** um workflow só, sem `paths`; o job `mudanca` diz "só documento" apenas quando todos os arquivos do diff casam `*.md | docs/*`, e na dúvida (base vazia, zeros, commit ausente, diff vazio ou com erro) diz código. O único `ci` exige `mudanca` success e, com código, suíte `success`; com só documento, suíte `skipped` e nada mais. A suíte com `if:` sem função de estado herda `success()`: falha da detecção pula a suíte e o `ci` fica vermelho (fecha em falha). Base e cabeça entram por `env`, sem `${{ }}` em `run` (teste `Higiene`).
- **A3 (recomendado) resolvido:** a skill explica o grupo por número e por que juntar push e PR não evitava duplicata.

Testes de comportamento em bash: `Deteccao` roda o script real do modelo num repositório descartável (só documento, código, misto, `docs.txt`, base vazia, zeros, diff vazio); `CheckObrigatorio` roda o agregador real na tabela completa de resultados. Specs divididas: `v0475-ci-custo.json` (M1-M16) e `-2.json` (M17-M20), um mutante por guarda mudada, cada um apontando o teste do ramo de falha.

Ferramentas e provas citadas, sem refazer:
- `python3 -m unittest tests.test_modelo_ci`: 17 testes OK no d8e1b09b (rodei o teste novo).
- Mutação: vale o PQ-1 do autor (commit d8e1b09b); não rerrodei.
- CI: sem PR aberto neste passo; a suíte completa fica no CI do PR, obrigatório para o merge.

Neutralidade (`R-NEUTRO`) e ADR 0001: modelo com `{{COMANDO_PRONTO}}`, sem ferramenta de stack; checkout fixado por SHA com `persist-credentials: false`, permissões mínimas, timeout em todo job: ok.
