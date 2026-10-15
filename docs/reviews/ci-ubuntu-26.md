---
tipo: review
contrato: 1
pedido: ci-ubuntu-26
branch: melhoria/ci-ubuntu-26
commit: 77a4028ba046ccf58774565adffbe73c3e505b6d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Code review: CI fixado em `ubuntu-24.04` (ci-ubuntu-26)

## Revalidação (rodada 3): aprovado
HEAD `77a4028` (merge `448d877` com a develop `3f4a21e`). Os 3 workflows conflitaram com o #138 e foram resolvidos ficando com a versão da develop e trocando só o rótulo. Conferido: `git diff origin/develop -- .github CHANGELOG.md` mostra só 4 linhas `runs-on` (`ubuntu-latest` para `ubuntu-24.04`: 1 em `catraca.yml`, 2 em `ci.yml`, 1 em `release.yml`); o `CHANGELOG.md` é idêntico ao da develop; a entrada vai no fragmento `changelog.d/ci-ubuntu-26.md` (`### Alterado`, com o rótulo `afrouxa-regra` e o parecer de devops). Os 4 `runs-on` de `.github/` estão em `ubuntu-24.04` e nenhum job novo do #138 ficou em `ubuntu-latest`. Fora de `.github/` e do fragmento, o diff só traz os pareceres em `docs/`; `bin`, `hooks`, `tests` e `scripts` são idênticos aos da develop.

Registro: a falha de `tests.test_ci_local` vem da develop (`026231f` e `3f4a21e`) e está em correção em `melhoria/ci-local-jobs-consolidados`; não é desta branch e não reprova o #136. Pareceres de devops, segurança e QA precisam carregar o commit `77a4028` (delegações próprias); push e merge são do dono.

## Volta 2: aprovado
O achado bloqueante da volta 1 está resolvido. O `docs/devops/ci-ubuntu-26.md` agora traz `commit: bbc658f13b9d57fd551f73e17b57975799146fd7`, corrigido em `a73ed6e`. O `8b52aa0` acrescenta o parecer de segurança (`docs/security/ci-ubuntu-26.md`), aprovado e sem achado bloqueante. O diff `229bceb..8b52aa0` toca só esses dois arquivos de `docs/`, sem mudança de código. Os recomendados 2 e 3 e o item 4 da volta 1 viraram cartões e não bloqueiam este PR. O que falta no portão é o parecer de QA.

## Volta 1: reprovado (histórico)
Reprovado só pelo achado 1, que é um metadado do parecer de devops. A troca nos workflows e o CHANGELOG estavam corretos.

Escopo: diff `develop..bbc658f` com 3 commits (`b87664b`, `acacc7c`, `bbc658f`). Arquivos: `.github/workflows/ci.yml`, `.github/workflows/catraca.yml`, `.github/workflows/release.yml`, `CHANGELOG.md` e `docs/devops/ci-ubuntu-26.md`. Parecer de devops: `docs/devops/ci-ubuntu-26.md`, aprovado. O parecer de segurança (`R-SEGURANCA`, gatilho `.github/`) é do `security-engineer` e fica em `docs/security/`. Ele não é refeito aqui.

## Conferido
- **Cobertura dos jobs completa.** `git grep -n ubuntu-latest HEAD` só encontra o texto do `CHANGELOG.md` e do parecer de devops, e nenhum `runs-on`. Os 12 `runs-on` de `.github/` usam `ubuntu-24.04`: 9 em `ci.yml` (testes, shell, workflows, plugin, instalacao, versao, fluxo, segredos, pareceres), 2 em `catraca.yml` (catraca, pr-texto) e 1 em `release.yml`. Nenhum outro workflow existe em `.github/workflows/`, e `templates/` não tem `ubuntu-latest`.
- **CHANGELOG e versão batem com o job `versao`.** `plugin.json` continua `0.13.0` na `develop` e na branch, porque a versão não sobe no PR (ADR 0006). O PR toca `docs/`, então o passo da `develop` exige uma linha nova em `## [Não publicado]`. A linha existe, em `### Alterado`, e cita o rótulo `afrouxa-regra` e o parecer de devops.
- **Faz o que o cartão pede, nem mais nem menos.** A mudança é só a troca de rótulo. Não há matriz, runner maior, passo novo nem ação nova.
- **`R-CUSTO`.** Mesmos jobs e mesmo tipo de runner (padrão), então o custo é zero adicional. A cota do runner privado é outro assunto, registrado pelo devops como fora do alcance.
- **`R-VERIFY` e commits.** São 3 commits em Conventional Commits em português, sem `--no-verify` nem `--force`. O `bbc658f` troca "Node.js" por "runtime JS" por causa da neutralidade (`R-NEUTRO`). É uma correção coerente.
- **Rollback.** Basta reverter `b87664b`.

