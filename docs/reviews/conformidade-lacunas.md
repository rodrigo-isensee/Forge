---
tipo: review
contrato: 1
pedido: conformidade-lacunas
branch: melhoria/conformidade-lacunas
commit: a0b8660
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: conformidade cobre `.claude-plugin/`, `.github/` e `tests/neutralidade.py`

Escopo: `hooks/conformidade.json` (3 entradas), 9 fixtures `tests/hooks/conformidade/protegido-*.json`, nota N6 da ADR 0009 e `CHANGELOG.md`.

## Conferido
- Entradas no mesmo formato de `tests/catraca.py`: `quem` `["tech-lead","doc"]`, `so_forge`, `branch` `melhoria/`, motivo claro. Nada existente foi alterado nem afrouxado; `.claude/settings.json` e o `denyWrite` não foram tocados.
- Testes escritos antes: 6 fixtures falharam sem a mudança (dev e tech-lead fora de `melhoria/*`, nos três caminhos) e as 3 de `tech-lead` em `melhoria/*` já passavam; todas passam com a mudança.
- A catraca acusa a alteração de `hooks/conformidade.json`, esperado: o PR precisa do rótulo `afrouxa-regra` do dono (a política fica mais restritiva, mas o arquivo é protegido).

## Riscos
- Os caminhos passam a exigir branch `melhoria/*` mesmo para o `tech-lead`; edições de `.github/` em outra branch de fábrica serão barradas, como as demais regras.

Parecer: aprovado. Sem itens que bloqueiam.
