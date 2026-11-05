---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/release-suite-paralela
commit: 6652f6b1898c91866a18e128ddbd1927c76b0277
parecer: aprovado
escopo: completo
revisor: forge:qa-engineer
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: release-suite-paralela (E24)

Código 6652f6b, head testado df7f62f (só pareceres depois do código). Base f54d9b7. Sem especificação de UX nem E2E de navegador: a obrigação é o escopo do E24 no pedido (a Release roda a suíte com `scripts/suite-paralela.py`, `setup-python` como o CI, teto 25 min).

## Achados
- A1 (recomendado) tests/test_volta_por_delta.py:625 · na 1ª rodada completa (carga alta), PqDeMerge.test_etapas_de_merge_trazem_o_pq_por_ancestralidade_da_base falhou (gerar rc 1 != 0, stderr vazio); isolado, 3 rodadas do módulo e a rodada seguinte passaram. Instável, fora do diff.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E24-1: o passo da Release chama o script paralelo | `test_ci_local` (asserção nova `python3 scripts/suite-paralela.py` e `unittest discover` ausente) + leitura do `release.yml` | passo antigo em série não volta | passou |
| E24-2: `setup-python` igual ao CI | leitura: SHA 6d4fd22b… (v7.1.0) e `3.12`, iguais ao job da bateria do `ci.yml` | n/a | passou |
| E24-3: teto 25 min | leitura: `timeout-minutes: 25` (era 20) | n/a | passou |
| E24-4: gatilho, permissões e publicação intactos | `git diff f54d9b7..6652f6b -- .github`: 9 linhas mudadas, só comentário, teto, `setup-python` e o passo de testes; `on: push main`, `contents: write`, checkout e passo Tag e release iguais | n/a | passou |
| E24-5: o passo roda de ponta a ponta | `python3 scripts/suite-paralela.py` na worktree: rc=0, 2516 testes, 89 módulos, 4 processos, 847 s, skipped=28 | n/a | passou |

## Execução real (head df7f62f)
- `.githooks/pre-push --status`: nenhuma suíte rodando. `.githooks/pre-push --suite`: 2516 testes, rc=1 por 1 falha (A1), de 873 s. Rodada de ponta a ponta do script, em seguida: rc=0, 2516 testes, mesma contagem, `OK (skipped=28)`.
- `scripts/validar-plugin.sh`: rc=0 (Validation passed). `bin/forge-check docs`: rc=0.
- Vermelho antes do verde: `bin/forge-testes --vermelho f54d9b7683d206bc1b0ba1900b86d22841311fc7 --modulos test_ci_local`, rc=0 (abre com `vermelho: base=f54d9b7683d2 head=df7f62f90ae0`; revertidos à base: release.yml e pareceres); a asserção nova do release cai na base e passa no head. A rodada de repositório inteiro do `--vermelho` ficou com um "sem veredito" fora do módulo tocado, sem relação com o diff.
- Mutação: não se aplica (o diff não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`).
- Bugs: nenhum.

## Parecer
Aprovado. A única ocorrência é a instabilidade A1, recomendada, que não devolve. O A1 do review (docs/devops/suite-paralela-d4.md) foi cortado e não se repete.
