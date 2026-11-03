---
tipo: revisao-devops
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: 0c90721c86b15d89ea0aec0befa1850b45948698
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-03
---
# Review de devops: lote-unico-032

## Parecer
Aprovado. No diff `b2580c6...0c90721` a parte de devops é `.github/workflows/ci.yml` (7 linhas em 3 trechos, L01), `scripts/suite-paralela.py` (L32) e `bin/forge-mutante` (L33). Nenhum `Dockerfile`, `compose*`, IaC nem `.githooks/` mudou.

Ferramentas: `shellcheck` presente (sem script de shell novo no diff); `yaml.safe_load` do `ci.yml` e `py_compile` dos dois scripts passam. `actionlint` não está no PATH: lacuna registrada, o trecho alterado é só um `if`/`grep` dentro de `run:` e uma linha de `unittest`.

### L01, gate do commit só de parecer (`ci.yml:5-7`, `ci.yml:106-108`, `ci.yml:120`)
- O gate pula os passos pesados só se todo arquivo do commit está em `docs/(reviews|qa|security|devops|ux)/`, nenhum é modelo `_*` nem está em `docs/security/{ameacas,aceites}/` e o check `bateria` do commit anterior é `success` (app `github-actions`, o mais recente). Sondei a expressão com 10 entradas: parecer de devops e de ux juntos pulam; parecer com `bin/forge-check`, `tests/x.py`, `docs/uxx/` ou `?` (diff ilegível) rodam tudo; `docs/devops/_modelo.md`, `docs/security/ameacas/*` e `docs/qa/sub/_x.md` rodam tudo. Commit com código não passa.
- Continua restrito a `pull_request` com base `develop` e ação `synchronize`; falha de leitura cai em `pesada=true`. O passo "Testes que leem pareceres" ganhou `NeutralidadeDoNucleo`, coerente com a lista de leitura de pareceres. Sem `continue-on-error`, `[skip ci]`, check desligado ou `paths-ignore` (`R-VERIFY`). `permissions` e SHAs das ações não mudaram.
- Junção com a `develop` atual (`c6244ac`): `git merge-tree --write-tree origin/develop 0c90721` junta o `ci.yml` automaticamente e os 3 `timeout-minutes` do #429 (20, 25, 25) permanecem. A junção só tem um conflito, em `tests/test_catraca.py:2697-2703` (fora de `.github/`): ver A1.

### L32, registro da suíte vermelha (`scripts/suite-paralela.py:469-512`, chamada em `:587`)
Grava em `~/.forge-contrib/suite-vermelha.jsonl`, fora do repositório; não escreve no CI (`GITHUB_ACTIONS=true` sai antes), não cria a pasta, recusa pasta de outro dono, com link ou gravável por outros, abre com `O_NOFOLLOW` e `0600`, guarda só ids e números e não muda o código de saída. O pre-push chama o mesmo script, então o efeito local é o mesmo e sem consequência para o push. Sem artefato, cache ou serviço novos.

### L33, `forge-mutante --processos K` (`bin/forge-mutante`)
Nenhum workflow nem o pre-push chamam o `forge-mutante` (conferido por busca): o CI não muda. Padrão 1 (série), teto 4 (o mesmo do pool da suíte), cada mutante na sua cópia, controle calculado uma vez por conjunto de testes sob trava, e erro ou sinal mata os grupos de processo em curso e apaga as cópias. Só biblioteca padrão e CPU local.

## Achados
- A1 (recomendado) tests/test_catraca.py:2697 · a junção com a `develop` (`c6244ac`) conflita neste ponto: a `develop` pôs a linha dos `timeout-minutes` (#429) e o lote trocou o `assertIn` para `docs/(reviews|qa|security|devops|ux)/`. A resolução é manter as duas linhas (o `ci.yml` resultante traz o novo regex e os três tetos); o `tech-lead` resolve ao atualizar a branch antes do PR. Não bloqueia: o conflito está em teste, não em pipeline, e o conteúdo de `.github/` junta limpo.
- A2 (recomendado) .github/workflows/ci.yml:106 · o gate pula por diretório, não por tipo de arquivo, então um arquivo executável em `docs/ux/` ou `docs/devops/` pularia a bateria (o mesmo já valia para `docs/reviews/` e `docs/qa/`). Sem caminho de ataque concreto hoje; se preocupar, restringir a `\.md$`.

## Custo e rollback
Custo zero (`R-CUSTO`): nenhum job, runner, cache, artefato ou serviço novo; o gate só reduz minutos de CI em commits de parecer. Rollback: reverter o commit do L01 devolve o gate anterior (`docs/(reviews|qa)/`); L32 e L33 são locais e opcionais, revertidos por commit sem migração.
