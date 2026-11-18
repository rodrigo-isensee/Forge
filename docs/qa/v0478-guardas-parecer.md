---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: d8e9aa8bef4f1b5fedbcfe157722e6c6dc974041
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (guardas do hook `parecer`, E3.5)

Escopo: `4182a6b9..d8e9aa8b` (`hooks/parecer.py`, `hooks/_gh_api.py`, 20 fixtures `incidente-r-*` e `leitura-api-*`, mutantes, `bin/forge-testes`). Sem especificação de UX: as obrigações são as duas guardas do changelog (CA-1 INCIDENTE-HOOK-PARECER-CONTORNADO, CA-2 GH-API-LEITURA-UNICA). Sem PR nem CI deste head: a suíte inteira não rodou (brief: sem suíte local); rodei só os testes dos arquivos tocados.

## Achados
- A1 (bloqueante) hooks/parecer.py:911 · Reproduzido: `gh pr ready -R dono/forge`, `GH_REPO=`, `gh pr merge <URL>` e `gh pr create -R` com cwd em cópia git alheia (remoto outro/coisa) dão código 0 sem parecer; `pasta_do_gh` devolve a cópia e o gh age em outro repositório (R-REVIEW).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 fora de repositório git, `-R`/`--repo`/`GH_REPO`/URL confere no clone da sessão | `test_gh_pr_fora_do_repositorio_confere_no_clone_da_sessao` (11 fixtures, lados 0 e 2) | sem clone da sessão; remoto de outro repo; dentro do clone | passou |
| CA-1 idem, cwd em cópia git alheia | sonda QA (abaixo) | cópia de trabalho sem relação com o repositório do `-R` | falhou (A1) |
| CA-2 `gh api` lê o mesmo arquivo que o gh ou recusa | `test_leitura_dos_arquivos_do_gh_api` (9 fixtures) | `~`, curinga, `-`, `--input=@arq`, FIFO, pasta não resolvida | passou |
| CA-2 `--field=campo=@arq` | `test_campo_longo_com_igual_le_o_arquivo_depois_do_arroba` | nome com `=@` | passou |
| CA-2 pasta desconhecida com relativo | `test_pasta_desconhecida_com_relativo_e_ilegivel` | pasta None | passou |

## Cenários e resultado real
- Teste dos arquivos tocados, TMPDIR próprio: `python3 -I -m unittest discover -s tests -p test_hooks_parecer_repo.py` → `Ran 4 tests ... OK`.
- Sonda QA independente (mesmo lançador da suíte, `Fixture.montar` e `rodar`; cwd = `{tmp}/alheio`, `git init` com remoto `git@github.com:outro/coisa.git`, sessão no clone, sem parecer): código 0 nos cinco comandos `gh pr ready -R dono/forge feature/x`, `GH_REPO=dono/forge gh pr merge feature/x`, `gh pr merge https://github.com/dono/forge/pull/5`, `gh pr create -R dono/forge --base develop --head feature/x`, `gh pr ready feature/x`. Esperado: 2 nos quatro com alvo explícito. Confere com S1 a S5 do parecer de segurança (`docs/security/v0478-guardas-parecer.md`), que li depois de sondar. As fixtures não cobrem a cópia alheia: só cwd fora de git e o clone.
- Vermelho antes do verde: `forge-testes --vermelho 4182a6b9` sem caminho, depois da trava da suíte (R-TETO) liberar, caiu em suíte completa ("o mapa não sabe": o diff altera `bin/forge-testes`) e foi interrompido por mim; não tenho veredito (rc 2, não vale como vermelho). Prova manual: base `4182a6b9` + `tests/test_hooks_parecer_repo.py` + fixtures novas, `python3 -I -m unittest discover -s tests -p test_hooks_parecer_repo.py` → `ERROR: test_hooks_parecer_repo (_FailedTest)`, `FAILED (errors=1)` (a base não tem `hooks/_gh_api.py`: falha de carga, só prova teste que a base não tinha). O vermelho por teste das fixtures de recusa está declarado no changelog (7 e 5 fixtures davam 0 na base); não o reproduzi por fixture.
- Mutação (`bin/forge-mutante tests/mutantes/v0478-guardas-parecer.json tests/mutantes/v0478-guardas-parecer-2.json`): `pedido=v0478-guardas-parecer rev=d8e9aa8bef4f` e M1 a M13 `morreu` (parecer.py:911, 915, 918, 920, 395, 398, 388, 902, 895; _gh_api.py:51 ×2, 48 ×2); nenhum sobrevivente.
- Cobertura (`forge-mutante --cobertura --base 4182a6b9`): as condições mudadas saem `coberta` ou `movida` (para `_gh_api.py`); `isenta · hooks/parecer.py:913` (equivalente declarado: `CLAUDE_PROJECT_DIR` sempre definida); `não coberto: tests/pesos-d4.json` (dado, sem decisão); cinco `spec editada` (hk3-parecer-pasta-10/11, v0457-fila27-2/3/4). Nenhuma condição mudada sem mutante, mas o mutante M1..M13 não alcança o ramo da cópia alheia (A1): a lista cobre o que o autor escreveu, não a matriz da família.
- Acessibilidade e E2E: não se aplicam (hook de linha de comando).

## Resultado
Reprovado por A1, defeito provado em controle de segurança do portão (`R-REVIEW`): o contorno do incidente fecha só fora de repositório git. Responsável sugerido: tech-lead (correção mínima no parecer de segurança, A1): em `pasta_do_gh`, devolver a cópia só sem `-R`/GH_REPO/URL ou com `hook.projeto` não nulo; senão clone da sessão com remoto do slug ou `bloquear`; somar fixtures S1 a S5 com recusa. A2 a A4 do parecer de segurança são `recomendado` e não os repito. Médios e baixos: nenhum.
