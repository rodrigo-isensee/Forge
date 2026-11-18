---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: c41f7fe58808dfae86c046611c39ee4de9825098
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (guardas do hook `parecer`, E3.9, revalidação)

Escopo: delta `d8e9aa8b..c41f7fe5` lido por `forge-check parecer delta`: `hooks/parecer.py`, 14 fixtures novas (`incidente-r-copia-alheia-*` e `graphql-*`), `tests/test_hooks_parecer_repo.py`, specs de mutantes (M14 a M21 e ajuste de M1, M3, M4 e do M8/M9 de `v0457-fila27-2`), `changelog.d`, índice de fixtures. Sem PR nem CI deste head: a suíte inteira não rodou (brief); rodei só os testes dos arquivos tocados. Sem especificação de UX: obrigações CA-1 (INCIDENTE-HOOK-PARECER-CONTORNADO), CA-2 (GH-API-LEITURA-UNICA), CA-3 (GRAPHQL-FORA-DO-CLONE) e CA-4 (GH-API-ARQUIVO-TROCADO), as duas últimas do parecer de segurança.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 cópia git alheia: `-R`, `GH_REPO`, URL, `gh repo`, `cd` e sem `-R` conferem no clone da sessão (A1 anterior) | `test_gh_pr_fora_do_repositorio_confere_no_clone_da_sessao` (19 fixtures, lados 0 e 2) | cópia com remoto outro, com remoto do Forge, sem remoto; sem repositório indicado | passou |
| CA-2 `gh api` lê o mesmo arquivo que o gh | `test_leitura_dos_arquivos_do_gh_api` (9) | `~`, curinga, `--input=@arq` | passou |
| CA-3 graphql que tira o rascunho fora do clone confere na sessão | `test_graphql_fora_do_clone_e_arquivo_trocado_na_linha` (6) | fora do clone; consulta que só lê libera | passou |
| CA-4 graphql com arquivo e outro comando na linha recusa | idem | `cp ... && gh api`, substituição; só `cd` antes libera | passou |

## Cenários e resultado real
- Testes tocados, TMPDIR próprio: `python3 -I -m unittest discover -s tests -p test_hooks_parecer_repo.py` → `Ran 5 tests ... OK`; `-p test_hooks_fila27.py` → `Ran 4 tests ... OK`.
- Vermelho antes do verde (manual; o `forge-testes --vermelho` cairia em suíte completa por o diff tocar `bin/`): head com `hooks/parecer.py` de d8e9aa8b → FAIL nas fixtures `incidente-r-copia-alheia-{cd-repo,create-r,gh-repo-merge,merge-url,ready-r,remoto-do-forge,repo-desconhecido}-bloqueia` e `graphql-{arquivo-trocado-em-substituicao,arquivo-trocado-na-linha,copia-alheia-ready,...}-bloqueia`: as recusas novas davam 0 sem a correção.
- Mutação: `bin/forge-mutante tests/mutantes/v0478-guardas-parecer.json -2.json -3.json --processos 3 --base d8e9aa8bef4f1b5fedbcfe157722e6c6dc974041`: `base=d8e9aa8bef4f1b5fedbcfe157722e6c6dc974041 mb=d8e9aa8bef4f1b5fedbcfe157722e6c6dc974041 rev=c41f7fe58808`; M1 a M21 todos `morreu` (M14 parecer.py:932, M15:933, M16:988, M17:996, M18:1093, M19:1094, M20:1093, M21:1006); nenhum sobrevivente. `v0457-fila27-2.json`: M4 a M10 `morreu`. Cada linha de guarda mudada no delta (pasta_do_gh, graphql_no_clone, arquivo_trocado_na_linha, `acompanhado`) tem mutante; a isenta da condição movida é justificada por M21.
- Cobertura: `--cobertura --base 4182a6b9` sai `coberta`/`movida` sem condição descoberta; com `--base d8e9aa8b` sai rc 2 (a isenta `raiz_declarada() or pasta` de `v0478-guardas-parecer.json` não cruza mais condição, pois o trecho foi para `sessao_ou`); não bloqueia, nenhum hook nem CI chama a checagem (A1).
- Sondas de variantes (`--repo=`, `-R` em maiúsculas, `GH_REPO` com URL, `-Rdono/forge`, graphql inline, `cp;`, pipe, subshell): a sonda não completou no ambiente (processo abortou); não afirmo resultado delas. A segurança as cobre no domínio dela.
- Acessibilidade e E2E: não se aplicam (hook de linha de comando).

## Achados
- A1 (recomendado) tests/mutantes/v0478-guardas-parecer.json:86 · a isenta `raiz_declarada() or pasta` ficou velha (o trecho foi para `sessao_ou`) e o `--cobertura --base d8e9aa8b` sai rc 2; atualize o trecho para `return raiz_declarada() or pasta` ou retire.

## Resultado
Aprovado: o A1 do parecer anterior (cópia git alheia) está fechado com fixtures e mutantes; M1 a M21 morrem; CA-3 e CA-4 provados, vermelho visto. Sem bug aberto.
