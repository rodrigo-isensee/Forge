---
tipo: revisao-devops
contrato: 1
pedido: versao-033
branch: melhoria/catraca-fork
commit: 838803f4c8da680b589f47f022aebe9c2e81e25b
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: catraca-fork

## Parecer
Aprovado. Sem achado bloqueante.

- .github/workflows/ci.yml (passo de pareceres): `HEAD_REPO` e `BASE_REPO` entram por `env:` e só o Python os lê; nenhuma expressão nova em `run:`. `permissions`, SHAs de ações e `timeout-minutes` intocados. Sem `continue-on-error`, check desligado ou teste pulado.
- tests/catraca.py: falha fechada quando os repositórios diferem, inclusive `head.repo` nulo (fork apagado), antes das promoções (um fork com ramo `develop` para a homolog também é recusado). Os dois vazios só ocorrem fora do CI.
- Por env e não por opção, de propósito: a catraca roda da base, e opção desconhecida daria rc=2 até o merge. Consequência (recomendado, não devolve): a recusa só vale depois deste merge; o PR registra isso.
- Delta 5ad6373..838803f (A1 de review e segurança): em CI (`GITHUB_ACTIONS`) com `BASE_REPO` vazio a recusa falha fechada, e um teste exige `HEAD_REPO` e `BASE_REPO` no `env:` do passo (sem `${{` no `run:`). Só endurece; conferido.
- Nada afrouxa a catraca nem tests/config.json.

Ferramentas: `python3 -m unittest tests.test_catraca` (280 testes, OK) e `tests.test_ci_local` (52, OK), com `python3 -I -m unittest discover`. Faltou `actionlint` no PATH: o diff do workflow é uma linha de `env:` mais uma, revisadas à mão. Mudança em `.github/` exige o rótulo `afrouxa-regra` do dono e o envio do workflow pelo dono.

## Custo e rollback
Sem minutos nem recurso novo (R-CUSTO). Rollback: reverter o commit; a catraca volta ao comportamento anterior.
