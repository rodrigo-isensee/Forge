---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.46.0
branch: melhoria/release-0.46.0
commit: 2e45133689fbddb381d134637cc1e5c6569e8b75
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: release-0.46.0 (pedido v0457, E23.85)

Escopo: a release 0.46.0 é a `develop` em 2e451336 contra a `main` em 4099658f (`git log origin/main..origin/develop`: 327 commits; `git diff --stat`: 485 arquivos, +23937/-1873), lida numa worktree destacada própria da `origin/develop`. Este parecer é o exigido por `scripts/promover-homolog.py` para a promoção.

## Gatilhos
`R-SEGURANCA`: a leva muda workflow de CI (`.github/workflows/ci.yml`), hooks e o manifesto do plugin que todos os projetos instalam. Cada item já passou pelo seu parecer; este review cobre o workflow (o único arquivo de `.github/` mudado) e confere os pareceres dos itens.

## Achados

## Sondas

## Detalhe dos achados
Sem achados novos. O que foi conferido:

- **Workflow** (`git diff origin/main..origin/develop -- .github/`: só `.github/workflows/ci.yml`, +66/-24; commits 0ec636d1 e 00e6d430 do A18, 34802d5e do CI-TEMPO-314):
  - Permissões: o job novo `verificacoes` (`.github/workflows/ci.yml:562`) declara só `contents: read` (`:571-572`); o job `bateria` mantém `contents: read` e `checks: read` e ganha só a saída `pesada` (`outputs`), um valor do gate, sem dado de segredo. As partes (`:187`, `:252`) seguem com `contents: read`. Nenhuma permissão de escrita nova.
  - Segredos: nenhuma referência a `secrets.` nem a token nas linhas acrescentadas. O passo "Nada pula degrau", só movido para antes do CLI, continua lendo `github.head_ref` por `env:` (`HEAD_REF`), sem interpolação no `run:`; o passo das Provas segue lendo o sha por `env:`.
  - Ações de terceiros: o job novo usa `actions/checkout`, `actions/setup-python` e `actions/setup-node` fixadas pelos mesmos SHAs de 40 caracteres já usados no arquivo; nenhuma ação nova. O checkout do job novo leva `persist-credentials: false`.
  - Gatilhos: nenhum `pull_request_target` nem `workflow_run` nos workflows.
  - Ordem do CLI (CI-ORDEM-LINT): no job novo, o CLI do Claude Code é instalado antes de qualquer código da branch (Provas, shellcheck, e2e), como no job de passos.
  - Agregador: `needs: [bateria, verificacoes, partes-doze, pulados-doze]` (`:639`) com `always()` e exigência de `success` em cada um; job pulado ou falho reprova o check exigido, então o encadeamento novo (`needs: [arvore, bateria]` nas partes) não abre caminho de verde sem rodar. O gate no job novo usa `!= 'false'`, que erra para o lado de rodar mais, não menos.
  - `timeout-minutes` 20 para 30 nas provas da develop (`:37`, `:79`): só tempo, sem efeito de segurança.
- **Pareceres dos itens da leva:** os 19 pareceres acrescentados em `docs/security/` entre main e develop (fora `ameacas/`, `aceites/` e modelos) estão todos com `parecer: aprovado`: backlog-ate-sexta, ci-tempo-314, conformidade-curinga, release-0460, suite-tempo-vivo, v0456, v0457, v0457-juncao, v0457-refs-push, v046, v046-ci-lote-e1 (cobre o A18 no 00e6d430), v046-conformidade-caminho-git, v046-develop-verde-494, v046-entrega-push-proxy, v046-envio-leve-ajustes, v046-forge-pesado-m12, v046-pesado-b4, v046-seguranca-sem-rerrodar, v046-testes-seguros. Nenhum `reprovado` nem `riscos-aceitos`.
- **Segredo e `.env`:** busca de padrões de token e chave privada nas linhas acrescentadas do diff main..develop: zero ocorrências; nenhum arquivo `.env` no diff.
- **Achados abertos em cartão:** A14, A15, CONFORMIDADE-MV-PASTA-CURINGA, A12, A13 e A4 a A10 já existiam na `main` e seguem nos seus cartões; não bloqueiam a release e não são reabertos aqui.
- **PA-7** (`docs/engineering/achados-recorrentes.md`): AR-1 a AR-13 tratam de mutantes, testes, hooks e leitura de comando; o único arquivo revisado aqui por conta própria é o workflow, onde nenhum se aplica (AR-3 e AR-5 não têm instância nas linhas novas: nenhuma trava de ambiente nem `python` em caminho que decide foi acrescentado).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, grep de padrões de segredo, leitura do workflow. Faltaram no ambiente: gitleaks, osv-scanner, semgrep, zizmor e actionlint (lacuna; o zizmor e o actionlint do CI do PR de promoção seguem como portão).
