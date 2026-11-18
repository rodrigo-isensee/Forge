---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: b989773a2ae7276692081441ff72c05d26d0f8da
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (guardas do hook `parecer`, E3.18, revalidação)

Escopo: delta `56bb90b5..b989773a` lido por `forge-check parecer delta`: `hooks/parecer.py` (remotos lidos como o gh lê, `gh-resolved`, `insteadOf`, `source`/`.`, nome por expansão em `SENSIVEIS`), 15 fixtures novas `incidente-r-copia-alheia-*` e `pasta-barra-home-fixado-...`, `tests/test_hooks.py` (`config` e `config_bruta` nos repos das fixtures), `tests/test_hooks_parecer_repo.py` (contagem 23 para 38), specs de mutantes (`v0478-guardas-parecer-5/6/7`, `hk3-parecer-pasta-11/12`), `changelog.d`, índice de fixtures. O aviso do merge `4a21e7f` (fora da origin/develop local) conta o merge inteiro; as linhas dele só têm apoio de teste. Sem PR nem CI deste head e máquina carregada: rodei só o módulo tocado e os mutantes, sem `tests.test_hooks` inteiro (brief).

Obrigações: CA-1 (INCIDENTE-HOOK-PARECER-CONTORNADO), CA-5 (GH-REPO-EXPORTADO) e, novas, GH-REPO-DE-ARQUIVO e GH-REMOTO-RESOLVIDO: `GH_REPO` carregado de arquivo ou com nome vindo de expansão, e remoto resolvido por `gh-resolved`/`insteadOf`, não deixam o PR do Forge sair do rascunho sem parecer.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1/CA-5 cópia alheia: `GH_REPO` exportado ou de arquivo (`source`, `.`, `builtin source`, `export $(cat)`, `read`, `printf -v`, `declare -n`) recusa fora de clone | `test_gh_pr_fora_do_repositorio_confere_no_clone_da_sessao` (38 fixtures, 15 novas) | nome por expansão recusa; `export` com valor expandido, `read -p` e `for` com expansão liberam (falso positivo) | passou |
| GH-REMOTO-RESOLVIDO `remote.<n>.gh-resolved`, `insteadOf`, remotos ilegíveis | mesmo teste (`gh-resolved-ready`, `insteadof-ready`, `remotos-ilegiveis`; `gh-resolved-base-libera`) | `gh-resolved=base` libera; remoto ilegível recusa | passou |
| `cd ~` / `/` depois da negação fixa a pasta | fixture `pasta-barra-home-fixado-depois-da-negacao-e-cd-til` (corpus `tests/test_hooks.py`, não rodado inteiro) | `cd` til após negação | coberta por mutante (M77 a M92) |
| CA-2 a CA-4 (gh api, graphql) | `test_leitura_dos_arquivos_do_gh_api`, `test_graphql_fora_do_clone_...`, `LeituraDoGhApi.*` | sem mudança no delta | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_hooks_parecer_repo.py` (TMPDIR próprio) → `Ran 5 tests in 14.333s ... OK`.
- Vermelho antes do verde: `bin/forge-testes --vermelho 56bb90b555cc63d4f035dd27d0d35a6541e3647a --modulos tests.test_hooks_parecer_repo` → `vermelho: base=56bb90b555cc head=b989773a2ae7`, `hooks/parecer.py` revertido à base; `test_gh_pr_fora_do_repositorio_confere_no_clone_da_sessao · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=4; prova (asserção)=1` (os 4 outros testes não mudaram), rc 0.
- Mutação: `bin/forge-mutante tests/mutantes/v0478-guardas-parecer-5.json -6.json -7.json --processos 3 --base 56bb90b5...` → `base=56bb90b555cc63d4f035dd27d0d35a6541e3647a mb=56bb90b555cc63d4f035dd27d0d35a6541e3647a rev=b989773a2ae7276692081441ff72c05d26d0f8da`; M27 a M41 todos `morreu` (parecer.py:607-613, 624-631, 937, 942). Specs `hk3-parecer-pasta-11/12` (pedido outro, rodada à parte, mesma base): M77 a M92 todos `morreu`. Nenhum sobrevivente.
- Cobertura: `bin/forge-mutante --cobertura --base 56bb90b5...` → rc 0, só a linha `base=`; nenhuma condição descoberta, isenta ou `só equivalente` no delta.
- Árvore limpa após as rodadas (cópias em `$TMPDIR`).
