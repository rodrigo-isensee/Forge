---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 56bb90b555cc63d4f035dd27d0d35a6541e3647a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (guardas do hook `parecer`, E3.14, revalidação)

Escopo: delta `c41f7fe5..56bb90b5` lido por `forge-check parecer delta`: `hooks/parecer.py` (`REPO_INCERTO`, `repo_indicado`, `GH_REPO` em `SENSIVEIS`), 4 fixtures `incidente-r-copia-alheia-*gh-repo*`, `tests/test_hooks_parecer_repo.py` (19 para 23), specs de mutantes (`-4.json` com M22 a M26; isenta velha retirada de `v0478-guardas-parecer.json`), `changelog.d`, índice de fixtures. Sem PR nem CI deste head: rodei só os testes dos arquivos tocados (brief). Obrigações: CA-1 (INCIDENTE-HOOK-PARECER-CONTORNADO, A1 anterior), CA-2 (GH-API-LEITURA-UNICA), CA-3 e CA-4 (graphql), CA-5 (GH-REPO-EXPORTADO: `GH_REPO` exportado antes do gh numa cópia alheia não libera o PR do Forge).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 cópia alheia: `-R`, `GH_REPO=`, URL, `cd` e sem `-R` conferem no clone da sessão | `test_gh_pr_fora_do_repositorio_confere_no_clone_da_sessao` | cópia com remoto outro, do Forge, sem remoto | passou |
| CA-2 `gh api` lê o mesmo arquivo que o gh | `test_leitura_dos_arquivos_do_gh_api` | `~`, curinga, `--input=@arq` | passou |
| CA-3/CA-4 graphql fora do clone e arquivo trocado na linha | `test_graphql_fora_do_clone_e_arquivo_trocado_na_linha` | consulta que só lê libera | passou |
| CA-5 `export`, `declare -x`, atribuição+`export`, `&&` com `GH_REPO` antes do gh recusam fora de clone | mesmo teste do CA-1 (23 fixtures, 4 novas) | `GH_REPO` mexido sem `-R`; `-R` ou prefixo legível seguem valendo | passou |

## Cenários e resultado real
- Testes tocados, TMPDIR próprio: `python3 -I -m unittest discover -s tests -p test_hooks_parecer_repo.py` → `Ran 5 tests ... OK`; `-p test_hooks_fila27.py` → `Ran 4 tests ... OK`.
- Vermelho antes do verde (cópia em `$TMPDIR`, `hooks/parecer.py` de c41f7fe5 com o resto do head): `Ran 5 tests ... FAILED (failures=4)`, as 4 fixtures novas `incidente-r-copia-alheia-{atribui-e-exporta-gh-repo-ready,declare-x-gh-repo-ready,export-gh-repo-e-merge,export-gh-repo-ready}-bloqueia` davam 0 sem a correção.
- Mutação: `bin/forge-mutante tests/mutantes/v0478-guardas-parecer.json -2 -3 -4 --processos 3 --base c41f7fe58808dfae86c046611c39ee4de9825098` → rc 0, `base=c41f7fe58808dfae86c046611c39ee4de9825098 mb=c41f7fe58808dfae86c046611c39ee4de9825098 rev=56bb90b555cc63d4f035dd27d0d35a6541e3647a`; M1 a M26 todos `morreu` (M22 parecer.py:923, M23:923, M24:942, M25:113, M26:914); nenhum sobrevivente. Cada linha de guarda do delta (`repo_indicado`, `if repo is REPO_INCERTO`, `SENSIVEIS`, `sessao_ou`) tem mutante.
- Cobertura: `bin/forge-mutante --cobertura --base 4182a6b95a12e085abbd879c5c5010541e1d11f1` → rc 0, 31 linhas `coberta`, as demais `movida`/`spec editada`/`isenta` (a única isenta é `parecer.py:980(base)`, movida para `graphql_no_clone` com M21); nenhuma condição descoberta. O A1 do parecer anterior (isenta velha) está fechado.
- Acessibilidade e E2E: não se aplicam (hook de linha de comando).

## Resultado
Aprovado: CA-5 provado com vermelho visto, M22 a M26 morrem, cobertura sem condição descoberta e A1 anterior fechado. Sem bug aberto.
