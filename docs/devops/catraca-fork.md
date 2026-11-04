---
tipo: revisao-devops
contrato: 1
pedido: catraca-fork
branch: melhoria/catraca-fork
commit: 5ad6373f37d21c727a1cf97f1f1c3a1256c62163
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
- Nada afrouxa a catraca nem tests/config.json.

Ferramentas: `python3 -m unittest tests.test_catraca` (278 testes, OK) e `tests.test_ci_local` (52, OK). Faltou `actionlint` no PATH: o diff do workflow é uma linha de `env:` mais uma, revisadas à mão. Mudança em `.github/` exige o rótulo `afrouxa-regra` do dono e o envio do workflow pelo dono.

## Custo e rollback
Sem minutos nem recurso novo (R-CUSTO). Rollback: reverter o commit; a catraca volta ao comportamento anterior.
