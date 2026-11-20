---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.11
branch: melhoria/v0479-release-04711
commit: fe752d14857633363b9da383eeeb9321ff67b7fe
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: release 0.47.11 (versão inteira)

Escopo: `git diff v0.47.10..fe752d14` (`v0.47.10` = `013b87af`), 24 arquivos: #701 (`ef186de8`, conserto da S1 e do corpus), #706 (`119aed79`, placar da META85) e a marca (`fe752d14`, E42.1). Cada item entrou com os próprios pareceres aprovados; aqui se confere a junção.

Gatilhos: hook `parecer`/`conformidade` só em teste (`tests/test_hooks*.py`), execução de comando (`bin/forge-placar`), release usada por todos os projetos.

## Sondas

## Detalhe dos achados
Sem achados novos. Junção conferida:
- #701: parecer `v0479-develop-relogio` aprovado no commit `76cbce17`; o patch dos arquivos de código (`tests/test_hooks.py`, `tests/test_hooks_volta_corpus.py`) tem o mesmo `git patch-id --stable` (`494db622`) no revisado (base `b23124f8`) e no mesclado (`ef186de8`). Só teste; o hook em si não muda.
- #706: parecer `v0479-meta85-placar` aprovado no commit `6f6aab30`; o diff entre `6f6aab30` e `119aed79` fora de `docs/{qa,reviews,security}`, `tests/mutantes`, `CHANGELOG.md` e `changelog.d/` é vazio.
- Marca `fe752d14`: só `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.11 (iguais ao `CHANGELOG.md`), `CHANGELOG.md` com `[0.47.11] - 2026-11-20` em português e `[Não publicado]` vazio, e os dois fragmentos apagados (`changelog.d/` só com o `README.md`); as duas entradas são os textos dos fragmentos. Nada além disso na marca.
- Segredo: nenhuma ocorrência de token, chave privada ou credencial nas linhas acrescidas do diff (busca por padrões de ghp_, AKIA, chave privada, xox, sk-: 0).
- Notas: nada de projeto específico no `[0.47.11]` (só `forge-placar`, testes e IDs do pedido; sem nome de cliente ou projeto).

Recomendação aberta que segue valendo sem recópia (não bloqueia): `v0479-develop-relogio` A1 (`tests/prova_de_carga.py:58`).

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. A suíte inteira é do CI do PR (a local falha por ambiente: `/proc` e `gh` no sandbox); a promoção exige o CI verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; a versão não toca workflow nem dependência.
