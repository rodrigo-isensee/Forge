---
tipo: revisao-devops
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: e8368a4cdd98951a1a3b96d18eb539e648d299ca
parecer: reprovado
revisor: forge:devops-engineer
data: 2026-11-26
---
# Review de devops: v0481-f6-ci-uma-vez (#929, F6)

## Achados
- A1 (bloqueante) .github/workflows/ci.yml:360 · o `name:` do passo "Fumaça no Python 3.14 (F6: a suíte ..." é escalar simples com `: ` dentro; o YAML fica inválido. O GitHub não criou o CI do PR e o run do push (45924102244) falhou por "workflow file issue". Aspas no nome, ou trocar `F6:` por `F6,`.
- A2 (bloqueante) .github/workflows/ci.yml:360 · sem o A1 resolvido não existem os checks `bateria` e `bateria (python 3.14)` no head (só `catraca`), que o ruleset exige; a duração (meta < 8 min) e o e2e no CI ficam sem medida. Nova rodada depois do conserto.
- A3 (recomendado) .github/workflows/ci.yml:1 · `actionlint` não está instalado nesta estação e teria pego o A1 antes do envio; instalar pelo `scripts/preparar-estacao.sh` e rodar `actionlint` e `zizmor` antes de enviar workflow.
- A4 (recomendado) .github/workflows/diario.yml:1 · o `schedule` só vale com o arquivo na `main`; até a release o diário só roda por `workflow_dispatch`. Registrar no cartão da release e medir os minutos da primeira execução (5 partes 3.14, e2e, mutantes) contra a franquia.

## Detalhes
Reprovado por defeito provado. PR #929, head e8368a4c, base ee05ee84, +520/-288 em 10 arquivos.

Defeito: o pipeline não roda. `gh pr checks 929` lista só `catraca` (pass); o `gh run list` do head mostra o run de push de `ci.yml` com conclusão failure, sem jobs (`actions/runs/45924102244/jobs` com `total_count: 0`). Com o parser YAML de Perl (`CPAN::Meta::YAML`) o `diario.yml` lê limpo e o `ci.yml` recusa o escalar do passo da linha 360. Os demais `name:` com `: ` estão entre aspas ou só em comentário (varredura por grep). Não achei outro problema estrutural: todo `needs.X` usado está no `needs` do job, sem ciclo, sem chave duplicada.

Conferido sem defeito:
- Nomes dos checks exigidos: o ruleset da `develop` (`rules/branches/develop`) exige `bateria`, `bateria (python 3.14)` e `catraca`; os `name:` dos jobs `agregador`, `bateria-python-tres-quatorze` e da catraca seguem iguais, e `docs/protecao-de-branch.md` registra a mudança de comportamento do agregador 3.14 (agora só instalação e fumaça). O agregador usa `always()` e exige `success`: pulado ou cancelado reprova.
- `diario.yml`: `permissions: contents: read` no topo; `issues: write` só no job `cartao`; ações fixadas por SHA com a tag em comentário; `persist-credentials: false`; `timeout-minutes` em todos; `concurrency` sem cancelar; entrada do cartão passa por `env`, não por `run:`; não é check exigido nem entra em agregador, então não bloqueia merge. Sem escrita na `main` (`R-MAIN`); sem serviço pago (`R-CUSTO`).
- `arvore-envio`: token só no passo da prova, permissões de leitura (`actions`, `checks`, `pull-requests`), falha fechada para suíte inteira.
- Plano de corte: o tamanho cabe num PR só porque `ci.yml`, `diario.yml`, o script e os testes são uma mudança só (mover passo do PR para o diário); não vejo ponto de corte que preserve o portão. `ci.yml` é arquivo protegido e tira do portão do PR a suíte no 3.14 e o e2e no 3.12: o `tech-lead` confere o rótulo `afrouxa-regra` do dono (ADR 0003).

Não medi o tempo do CI do PR: não há run de `ci.yml` no head. Não rodei a suíte (G3); só li o CI e os arquivos.

Provas: `gh pr checks 929` (PQ-3) traz apenas `catraca`; o CI do head não está verde, por isso não há linha `ci:` de verde.

## Custo e rollback
Sem custo novo de dinheiro. Rollback: reverter o merge do PR na `develop`; o `diario.yml` some junto e nenhum estado fica fora do repositório.
