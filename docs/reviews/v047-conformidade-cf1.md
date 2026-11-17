---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-conformidade-cf1
commit: 7412a90f2e2389af96e3e8aa0ead8f22de90baee
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 · CF1 do hook conformidade (A17, A18, A19) depois das junções com a develop (E1.29)

Parecer anterior: `docs/reviews/v047-conformidade-destino-opaco.md`, aprovado no 0121b3b2 (E2.493). Aquele arquivo é do pedido v047, já integrado no #611; daqui em diante o parecer do CF1 fica neste arquivo.

## Revalidação por delta 0121b3b2..7412a90f
Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (intervalo `0121b3b2..7412a90f`, escopo "sem o que veio da base (develop)"). No domínio: `bin/forge-testes`, `docs/hooks-fixtures.md`, `docs/hooks.md`, `tests/mutantes/v046-conformidade-caminho-git.json`, `tests/mutantes/v047-destino-opaco-10.json`, `tests/test_conformidade_verde.py`, `tests/test_oraculo_v047.py`, `tests/test_testes_tocados.py`. O delta são duas junções da develop: b7a82cf4 (com a 45615e20) e 7412a90f (com a e2880b42).

Junção conferida com `git show --remerge-diff`:
- `hooks/conformidade.py` (b7a82cf4): os dois conflitos ficam com o lado da branch (`DECLARADORES`, `atribui_como_argumento` e a guarda A19 na linha 730). O patch do CF1 sobre a develop é o mesmo que foi aprovado: as linhas `+`/`-` de `git diff a219fa8c^ 45151e92` e de `git diff e2880b42 7412a90f`, em `hooks/`, `tests/hooks/`, `tests/mutantes/v047-conformidade-cf1.json` e `tests/test_conformidade_verde.py`, são iguais (diff vazio).
- `bin/forge-testes`: `FORGE_CHECK` é a tupla da develop mais `test_conformidade_verde` (a única diferença entre os lados); o `MAPA` de `hooks/.*` fica com o lado da develop, que já traz os três nomes da branch. `test_estado_ilegivel` entrou sem conflito.
- `tests/test_testes_tocados.py` (7412a90f): a contagem 90 é igual aos 89 da develop mais `test_conformidade_verde`. `python3 -m unittest tests.test_testes_tocados.Mapa`: 18 testes, OK.
- `tests/test_oraculo_v047.py`: fica com o lado da develop, que é o blob da develop. O oráculo não muda em relação à base.
- Specs G6 e O60 realinhadas ao texto da branch (`SO_VARIAVEL` com `\$[@*]`, a guarda A19). `bin/forge-mutante --conferir --base e2880b42`: "o trecho de cada spec do diff está no lugar". `bin/forge-mutante tests/mutantes/v046-conformidade-caminho-git.json`: G1 a G8 morreram. `bin/forge-mutante tests/mutantes/v047-destino-opaco-10.json`: O58 a O65 morreram.
- Pareceres da v047: o de segurança fica com o lado da develop. O de review e o de QA ficam com o frontmatter da branch (A1). O frontmatter que a junção deixou nos dois arquivos é `branch: melhoria/v047-conformidade-cf1` com `commit: 0121b3b2` (review) e `6f8bd39e` (QA). A develop tem `melhoria/v047-conformidade-destino-opaco` com `c7a8ff72`. Para voltar: `git checkout origin/develop -- <arquivo>`. O CF1 já tem pareceres próprios (este arquivo e `docs/security/v047-conformidade-cf1.md`), e o conflito some nas próximas junções.

Suíte: sem PR nem CI para este sha (o brief não pede PR); a suíte completa fica com o CI do PR.

## Achados
- A1 (recomendado) docs/reviews/v047-conformidade-destino-opaco.md:5 · o parecer do #611 (e o de QA, docs/qa/…:5) ficou com o frontmatter do CF1; o merge regravaria o registro integrado. Voltar os dois ao blob da develop antes do PR (R-FLUXO).
- A2 (recomendado) bin/forge-testes:172 · a resolução do `MAPA` deixou duas linhas com 20 espaços de recuo, contra 19 nas linhas vizinhas. É só forma e veio do lado da develop.

## Sondas

## Parecer
Aprovado no 7412a90f (R-REVIEW), por delta. As duas junções somam os dois lados sem mudar comportamento. O código do CF1 em `hooks/` é o mesmo do 0121b3b2, as specs G6 e O60 seguem a fonte e os 16 mutantes morrem. A1 e A2 são recomendados e não bloqueiam. Aprovação anterior: 0121b3b2, em `docs/reviews/v047-conformidade-destino-opaco.md`.
