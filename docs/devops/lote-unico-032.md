---
tipo: revisao-devops
contrato: 1
pedido: lote-unico-032
branch: melhoria/lote-unico-032
commit: cd93720c89c21f935783c98501d3817a5b7ad3f7
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-03
---
# Review de devops: lote-unico-032

## Parecer
Aprovado. No diff `b2580c6...9f32431` a parte de devops é `.github/workflows/ci.yml` (7 linhas em 3 trechos, L01), `scripts/suite-paralela.py` (L32) e `bin/forge-mutante` (L33). Nenhum `Dockerfile`, `compose*`, IaC nem `.githooks/` mudou.

Ferramentas: `shellcheck` presente (sem script de shell novo no diff); `yaml.safe_load` do `ci.yml` e `py_compile` dos dois scripts passam. `actionlint` não está no PATH: lacuna registrada, o trecho alterado é só um `if`/`grep` dentro de `run:` e uma linha de `unittest`.

### L01, gate do commit só de parecer (`ci.yml:5-7`, `ci.yml:106-108`, `ci.yml:120`)
- O gate pula os passos pesados só se todo arquivo do commit está em `docs/(reviews|qa|security|devops|ux)/`, nenhum é modelo `_*` nem está em `docs/security/{ameacas,aceites}/` e o check `bateria` do commit anterior é `success` (app `github-actions`, o mais recente). Sondei a expressão com 10 entradas: parecer de devops e de ux juntos pulam; parecer com `bin/forge-check`, `tests/x.py`, `docs/uxx/` ou `?` (diff ilegível) rodam tudo; `docs/devops/_modelo.md`, `docs/security/ameacas/*` e `docs/qa/sub/_x.md` rodam tudo. Commit com código não passa.
- Continua restrito a `pull_request` com base `develop` e ação `synchronize`; falha de leitura cai em `pesada=true`. O passo "Testes que leem pareceres" ganhou `NeutralidadeDoNucleo`, coerente com a lista de leitura de pareceres. Sem `continue-on-error`, `[skip ci]`, check desligado ou `paths-ignore` (`R-VERIFY`). `permissions` e SHAs das ações não mudaram.
- Junção com a `develop` atual (`c6244ac`): `git merge-tree --write-tree origin/develop 0c90721` junta o `ci.yml` automaticamente e os 3 `timeout-minutes` do #429 (20, 25, 25) permanecem. A junção só tem um conflito, em `tests/test_catraca.py:2697-2703` (fora de `.github/`): ver A1.

### L32, registro da suíte vermelha (`scripts/suite-paralela.py:469-512`, chamada em `:587`)
Grava em `~/.forge-contrib/suite-vermelha.jsonl`, fora do repositório; não escreve no CI (`GITHUB_ACTIONS=true` sai antes), não cria a pasta, recusa pasta de outro dono, com link ou gravável por outros, abre com `O_NOFOLLOW` e `0600`, guarda só ids e números e não muda o código de saída. O pre-push chama o mesmo script, então o efeito local é o mesmo e sem consequência para o push. Sem artefato, cache ou serviço novos.

### L33, `forge-mutante --processos K` (`bin/forge-mutante`)
Nenhum workflow nem o pre-push chamam o `forge-mutante` (conferido por busca): o CI não muda. Padrão 1 (série), teto 4 (o mesmo do pool da suíte), cada mutante na sua cópia, controle calculado uma vez por conjunto de testes sob trava, e erro ou sinal mata os grupos de processo em curso e apaga as cópias. Só biblioteca padrão e CPU local.

## Revalidação da volta 2 (delta `0c90721..9f32431`, head `9f32431`)
Aprovado, sem bloqueante. No delta, `.github/` só muda no `ci.yml` (3 linhas de `timeout-minutes`, vindas do merge da `develop` `6ef56a0`, #429); `Dockerfile*`, `compose*`, IaC, `.githooks/` e `scripts/` não mudaram. `bin/forge-check` tem as correções L16, L18, L13, L15, L49, L35, L31 e L17, sem relação com o pipeline.
- `ci.yml` depois do merge: `yaml.safe_load` passa; o gate do L01 (regex `docs/(reviews|qa|security|devops|ux)/`, `--no-renames`, `!cancelled()`, `permissions`, SHAs) está intacto e os `timeout-minutes` são 20, 25 e 25, juntos, sem marcador de conflito. `tests.test_catraca` (`test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore`, `test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde`) passa. A `develop` `c6244ac` já é ancestral do head.
- Conflito do A1 anterior (item removido dos achados) (`tests/test_catraca.py`): resolvido com as duas linhas, o `assertIn("docs/(reviews|qa|security|devops|ux)/", ci)` e o `assertEqual(..., ["20", "25", "25"])`. A1 fechado.
- L18 (`ocupacao_da_trava`, `bin/forge-check:1940`): agora só executa `.githooks/pre-push --status` se o texto do hook contém `--status`, sem seguir link; não executa hook alheio. Melhora o que o parecer de segurança apontou, sem custo nem serviço novo.
- O A2 anterior (gate por diretório e não por `.md`) segue como recomendação, sem mudança.
- Ferramentas: `shellcheck` presente (nenhum shell novo); `actionlint` ausente do PATH (lacuna registrada); `py_compile` do `bin/forge-check` passa.
- Custo zero (`R-CUSTO`): nenhum job, runner, cache ou artefato novo; os tetos de tempo maiores vêm da `develop` e ficam dentro da franquia. Rollback: reverter o commit da correção correspondente; sem migração.

## Revalidação da volta 3 (delta `9f32431..cd93720`, head `cd93720`)
Aprovado, sem bloqueante. `git diff --stat 9f32431..cd93720 -- .github .githooks scripts Dockerfile* compose*` vem vazio: o pipeline, os containers, a IaC e o pre-push não mudam. `bin/forge-check` muda só na `RE_LINHA_REPROVADA` (L13: `escopo:` de integração da base, sem commit e união de N briefs deixam de contar como reprovação) e no texto de uso, e `tests/test_forge.py` e `tests/config.json` ganham os casos e contagens do L35 (9f5c191); o `forge-check vereditos` só mede e o CI e o pre-push não o chamam. `py_compile` do `bin/forge-check` e `yaml.safe_load` do `ci.yml` passam; `actionlint` segue fora do PATH (lacuna registrada). Custo zero (`R-CUSTO`); rollback por revert do commit, sem migração. O A2 segue como recomendação.

## Achados
- A2 (recomendado) .github/workflows/ci.yml:106 · o gate pula por diretório, não por tipo de arquivo, então um arquivo executável em `docs/ux/` ou `docs/devops/` pularia a bateria (o mesmo já valia para `docs/reviews/` e `docs/qa/`). Sem caminho de ataque concreto hoje; se preocupar, restringir a `\.md$`.

## Custo e rollback
Custo zero (`R-CUSTO`): nenhum job, runner, cache, artefato ou serviço novo; o gate só reduz minutos de CI em commits de parecer. Rollback: reverter o commit do L01 devolve o gate anterior (`docs/(reviews|qa)/`); L32 e L33 são locais e opcionais, revertidos por commit sem migração.
