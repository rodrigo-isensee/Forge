---
tipo: qa
contrato: 1
pedido: hk3-fixtures
branch: melhoria/hk3-fixtures
commit: 7c4c7968fe4683837207875e80eeac40970b4dc3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: hk3-fixtures

Delta sobre a base 5ce822d: três fixtures de `tests/hooks/parecer/` (`home/wtx` para `ctx/wtx`, 7 linhas de dados de teste) e o fragmento de changelog. Nenhum código de produção mudou.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (fixtures com nome neutro, mesmo comportamento) | `tests.test_hooks_parecer_pasta` sobre 7c4c796 | pasta que não existe, `..` de link, `-C` com `..` | passou (1 teste, OK) |
| PQ-1 do pedido (verificador de caminho pessoal) | `scripts/verificar-contribuicao.sh origin/develop` | caminho pessoal no diff | passou: "ok: nenhum segredo nem caminho pessoal no diff" |

## Cenários e resultado real
- Diff conferido: nas três fixtures, `worktree` e `command`/`cwd` mudaram juntos para `ctx/wtx`; nenhuma divergência entre eles.
- Vermelho antes do verde: não se aplica (dado de teste sem regra nova; o comportamento esperado das fixtures não mudou).
- Mutante manual em cópia descartável (`ctx/wtx/lnk` trocado por `ctx/zzz/lnk` na fixture do link): `tests.test_hooks_parecer_pasta` falhou (`FAILED (failures=1)`), logo as fixtures são lidas e a troca de caminho é detectada.
- Fixtures vizinhas ainda com `home/wtx` não entram no diff e o verificador as aceita; fora do escopo do pedido.
- Suíte completa não rodada aqui (corte 1 da decisão ACELERA-RODADA); roda no pre-push.
