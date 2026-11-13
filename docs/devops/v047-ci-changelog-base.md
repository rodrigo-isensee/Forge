---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-ci-changelog-base
commit: 136cf316b34434dbefc9dbe3dd41ca98c49b3fbb
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-13
---
# Review de devops: v047-ci-changelog-base

## Achados

## Detalhes
Aprovado no head 136cf316 (E1.52, revisada pela E1.56 em instância que não fez a entrega).

- `.github/workflows/ci.yml` (passo "develop - mudança na fábrica exige fragmento"): `BASE=$(git rev-parse HEAD^1)` no lugar de `github.event.pull_request.base.sha`. No checkout de `pull_request` o HEAD é o merge commit e o primeiro pai é a ponta atual da base; o SHA do evento fica velho quando a `develop` anda. Igual à catraca e ao passo de pareceres.
- O job faz checkout com `fetch-depth: 0`, então o pai existe para o `git diff`. O `run:` usa o shell padrão do Actions (`bash -e`): se `rev-parse` falhar, o passo falha, não pula. A `if:` não mudou e não há `continue-on-error`. Nenhuma entrada não confiável em `run:` (a `env: BASE` com expressão saiu).
- Barra PR sem fragmento: cópia descartável do head, commit em `agents/jarvis.md` sem fragmento, `forge-changelog conferir --base HEAD~1` saiu rc=1 ("Registre a mudança num fragmento novo em changelog.d/").
- Teste `MatrizNeedsEAgregadorTest.test_changelog_compara_com_o_pai_do_commit_de_juncao_...` roda o `run:` real do ci.yml num repo temporário com a develop adiantada, injeta um `BASE` velho e confere que sai o pai da junção. Os 11 testes da classe passam. O mutante M1 (voltar a `"$BASE"`) está coberto por esse teste e o manifesto aponta para o teste certo.
- Não abre caminho para pular: nenhuma mudança de gatilho, permissão, concurrency ou check exigido.
- Ferramentas: `shellcheck` presente (o `run:` é trivial); `actionlint` ausente do PATH (lacuna; o CI do PR a cobre). Não havia PR aberto, então o CI do PR não foi consultado; rodaram só testes leves e afetados.
- Mudança em arquivo protegido de `.github/`: o `tech-lead` avalia a necessidade do rótulo `afrouxa-regra`; o passo não afrouxa nada, só corrige a base.

## Custo e rollback
Zero minuto novo de CI e nenhum recurso novo (`R-CUSTO`). Rollback: reverter o commit 136cf316 (volta ao `base.sha` do evento).