## Ferramentas (citadas, não refeitas)
- `actionlint` e `zizmor` rodam no job `workflows` do CI e não estão neste ambiente. Pendência: confirmar o job verde no PR.
- `python3 -m unittest discover -s tests`: 561 testes na `develop` (checkout `~/Forge`), todos OK. Na worktree desta branch, 561 testes com 7 falhas, todas em `test_forge.JarvisForgeAbrir`. As falhas não vêm do diff. `git diff --quiet develop HEAD -- tests scripts hooks bin` confirma que esses arquivos são idênticos, e o mesmo teste (`test_tag_origin_develop_nao_e_usada_ao_abrir`) passa no `~/Forge` e falha na worktree em `~/.forge-contrib/wt/`. A falha depende do lugar onde o checkout está, e o CI usa checkout comum. Isso fica fora deste pedido e vira cartão próprio (abaixo).
- `python3 tests/catraca.py --base develop`: aponta só `R-CONFORMIDADE` para os 3 workflows, o esperado. Passa com o rótulo `afrouxa-regra` do dono.
- `bin/forge-check docs`: sai 0 com este parecer.

## Achados
Bloqueia:
1. **`docs/devops/ci-ubuntu-26.md:6`: `commit: b87664b...` está desatualizado.** O `bbc658f` mudou o `CHANGELOG.md` depois desse commit. `bin/forge-check pr ci-ubuntu-26` aponta `commit: desatualizado: CHANGELOG.md mudou depois do parecer`. O job `pareceres` do CI fica vermelho por isso, conforme simulado com `python3 tests/catraca.py --modo pareceres --base develop --head HEAD --ramo=melhoria/ci-ubuntu-26 --base-ref develop`. **Sugestão:** o devops confere o `bbc658f` e atualiza o `commit:` do parecer para o head revisado. A correção é dele.

Recomendados (vão para o cartão da migração à 26.04, não para este PR):
2. `.github/workflows/ci.yml` (jobs versao, fluxo, segredos, pareceres), `catraca.yml` e `release.yml` usam o `python3` do sistema, sem `setup-python`. Fixar o Python nesses jobs na migração. O devops já apontou isso.
3. A data de 19/11/2026 é o fim previsto da onda. Abrir o cartão "migrar CI para ubuntu-26.04" agora, com prazo, para a fixação não virar permanente.

Fora do pedido:
4. `tests/test_forge.py:1102` (`JarvisForgeAbrir`) falha em 7 testes quando a suíte roda numa worktree em `~/.forge-contrib/wt/` e passa no `~/Forge`. Pelo README ("Sandbox do Bash"), o fluxo de contribuição usa justamente essas worktrees. Abrir um cartão para isolar a causa.

## Riscos
- O mesmo portão também cobra o parecer de segurança (`docs/security/`, `R-SEGURANCA`), que ainda não está commitado na branch. Ele está em andamento com o `security-engineer`.
- **O rótulo vale pelo conteúdo.** `tests/catraca.py` (`PARECERES`) isenta só `docs/reviews/` e `docs/qa/`. Se o parecer de segurança em `docs/security/` for commitado depois do rótulo `afrouxa-regra`, o rótulo deixa de valer. O dono deve aplicar o rótulo só depois que o parecer de segurança estiver na branch.
- O push exige o escopo `workflow`, então quem faz o envio é o dono.
- Se a 24.04 for descontinuada antes da migração, o CI para. Por isso o achado recomendado 3.
