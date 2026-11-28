---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: 054d4103ddb0c0364136575a4b36bbd3a2708164
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-27
---
# Review de devops: v0481 (espera amarela, #948, E47.9, delta da volta 1)

- ci: 054d4103ddb0c0364136575a4b36bbd3a2708164 verde

## Achados
- A1 (recomendado) .github/workflows/ci.yml:1 · actionlint e zizmor ausentes na estação; o delta de ci.yml e catraca.yml não rodou os dois. Instalar por scripts/preparar-estacao.sh.

## Detalhes
Aprovado. Delta lido: `git diff 5d293a8b..054d4103 -- .github/workflows` (três linhas em ci.yml, três em catraca.yml).

- Nomes exigidos: o job `agregador` segue chamado `bateria` e o `catraca` segue `catraca` quando o sufixo é vazio; `bateria (python 3.14)` não foi tocado. O sufixo vira `' (espera parecer)'` / `' (espera rótulo)'` só com todos os `needs` em `success` (`bateria`, `pareceres`, `verificacoes`, `partes-doze`, `pulados-doze` no agregador, todos presentes no `needs:` da linha 687; `conferencia` na catraca). Com qualquer um vermelho, cancelado ou pulado o nome fica exato e o check exigido reporta o vermelho. Com os outros verdes e a espera, o nome muda e o check exigido fica pendente, barrando a junção. `A && B || ''` com `espera` vazia dá `''`, como esperado.
- Falha fechada mais estrita: o `case` só segue (espera) quando o último check do head é `nenhum|failure|cancelled|timed_out|action_required|stale`; verde, pulado, neutro, em andamento (conclusão `null`) e erro da API saem com 1. Troca `!= success` por lista permitida, que cobre mais estados e não afrouxa nada.
- YAML: sem parser de YAML na estação (sem PyYAML nem ruby); leitura. Os escalares simples de `name:` não têm `: ` nem ` #`, as aspas `''` ficam dentro de `${{ }}`, e o `case` está em bloco `run: |`. Sem `continue-on-error`, `[skip ci]` nem check desligado; ações fixadas por SHA como antes; nada escreve na `main` (`R-MAIN`); permissões inalteradas.
- CI (G3), `gh pr checks 948` no `Revisar-sha`: verdes suíte 1..5/5, instalação 3.14, `bateria (python 3.14)`, passos, verificações, teto de pulados, árvore. Vermelhos esperados: `bateria (pareceres)`, `bateria`, `catraca` (o brief os exclui) e `catraca (conferência)`, que falha só pela exigência do rótulo `afrouxa-regra` do dono sobre `.github/` e `tests/catraca.py`; os "confira" não barram. O `bateria (pareceres)` falha com rc 1 porque o job roda o `catraca.py` da base (sem o rc 3 desta entrega) e os pareceres estão desatualizados; é a introdução, que só vale depois do merge.
- PQ-3 não é rc 0 enquanto pareceres e rótulo faltam; a leitura acima é o que vale.

## Custo e rollback
Sem job novo nem custo de dinheiro (`R-CUSTO`). Rollback: reverter o commit; nada de estado externo.
