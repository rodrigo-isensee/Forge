---
tipo: revisao-devops
contrato: 1
pedido: release-0.25.0
branch: melhoria/release-0.25.0
commit: 630d200aff68570aa1a184be41b645ecb8d60ab8
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-20
---
# Review de devops: release-0.25.0

Revisão a posteriori da DV-4 (implementação 37212eb, mesclada pelo dono no #229 e levada à homolog no #231 sem pareceres; decisão do dono "B"). Não sou o autor. O `ci.yml` e o `scripts/conferir-release.py` do HEAD revisado (630d200) são idênticos aos de 37212eb e aos da `origin/homolog` (`diff` vazio).

## Achados

## Parecer
Aprovado. Nenhum bloqueante; duas recomendações em "Detalhe dos achados".

**Um passo, duas chamadas.** `.github/workflows/ci.yml:132-142`: o antigo passo inline da main virou um passo só, com `if:` em `github.event_name == 'pull_request'` e `github.base_ref` igual a `main` ou `homolog`. No `run:`, `BASE_REF = homolog` chama `scripts/conferir-release.py --base "$BASE" --so-se-versao-mudou`; os demais casos (só pode ser `main`) chamam o script sem a flag, com o comportamento antigo. A regra (versão sobe, entrada `## [X.Y.Z]`, `[Não publicado]` vazio, nenhum fragmento em `changelog.d/` via `bin/forge-changelog conferir-release`) mora só no script; o workflow não repete texto.

**Condição da homolog, nos eventos e refs que o workflow usa.** Gatilho `pull_request` com `opened`, `synchronize` e `reopened` (ci.yml:8-9): o passo roda na abertura do PR de promoção e a cada push na `develop` enquanto ele estiver aberto. Em `pull_request`, `github.base_ref` é o nome da branch de destino (`homolog`/`main`), o que o `if:` e o `case` de "Nada pula degrau" já usam. `BASE` é `github.event.pull_request.base.sha`; o checkout (ci.yml:51-54) é o merge commit do PR com `fetch-depth: 0`, então o `git show <base>:.claude-plugin/plugin.json` acha o commit da base e o `plugin.json` lido no disco é o resultado da promoção. Com a flag, versão igual à da base sai 0 sem conferir (promoção sem release); versão diferente roda a checagem inteira, e versão menor que a da base reprova (`a <= b`, scripts/conferir-release.py:34). Push na homolog/main e `workflow_dispatch` não rodam o passo (não há PR nem base). Entrada vem por `env:`, sem `${{ }}` dentro do `run:` (o teste `test_entrada_nao_confiavel_so_por_env` garante).

**Esta promoção vai disparar a checagem.** Simulação em clone próprio em `$TMPDIR`: merge `--no-ff` de 630d200 sobre `origin/homolog` (sem conflito) e o script rodado como o CI roda:
- `--base <homolog> --so-se-versao-mudou` no merge: `versão base: 0.24.0 | versão da release: 0.25.0`, `ok: changelog.d/ sem fragmentos pendentes`, rc 0 (a checagem rodou, não foi pulada).
- Mesmo comando com a homolog sem a release (0.24.0 → 0.24.0): `promoção sem versão nova: não é release`, rc 0.
- Prova negativa: o merge com um fragmento a mais em `changelog.d/` reprova com rc 1 (`Há fragmentos em changelog.d/ (sobra.md)`).
- `--base <main>` sem a flag (PR homolog → main de 0.24.0 para 0.25.0): rc 0. A `main` ainda não tem o script, sem efeito: o passo roda o script do checkout do PR, não o da base.

**O que esperar no PR develop → homolog.** No job `bateria`, o passo "release exige versão nova e changelog fechado (main sempre; homolog só se a versão subiu)" imprime `versão base: 0.24.0 | versão da release: 0.25.0` e `ok: changelog.d/ sem fragmentos pendentes` e fica verde. Se alguma entrega entrar na `develop` depois do E1.1 com fragmento próprio (fora do escopo da release), o passo fica vermelho apontando o arquivo: é o comportamento desejado da DV-4, não falha do CI; o caminho é tirar a entrega da promoção ou fechar uma nova versão, nunca desligar o passo (`R-VERIFY`). O gate de "commit só de parecer" (ci.yml:68) só vale para base `develop`; na homolog a bateria inteira roda sempre (`R-FLUXO`).

**Testes.** `tests/test_conferir_release.py` (10 testes: as duas chamadas, a flag só no ramo da homolog, a entrada só por `env:` e o comportamento em repositório git temporário) passa: `Ran 10 tests ... OK`. As três asserções antigas (`test_changelog.py`, `test_ci_local.py`, `test_forge.py`) passaram a apontar para o script, sem afrouxar o que verificavam.

**Ferramentas.** `actionlint`, `shellcheck` e `zizmor` não estão no PATH deste ambiente: lacuna registrada. O job `bateria` roda os três no PR (versões e sha256 fixos, ci.yml:46-49 e 93-113). O shell novo é um `if/else` de duas linhas com variáveis entre aspas.

## Detalhe dos achados
- R1 (recomendado) `scripts/conferir-release.py:21-23`: base ilegível (sem `plugin.json` ou JSON quebrado) vira `0.0.0`. Na homolog isso falha fechado (versão difere, a checagem roda); na main, falha aberto na parte "versão sobe". O comportamento veio igual do passo inline anterior, então não é regressão, e com `fetch-depth: 0` a base sempre existe. Sugestão para um cartão próprio: sair com erro quando o `git show` da base falhar, em vez de assumir `0.0.0`.
- R2 (recomendado) `tests/test_conferir_release.py`: falta um caso de versão menor que a da base com `--so-se-versao-mudou` (o script reprova, como deve, mas nenhum teste segura isso). Esforço P, dono: devops-engineer em cartão próprio.

## Custo e rollback
Custo: zero adicional (`R-CUSTO`). Nenhum job, runner, cache, artefato ou download novo; é um script Python de menos de um segundo dentro do job `bateria` que já existia, em `ubuntu-24.04` padrão. O repositório é público (`gh repo view`: `PUBLIC`), então os minutos de runner padrão não são cobrados. Nenhum workflow passou a escrever na `main` nem a publicar release (`R-MAIN`): `release.yml` não mudou. Rollback: reverter 37212eb (volta o passo inline só na main) em `melhoria/*`, com envio pelo dono (o token do bot não tem o escopo `workflow`) e o rótulo `afrouxa-regra` no PR, como toda mudança em `.github/`.
