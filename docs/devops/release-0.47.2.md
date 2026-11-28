---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.2
branch: melhoria/v047-release-0472
commit: b57bb55861115f7b9b5236d4349b4807fe842aa8
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-16
---
# Review de devops: release-0.47.2 (develop 86ac0fc até b57bb55)

## Parecer
Aprovado, sem achado bloqueante. O commit de release b57bb55 só muda `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` (versão 0.47.2), `CHANGELOG.md` (entrada 0.47.2 fechada) e remove os fragmentos de `changelog.d/`. Nenhum arquivo de `.github/`, `.githooks/`, `Dockerfile*`, `compose*` ou IaC muda no delta sobre a develop. Não sou autor de nenhuma parte da leva. Manifesto e CHANGELOG batem em 0.47.2.

O delta de pipeline da leva sobre a `main` (`git diff origin/main -- .github`) é só `.github/workflows/ci.yml` (+10 -2), já na develop: o passo "Nada pula degrau" passa a ler o par head/base da tabela única PROMOCOES (`tests/catraca.py --modo degrau`), da develop do servidor e não do PR, com `HEAD_REF`, `HEAD_SHA`, `HEAD_REPO` e `BASE_REPO` por variável de ambiente (sem interpolação em `run:`).

## Achados
- A1 (recomendado) .github/workflows/ci.yml:506 · a leva muda `.github/` em relação à `main`: o PR `homolog` → `main` precisa do rótulo `afrouxa-regra` do dono (catraca) e do corpo com a saída de `tests/catraca.py --modo rotulados` (ADR 0008). Avisar o `tech-lead`; não bloqueia.

## Detalhes
ci.yml de 3 partes (voltou com o revert do #576), conferido no head: `permissions: contents: read` no topo; `concurrency` cancelando o ref obsoleto; `timeout-minutes` em todos os 14 jobs; as 31 linhas `uses:` fixadas por SHA de 40 caracteres; sem `continue-on-error`, `[skip ci]`, `pull_request_target` nem `--no-verify` fora de comentário.

Agregadores: `bateria` exige `success` de `bateria`, `verificacoes`, `partes-doze` e `pulados-doze`; `pareceres` só aceita `skipped` fora de `pull_request`, então em PR pulado ou cancelado falha (J11). `bateria (python 3.14)` exige `partes-quatorze`, `pulados-quatorze` e `instalacao-quatorze` em `success`; ambos com `if: always()`, logo pulo e cancelamento reprovam. Os checks nomeados seguem os do ruleset do dono, que não foi tocado (`R-CONFORMIDADE`).

Promoção: develop → homolog e homolog → main passam por "Nada pula degrau" e por "release exige versão nova e changelog fechado" (main sempre; homolog só se a versão subiu), ambos no sha do candidato; o job `árvore` só pula a suíte com prova de árvore idêntica verde na develop. Nenhum workflow escreve na `main` nem publica release antes do merge do dono (`R-MAIN`); `release.yml` não muda. Pós-merge: tag `v0.47.2` e release pelo fluxo existente; versão e CHANGELOG já batem.

Ferramentas: `shellcheck .githooks/pre-push` rc=0; `forge-check docs` rc=0 (aviso de cache 0.47.1 sem prova do código). `actionlint` ausente do PATH (lacuna registrada; o CI o roda em versão fixa com checksum no passo "Baixa actionlint e zizmor"). `docker build` não se aplica. Nenhum teste rodado (ordem do dono de 16/11: só testes dos arquivos tocados; nenhum arquivo de código tocado).

## Custo e rollback
Sem minutos de CI novos nem recurso pago (`R-CUSTO`): nenhum workflow muda neste commit. Rollback: `git revert` do merge da release na develop e, se já na `main`, reimplantar a tag anterior (v0.47.1); manifestos e CHANGELOG são arquivos versionados, sem migração nem estado fora do repositório.
