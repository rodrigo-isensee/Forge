---
tipo: revisao-devops
contrato: 1
pedido: lote-ci1-lint
branch: melhoria/lote-ci1-lint
commit: b59891dd4b621fc6f5b0bdce44a192d1c5ed33a6
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-24
---
# Review de devops: lote-ci1-lint

## Parecer
Aprovado, sem bloqueante. O lote move, no job `bateria` de `.github/workflows/ci.yml`, os passos "Baixa actionlint e zizmor", `actionlint` e `zizmor` para antes de todo passo que executa código da branch (agora logo depois do `setup-node`, antes do Claude Code CLI). O diff é só reordenação (43 linhas, sem texto novo nos passos), mais um teste e o fragmento de changelog.

Conferido:
- Caminho pesado: ordem baixa, actionlint, zizmor, depois CLI, plugin validate, changelog, release, catraca, segredos, pareceres, provas, suíte, shellcheck, e2e. Nenhum binário entra no `GITHUB_PATH` depois de código da branch rodar; o único `>> "$GITHUB_PATH"` é o do passo de download.
- Caminho leve do gate (commit só de `docs/reviews|qa/` com a bateria verde antes): os passos de lint continuam com `pesada == 'true'` e não rodam; o passo leve roda só três classes de teste sobre docs, sem ferramenta baixada. Sem mudança de comportamento.
- Dependências na posição nova: o passo de download usa só `curl`, `sha256sum`, `tar`, `$RUNNER_TEMP` e `GITHUB_PATH`; o `actionlint` precisa do checkout (feito antes do gate) e usa o `shellcheck` do runner (`ubuntu-24.04`), independente da posição; o `zizmor` roda `--offline`. O gate (`git`, `gh`) é inline e não executa código da branch. Nenhum passo depende de algo que ainda não exista.
- Download com checksum: versões e SHA-256 nas variáveis `env` do job, `sha256sum -c` antes do `tar`, extração só do binário nomeado. Não há cache (nada a envenenar, nada de franquia de cache).
- Tempo: o mesmo conjunto de passos, só em outra ordem; o custo do job não muda e a falha de lint passa a aparecer antes dos passos caros (CLI via npm, suíte). Os passos seguintes usam `!cancelled()` e continuam rodando depois de uma falha de lint, o que mantém o feedback completo e é seguro porque o PATH nunca foi alterado por código da branch.
- `permissions`, `timeout-minutes`, `concurrency` e ações fixadas por SHA: sem mudança. `R-CUSTO`, `R-MAIN` e `R-VERIFY`: nada novo (sem `continue-on-error`, sem runner pago, sem escrita na `main`).
- Teste: `python3 -m unittest tests.test_ci_local` no head b59891d: 52 testes, OK. O YAML carrega.

Ferramentas: `shellcheck` presente no PATH. `actionlint` e `zizmor` ausentes no ambiente (lacuna registrada: a ordem foi conferida pela leitura do YAML e pelo teste, e os dois lints rodam no CI).

## Achados
- A1 (recomendado) tests/test_ci_local.py:178 · a lista `executam_codigo` é fechada por nome; passo novo que execute código da branch e não esteja na lista pode ficar antes do lint sem o teste notar (igual ao A1 do review e ao R1 da segurança; cartão CI-LINT-LISTA-ABERTA); não devolve.
- A2 (recomendado) .github/workflows/ci.yml:135 · os dois `curl` não têm `--retry`; o passo está agora antes de tudo e uma falha de rede do GitHub derruba a bateria inteira, ao contrário do passo do Claude Code CLI, que tenta de novo; sugestão `curl --retry 3 --retry-all-errors`. Já era assim antes do lote; não devolve.

## Custo e rollback
Sem recurso novo nem minuto novo de CI (`R-CUSTO`): só reordenação de passos no mesmo job. Rollback: reverter o commit b59891d (devolve os três passos à posição anterior); nenhuma migração nem estado envolvido.
