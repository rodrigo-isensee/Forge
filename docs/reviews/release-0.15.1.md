---
tipo: review
contrato: 1
pedido: pos-release-0.15.0
branch: melhoria/release-0.15.1
commit: 82d0d52111a274a2a166e4ab7e08fc2f2c45a3b1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Review independente: versão 0.15.1 e comandos de fechamento da 0.15.0

Escopo: `bad3edd..d155d29` (1 commit, `chore(release): prepara a versão 0.15.1`, autor não é este revisor) e o arquivo de comandos ao dono `~/.forge-contrib/docs/briefs/pos-release-0.15.0-comandos.md` (fora do repositório, revisado como insumo do pedido).

Veredito: **APROVADO** para a branch. No arquivo de comandos, dois ajustes recomendados (abaixo) antes de entregá-lo ao dono; nenhum bloqueia o merge da branch.

## Diff (conferido)
- `git diff --stat bad3edd..d155d29`: só `.claude-plugin/plugin.json` (1 linha, `version` 0.15.0 para 0.15.1), `CHANGELOG.md` (+5) e `changelog.d/ci-local-jobs-consolidados.md` apagado. Nada além.
- Entrada do #145 literal: a linha 2 do fragmento em `bad3edd` e a linha nova do `CHANGELOG.md` comparadas com `diff`: idênticas. Está em `## [0.15.0]`, sob `### Corrigido` (o mesmo tipo do fragmento), última da lista; nenhuma outra linha da 0.15.0 mudou.
- `## [0.15.1] - 2026-10-15` entre `## [Não publicado]` (vazia) e `## [0.15.0]`, com `### Corrigido` e uma entrada que descreve só a correção das notas. Patch é coerente com a regra "Versão" do `CLAUDE.md` (mudança que chega à `main` sobe versão; correção = patch).
- `changelog.d/` some do repositório (era o único arquivo em `bad3edd`, sem README). Efeito nos comandos:
  - `bin/forge-changelog novo`: `arquivo.parent.mkdir(exist_ok=True)` recria a pasta; simulado num clone em `$TMPDIR` (`gravado em changelog.d/teste.md`).
  - `fragmentos()` usa `Path.glob` em pasta ausente: lista vazia, sem erro. `conferir-release` nesta branch: `ok: changelog.d/ sem fragmentos pendentes`, rc=0.
  - Checagem do PR para a `develop` (`forge-changelog conferir --base bad3edd`): `PR de release (versão mudou): o changelog fechado é conferido na promoção para a main.`, rc=0.
  - Checagem do PR para a `main` (`ci.yml`, passo "main - release exige versão nova e changelog fechado"): base 0.15.0 < 0.15.1, `## [0.15.1]` presente, `[Não publicado]` vazia, sem fragmentos: passa.
- Commit: Conventional Commits em português, corpo claro, atribuição presente.

## Arquivo de comandos (conferido)
- Ordem segura: PR da `develop`, promoção para `homolog`, PR `homolog` para `main` (merge do dono, `R-MAIN`), releases só depois do `git fetch`, remoção de remotas por último. Nenhum `--force` nem `--no-verify` (`grep` sem ocorrências); `git push origin --delete` só em `melhoria/*`.
- Alvos: `git log origin/main --first-parent` com o `plugin.json` de cada commit: `2d8d5e5` 0.13.0, `4d6087d` 0.14.0 (primeiro), `3040a8a` e `3a34df6` 0.14.0, `408c2eb` 0.15.0 (primeiro). v0.14.0 = `4d6087d` e v0.15.0 = `408c2eb` corretos.
- Extração das notas: o `awk` é o mesmo do `release.yml`, caractere a caractere; muda só a fonte (`git show origin/main:CHANGELOG.md`), o que é intencional para a 0.15.0 sair com a entrada do #145.

## Achados
| # | Onde | Problema | Sugestão | Severidade |
|---|---|---|---|---|
| 1 | comandos, passos 1 e 3 (`gh pr merge ... --merge`) | `R-FLUXO` e ADR 0008 mandam squash na `develop` e na `main` (merge commit só na `homolog`). O histórico recente (`#145`, `#148`, `#150`) também usou merge commit, então a prática já diverge da regra. | Usar `--squash` nos passos 1 e 3 (o passo 2, `--merge`, está certo) ou o dono decidir manter merge commit e a regra/ADR ser atualizada (cartão separado). O passo 4 continua certo nos dois casos (`git rev-parse origin/main`). | recomendado |
| 2 | comandos, passo 4 (`--target 4d6087d`, `--target 408c2eb`) | A API de releases do GitHub espera em `target_commitish` um nome de branch ou o SHA completo; SHA abreviado pode ser recusado (422). | Usar os SHAs completos: `4d6087db5a2e15dfdff7ecc6c18f8b8c101ad3e8` e `408c2ebba137666000f6df670f8a7e6f0602cb78`. | recomendado |
| 3 | comandos, passo 4 | Notas vazias passam caladas se a seção não for achada. Se o Actions voltar a ter cota, o `release.yml` cria a v0.15.1 sozinho no push da `main` e o `gh release create v0.15.1` falha (sem dano). | `test -s` no arquivo de notas antes de cada `gh release create`; conferir `gh release view v0.15.1` antes de criá-la; conferir que `git show origin/main:.claude-plugin/plugin.json` diz 0.15.1 antes de usar `origin/main` como alvo. | recomendado |

## Pendências (não são deste review)
- Suíte e `scripts/validar-plugin.sh`: QA (brief 3). Sem mudança em pipeline, container, IaC nem superfície de segurança: sem parecer de `devops-engineer` ou `security-engineer`.

## Revalidação após merge da develop
Merge `82d0d52` trouxe da `develop` (930d6bb, K1 do conferente) `agents/conferente.md`, `agents/jarvis.md`, regras `R-BRIEF`/`R-DECISAO`/`R-PROVA`, modelo de pedido, `tests/` e os pareceres da K1: já revisados e aprovados nos PRs da K1, fora deste escopo. `origin/develop` (930d6bb) está contida no HEAD.
- Diff próprio (`git diff origin/develop...HEAD`): `plugin.json` 0.15.1, `CHANGELOG.md`, `changelog.d/ci-local-jobs-consolidados.md` removido e os pareceres de review e QA. Igual ao aprovado em `d155d29`: `git diff d155d29..82d0d52 -- CHANGELOG.md .claude-plugin/plugin.json` vazio.
- `changelog.d/conferente-k1.md` (da `develop`) segue como fragmento pendente e não entra na `[0.15.1]`, conforme a decisão técnica do pedido; os comandos ao dono não mudam por causa disso.
- Achados 1 a 3 (recomendados, só no arquivo de comandos) continuam valendo; nada novo. Suíte e `validar-plugin` sobre `82d0d52`: do autor (653 OK, "Validation passed"); QA roda de novo.
