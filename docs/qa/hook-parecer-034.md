---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/hook-parecer-034
commit: 907d3ad5c85e57aa2d03b255954dff456e97ca6d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: versao-033 (frente 0.34, hook-parecer-034)

Base `b45e40a`; código `05b6d6b`; este parecer vale para `907d3ad` (05b6d6b mais a fixture do A1 da segurança, único acréscimo, em teste). Ambiente: worktree da branch, Python 3.12, repositórios descartáveis no scratchpad (prefixo `qa034_`), hook rodado de verdade com JSON de PreToolUse no stdin. Sem suíte inteira (D-5 do pedido: só o módulo da pasta e os mutantes).

## Achados
- A1 (recomendado) tests/hooks/parecer/atualiza-passa-fetch-e-ff-only-da-propria-branch-reprovada.json:1 · as fixtures atualiza-passa-* passam também na base (o passa já existia; o cartão BARRA-FETCH só adiciona o corpus); guardam regressão, não provam correção

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| HOOK-DICA-EDIT: outro programa roda o corpo, a mensagem manda Write ou Edit | `texto-barra-heredoc-*-dica-write`, `corpo-ilegivel-e-git-diz-a-causa`, E2E `cat-heredoc-corpo-ilegivel-git` | corpo ilegível (aspa sem par) com `git` na chamada | passou (rc 2, `grave pelo Write ou Edit`) |
| HOOK-DICA-EDIT: o próprio sh ou bash roda o corpo, a mensagem segue com `<<'FIM'` | `texto-barra-heredoc-sh-com-heredoc-aninhado-sem-aspas-pede-fim`, E2E `sh-` e `bash-heredoc-aninhado-sem-aspas` | dono `sh`/`bash` (valor True) contra programa do texto (str) | passou (rc 2, `<<'FIM'`, sem `Write ou Edit`) |
| HOOK-DICA-EDIT: nenhuma recusa vira liberação | diferencial base x head, 365 fixtures de Bash | decisão (rc), não o texto | passou: 0 recusas liberadas, 0 liberações novas barradas; 15 recusas só com texto novo |
| BARRA-FETCH: fetch, merge --ff-only, pull --ff-only passam na branch reprovada | `atualiza-passa-*` (3), E2E `fetch-ff-origin-develop`, `pull-ff-feature`, `fetch-merge-ff-branch` | branch de trabalho com review reprovado | passou (rc 0, stderr vazio) |
| BARRA-FETCH: a develop segue barrada | `atualiza-barra-*` (3, mais a nova), E2E `develop-sem-checkout-{merge,fetch-merge,pull}`, `checkout-develop-merge`, `develop-merge-sem-ff-only` | já na develop sem checkout (A1 da segurança); com checkout na linha | passou (rc 2, `R-REVIEW: docs/reviews/p1-1.md`) |

## Cenários E2E (hook real, repositório descartável)
13 cenários em `qa034_e2e.py` (scratchpad), 12 como esperado. O 13º (`python3 <<'EOF'` com apóstrofo e `git merge` depois do heredoc) deu rc 2 com a mensagem antiga de programa fora da lista, não a dica nova: expectativa minha errada, caminho distinto e já recusado na base; não é defeito.

## Fixture criada pelo QA (commit 907d3ad, separado)
`atualiza-barra-ff-only-na-develop-sem-checkout.json`: estado já na develop (`checkout` no passo, sem checkout na linha), `git merge --ff-only feature/x`, espera rc 2 e `R-REVIEW: docs/reviews/p1-1.md`. Primeira versão (chave `git` inválida) deixou a sessão na feature e o teste falhou com rc 0, o que mostra que a fixture distingue os dois estados; corrigida para `checkout`. Fecha o A1 da segurança.

## Execução
- `python3 -I -m unittest discover -s tests -p test_hooks_parecer_pasta.py`: 3 testes, OK (22 s), com a fixture nova.
- `bin/forge-mutante tests/mutantes/hook-parecer-034.json`: saída 0; M1, M2, M3, M4, M5, M6 morreram (`parecer.py:669`, `:86`, `:689`, `:714`, `:692`, `:669`). Conferido contra o diff: as cinco linhas de guarda/texto mudadas têm mutante.
- Vermelho antes do verde: `forge-testes --vermelho b45e40a --modulos test_hooks_parecer_pasta`, rc 0: `texto_passa_e_barra` prova (falha na base); `atualiza` e `pasta` "não prova (passa na base)" (A1).

## Resultado
Aprovado, sem bug aberto. Pareceres de review (be97820) e segurança (353464f) aprovados sobre o mesmo código.
