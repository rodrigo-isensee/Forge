---
tipo: revisao-devops
contrato: 1
pedido: release-0.26.0
branch: melhoria/release-0.26.0
commit: 998fdd5115212ef7ad892c0874574d859f60703c
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-20
---
# Review de devops: release-0.26.0

Revisão da leva da 0.26.0 (S-16, FECHAR-ESTAVEL, CATRACA-ENDURECER, CONF-CORRECAO e o fechamento de versão). Não sou o autor. Diff lido: `74e5bb7..998fdd5` em `.github/`, `.githooks/` e `scripts/`.

## Achados

## Parecer
Aprovado. Nenhum bloqueante; uma recomendação em "Detalhe dos achados".

**Só o modelo de PR mudou no pipeline.** O diff de `.github/`, `.githooks/` e `scripts/` tem um arquivo e uma linha: `.github/pull_request_template.md`, item desmarcado do rótulo `afrouxa-regra` (veio do #243, já com parecer em `docs/devops/fechar-estavel.md`). Nenhum workflow (`.github/workflows/` sem diferença, 0 linhas), nenhuma `permissions:`, nenhum segredo, nenhum hook e nenhum script de `scripts/` mudou. `release.yml` não mudou: nada escreve na `main` nem publica release antes do merge do dono (`R-MAIN`).

**`scripts/conferir-release.py` em PROTEGIDOS.** Confirmado em `tests/catraca.py:39-41` (entrada nova da leva, #244). O próprio script não mudou nesta leva (só passou a ser protegido). Efeito: o conjunto da promoção altera dois arquivos protegidos, `tests/catraca.py` e `bin/forge-check` (conferido por `git diff` contra `origin/homolog`), então a catraca vai pedir o rótulo `afrouxa-regra` do dono no PR develop → homolog; o tech-lead deve avisar o dono, e quem escreveu não aplica o rótulo. O modelo de PR não está em PROTEGIDOS, então sozinho não o exigiria; a correção vale para o que o parecer do #243 disse sobre ele.

**A checagem de release dispara na promoção.** `ci.yml:132-142` (inalterado) roda `scripts/conferir-release.py --base "$BASE" --so-se-versao-mudou` para base `homolog`. Simulação em clone próprio em `$TMPDIR`: merge `--no-ff` de 998fdd5 sobre `origin/homolog` (8d34b13, sem conflito), script rodado como o CI roda: `versão base: 0.25.0 | versão da release: 0.26.0` e `ok: changelog.d/ sem fragmentos pendentes`, rc 0. A checagem roda (não é pulada) e fica verde. Se entrar na `develop` algo com fragmento depois do E1.1, o passo fica vermelho apontando o arquivo; é o comportamento desejado, e o caminho é tirar a entrega da promoção ou fechar nova versão, nunca desligar o passo (`R-VERIFY`).

**O que esperar no PR develop → homolog.** Bateria completa verde (a mudança toca código da fábrica); o passo de release imprime as duas linhas acima; a catraca pede o rótulo `afrouxa-regra` por `tests/catraca.py` e `bin/forge-check` (rótulo posto antes num PR mesclado vale para o mesmo conteúdo, #242, mas esta é a primeira promoção desse conteúdo, então pede ao dono); "Nada pula degrau" exige head `develop`. No PR homolog → main, a mesma checagem roda sem a flag e exige versão nova e `[Não publicado]` vazio.

**Ferramentas.** `actionlint`, `shellcheck` e `zizmor` não estão no PATH deste ambiente: lacuna registrada; não houve mudança de workflow ou shell a validar, e o job `bateria` as roda no PR.

## Detalhe dos achados
- R1 (recomendado, sem relação com a leva): `scripts/conferir-release.py` trata base ilegível como `0.0.0` (R1 do parecer da 0.25.0, ainda aberto); com `fetch-depth: 0` a base sempre existe, sem risco prático. Cartão próprio, esforço P.

## Custo e rollback
Custo: zero (`R-CUSTO`). Nenhum job, runner, cache, artefato, download, segredo ou serviço novo; a leva só edita um texto de modelo em `.github/`. O repositório é público, e os minutos de runner padrão não são cobrados. Rollback: reverter a promoção (ou o commit do modelo de PR) em `melhoria/*`; não há migração nem estado externo.
