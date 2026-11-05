---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/release-suite-paralela
commit: 6652f6b1898c91866a18e128ddbd1927c76b0277
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (E24 RELEASE-SUITE-PARALELA)

Diff `f54d9b7...6652f6b`: 3 arquivos, 12 linhas adicionadas e 6 removidas; só `release.yml` e `tests/test_ci_local.py` contam para a M14 (10 linhas, dentro do teto), um comportamento só.

## Conferido contra o Entregar
- `release.yml`: o passo da suíte passa a `python3 scripts/suite-paralela.py`, igual ao `ci.yml:36`. O `actions/setup-python` entra com o mesmo SHA `6d4fd22b...` (v7.1.0) e `python-version: "3.12"` do `ci.yml:32-34`. O `ci.yml` não define variável de ambiente para a suíte paralela (o `env:` do job é só do actionlint e do zizmor), então não há o que copiar; o `CI` do próprio Actions faz o script rodar sempre. Teto 20 para 25 min, o mesmo da bateria. Gatilho, `permissions`, checkout, `persist-credentials: false` e a publicação não mudaram.
- `tests/test_ci_local.py`: o teste agora exige `python3 scripts/suite-paralela.py` e proíbe `unittest discover` no `release.yml`; a proibição pega a regressão ao passo em série. `python3 -m unittest tests.test_ci_local`: 52 testes, OK.
- Fragmento `changelog.d/release-suite-paralela.md` presente, tipo Corrigido.
- Achados recorrentes (PA-7, AR-1 a AR-10): nenhum alcança estes arquivos. Segurança e devops têm parecer próprio e não foram refeitos aqui.

## Achados
- A1 (recomendado) docs/devops/suite-paralela-d4.md:25 · diz que a release segue em série com teste de contraprova; passou a ser falso. Registro histórico de outro pedido, não devolve; atualizar quando o doc for tocado.
