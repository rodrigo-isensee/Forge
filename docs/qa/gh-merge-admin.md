---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/gh-merge-admin
commit: 94377b7311db64c26d2f51d1641d760e4bcb73a6
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: gh-merge-admin (versao-033, E1.6)

Revisor: `forge:qa-engineer` (nem autor nem revisor do E1; D-ETAPAS-INST). Base `928e61b`, código `dfcc2b2`; rodada 1 testada em `926a1d4`, rodada 2 em `94377b7` (volta 8, só `tests/mutantes/`). Worktree `~/.forge-contrib/wt/wt-qa-gh-merge-admin`; sondas e logs em `$TMPDIR/qa-engineer-gh-merge-admin/`.

## Achados
Nenhum achado aberto. A1 e A2 da rodada 1 foram resolvidos na volta 8 (ver Rodada 2).

## Critério → teste → resultado
O E1 não tem especificação de UX (`CA-n`); as obrigações são os controles C-1 a C-8 e as mudanças proibidas T-1 a T-5 do modelo de ameaças (seção E1 GH-MERGE-ADMIN), com R-MAIN.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C-1 `--admin` e `--admin=<valor>` recusam | sondas S1 (24 formas) e fixtures `admin-*` | valor `false`/`1`, depois de `--`, como valor de `--body`, `-R` entre `pr` e `merge`, programa por caminho ou expansão | passou |
| C-2 recusa antes das saídas antecipadas, sem papel, base ou pasta | S1 em 3 papéis x (repositório, `cd /tmp &&`) | sem papel, `cd /tmp`, `GH_REPO=` | passou |
| C-3 toda posição chega à mesma decisão | S1 e S2: `bash -c`, `eval`, crase, `$()`, `xargs`, `env`, `command`, `&&`, `;`, `( )`, `{ }`, `if`, `for`, `time`, `nohup`, `&` | invólucros | passou |
| C-4 `gh api` mutante de merge e GraphQL | S1 e S2 (REST PUT, `merges`, `{owner}`, URL, `-iX`, `-XPUT`, `-X GET -X PUT`, `-p -XGET` com campo; GraphQL inline, `-F @arq`, `--input arq`, `--input -`, `--field=`, 4 mutações, `git/refs`) | método minúsculo, `/graphql`, campo colado, corpo ilegível | passou |
| C-5 legítimos mantêm o veredito da base | S1 (30) e S2 (9) em 3 papéis x 2 pastas, base x head | `pr view`, `pr merge` sem `--admin`, `gh api` em GET com e sem campo | passou (0 diferenças) |
| C-6 sem rede nem `gh` novo | leitura do diff; teste de prazo na suíte | n/a | passou |
| C-7 (a) a (h) | S1 e fixtures do lote `test_fixtures_do_gh_merge_admin` | (a) a (g) recusam, (h) passa | passou |
| C-8 mutantes | `forge-mutante` nas três specs | guardas do diff | passou (rodada 2: 3 specs numa rodada, rc=0, todos mortos) |
| T-1 a T-3 | sondas por papel e pasta; leitura do diff | nada de papel, base, valor de `--admin=` nem escape | passou |
| T-4 nada recusado na base passa a liberar | S1 e S2: 139 comandos x 3 papéis x 2 pastas, base e head | recusas antigas (`git push`, `API_ADMIN`, `--auto`, `gh_trava`) | passou (0 regressões) |

## Resultado real (rodada 1)
- **Suíte inteira** (`.githooks/pre-push --suite`, head `926a1d4`, uma vez): `Ran 2490 tests in 954.285s (4 processos)`, `OK (skipped=28)`, rc=0. Fila conferida antes (`--status`: nenhuma suíte rodando).
- **`scripts/validar-plugin.sh`:** rc=0, `Validation passed`. **`bin/forge-check docs`:** rc=0.
- **Ponta a ponta (hooks da worktree, entradas montadas):** S1 com 104 comandos e S2 com 35 (74 abusos, 39 legítimos e recusas antigas), em Jarvis, tech-lead e sem `agent_type`, no repositório e com `cd /tmp &&`: 0 abusos liberados, 0 legítimos com veredito diferente da base, 0 regressões da T-4 (204 execuções recusadas na base seguem recusadas); 324 execuções recusadas só no head. Com a pasta atual fora de qualquer projeto Forge o hook libera tudo, no head e na base (312 de 312 iguais): é o desenho do hook, não mudou.
- **Vermelho antes do verde:** `bin/forge-testes --vermelho 928e61b` sai rc=2 (`test_hooks` sem veredito por prazo; 1348 testes "não prova (passa na base)" são os de outros módulos, 26 pulados). Feito à mão, o lote `test_fixtures_do_gh_merge_admin` com as fixtures e o `test_hooks.py` do head sobre o código da base: 79 das 84 fixtures `bloqueia` caem na base (as 5 restantes já eram recusadas pela base: `git/refs`, `enablePullRequestAutoMerge` e afins), e as 15 `libera` passam nos dois. Sem teste novo que passe sem o código.
- **Mutantes (rodada 1):** `gh-merge-admin-2.json` e `-3.json` rc=0, 31 mortos; `gh-merge-admin.json` rc=2 por `G8 · inválido · o trecho aparece 0 vezes no arquivo` (A1, resolvido na rodada 2).
- **PA-7** (`docs/engineering/achados-recorrentes.md`), conferida: AR-1 (lista de mutantes) foi o A1 e o A2, e a linha já existe (vezes: 6), sem linha nova; AR-7 e AR-8 (pasta e invólucro) cobertos por `cd /tmp &&`, `bash -c`, `eval`, `env`, `command`; AR-11 (leitura de opção do `gh api`) coberta pelas sondas de `-iX`, `-XPUT`, `-p -XGET`; AR-3, AR-5, AR-6, AR-9 e AR-10 não se aplicam.
- Review A7 e A10 e segurança A8 e N1 (recomendados, já registrados, fora do E1): não repetidos. Nenhum bug de comportamento do produto encontrado; `docs/qa/bugs/` sem entrada.

## Rodada 2
Head testado `94377b7311db64c26d2f51d1641d760e4bcb73a6` (volta 8 do autor). `git diff --name-only c09ecec 94377b7` lista só `tests/mutantes/gh-merge-admin.json`, `-2.json` e `-3.json`: sem `hooks/`, então as sondas S1 e S2 da rodada 1 seguem valendo e não foram repetidas.
- **Suíte inteira** (`.githooks/pre-push --suite`, uma vez, fila vazia conferida por `--status`): `Ran 2490 tests in 829.550s (4 processos)`, `OK (skipped=28)`, rc=0.
- **`scripts/validar-plugin.sh`:** `Validation passed`. **`bin/forge-check docs`:** rc=0.
- **Mutantes** (`bin/forge-mutante` nas três specs numa rodada só): rc=0, `pedido=gh-merge-admin`, todos `morreu` (G1 a G10, G11 a G27 sem G13, G28 a G44 sem G36); o G8 (hooks/parecer.py:559) agora roda e morre.
- **Cobertura** (`forge-mutante --cobertura --base 928e61b`): rc=0, toda condição mudada de `hooks/` aparece `coberta` ("declarado, não provado", provada pela rodada acima); nenhuma sem mutante.
- **A1:** resolvido (o `de` do G8 casa com o código; a spec 1 voltou a rodar). **A2:** resolvido (as três specs com o mesmo `pedido`; rodada única sem rc=2).

## Parecer
**Aprovado** sobre `94377b7`. Nenhum bloqueante, nenhum bug de produto. O comportamento do E1 foi provado na rodada 1 e a prova de mutação fechou na rodada 2.
