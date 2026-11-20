---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-onde
commit: b11db7154c0b4eb2d91b50a15242e46ed7aa297b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-ae1-onde

Etapa E58.16 do pedido v0478, revalidação depois da volta (E58.13). A rodada anterior (head `bef021c1`, A1 e A2 recomendados) fica no git.

Gatilhos: controle do Forge (ferramenta que produz prova de estado), entrada livre repassada a processo externo (git e gh).

## Resumo
Delta lido (`forge-check parecer delta`, `bef021c1..b11db715`): no domínio, só `bin/forge_onde.py`; fora dele, `tests/test_forge_onde.py`, `tests/mutantes/v0478-ae1-onde-7.json`, `changelog.d/v0479-ae1-onde.md` e os pareceres de review e QA. Os merges `db6da3a2` e `5d42f3e5` só trouxeram pareceres da própria branch.

Estado dos achados anteriores:
- A1 corrigido. `bin/forge_onde.py:136-137`: no tipo `commit`, o sha lido que não começa pelo alvo sai `nao-verificavel` e rc 2. O alvo só passa pelo `SHA` (`:17`, minúsculo), então a comparação com a saída do `rev-parse` (sempre minúscula) não recusa alvo legítimo. O `mergeCommit` do PR (`:68`) já exige 40 hex, que o git resolve pelo objeto. Teste: `tests/test_forge_onde.py:142`. Sonda ponta a ponta em repositório descartável em `$TMPDIR` (tag de 7 hex de A apontando para B): `forge-check onde <7hex>` devolveu `nao-verificavel (sha ambíguo com ref ...)` rc 2; com o sha de 40 hex leu A.
- A2 corrigido. `bin/forge_onde.py:145-149`: `executar` captura `subprocess.TimeoutExpired` e devolve 2; o despacho (`bin/forge-check:10439`) chama esse `executar`, então o `return 1` genérico do forge-check não é alcançado pelo `onde`. Teste: `tests/test_forge_onde.py:151`.

Nada novo no delta: sem escrita, sem rede além do que já havia, sem segredo, saída ainda passa por `seguro`.

Suíte: a inteira não foi rodada aqui (brief: sem suíte local; o CI do PR é o portão). Rodei o teste do subcomando: `python3 -m unittest tests.test_forge_onde`, 32 testes, OK.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura estática e sondas locais com git e o interpretador da stack em `$TMPDIR`. Ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint, osv-scanner; nenhum segredo, workflow ou dependência nova no delta.
