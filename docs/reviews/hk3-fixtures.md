---
tipo: review
contrato: 1
pedido: hk3-fixtures
branch: melhoria/hk3-fixtures
commit: 7c4c7968fe4683837207875e80eeac40970b4dc3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: hk3-fixtures

## Achados

## Parecer
Aprovado. Delta lido inteiro (base 5ce822d): três fixtures de `tests/hooks/parecer/` com `home/wtx` trocado por `ctx/wtx` (7 linhas) e o fragmento `changelog.d/hk3-fixtures.md`.

- Escopo (`R-REVIEW`): só dados de teste e o fragmento; nenhum arquivo de `hooks/`; o que cada caso testa não muda (o `worktree` da fixture e os caminhos de `command` e `cwd` mudam juntos, o `esperado` fica igual).
- Teto M14: 14 linhas de código e teste contáveis (as fixtures ficam fora da contagem); sem excedente.
- Prova: `scripts/verificar-contribuicao.sh` contra `origin/develop` neste head sai com 0 ("nenhum segredo nem caminho pessoal"); `grep` do padrão de caminho pessoal em `tests/hooks` e `tests/fixtures` não acha mais ocorrência.
- Fragmento no formato (`### Corrigido`), versão não tocada (ADR 0006); `R-NEUTRO` e `R-CUSTO` preservadas.
- Achados recorrentes (PA-7): nenhum item se aplica ao delta; nenhuma linha AR nova.
- Segurança e QA têm pareceres próprios (outras delegações).
