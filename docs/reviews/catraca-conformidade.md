---
tipo: review
contrato: 1
pedido: catraca-conformidade
branch: melhoria/catraca-conformidade
commit: 0d34f53
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: catraca confere hooks/conformidade.json

Escopo: `origin/develop..0d34f53` (1 commit): `tests/catraca.py`, `tests/test_catraca.py`, `CHANGELOG.md`. Referências: ADR 0008, R-CONFORMIDADE.

## Checklist
- Faz o pedido: acusa remoção de caminho, ampliação de `quem`/`acoes`/`papeis`, perda ou troca de `so_forge`/`branch` e verbo de instalação removido; acrescentar ou restringir não acusa. Nada mais.
- Nenhuma checagem existente foi alterada; a nova entra só como soma em `violacoes_das_regras`. Violação é R-CONFORMIDADE (não R-CUSTO), então o rótulo do dono libera.
- Política ausente na base não acusa (arquivo novo); ausente no head acusa tudo (base com conteúdo, head vazio).
- Testes: 13 casos novos; vermelho antes (9 falhas sem a mudança), verde depois (238 OK). Cobrem remoção, ampliação, branch, acréscimo e rótulo.
- Só biblioteca padrão; sem custo; neutro.

## Observações (não bloqueiam)
- `papel_padrao`/`sem_agent_type` acusam em qualquer mudança (conservador).
- Como `tests/catraca.py` é protegido, este PR exige o rótulo `afrouxa-regra` do dono.

Parecer: **aprovado**.
