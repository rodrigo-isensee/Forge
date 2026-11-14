---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-ci-serie
commit: 2a0bebc2e9924a9fc0335e0d476ed1b0d8b3aa75
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-13
---
# Review de devops: v047 (série de CI, E1.87)

## Achados
- A1 (recomendado) tests/test_ci_local.py:30 · `permissoes_e_env_do_job` só lê `env:` com recuo 6 sob recuo 4; `env: {GH_TOKEN: x}` inline ou outro recuo escapa da guarda. O ci.yml de hoje não usa essa forma; endurecer se ela aparecer.

## Detalhes
Aprovado no head 2a0bebc2 (base b27f6985), instância que não fez a entrega. O diff em `.github/workflows/ci.yml` é só comentário (+9, conferido: nenhuma linha não comentada muda), então não há mudança de comportamento do pipeline: `permissions:` do topo segue `contents: read`, nenhum gatilho, `needs`, `if:` ou `run:` mudou.

- Guarda de permissões e env (tests/test_ci_local.py): o leitor novo vê `GH_TOKEN: ${{ github.token }}` no env do job, que a regex antiga (`\S+$`) não via por causa do espaço no valor. O job `pareceres` continua com só `contents: read` e sem `env:`. Rodei `python3 -I tests/test_ci_local.py`: 73 testes, OK.
- Atalho do commit só de parecer (ci.yml:432): manter o gate no agregador `bateria` é correto. O custo é uma rodada de suíte a mais no commit que traz o parecer (minutos, dentro da franquia), nunca merge indevido: o agregador do commit novo ainda exige pareceres e suíte verdes (ci.yml:685). O filtro `name == "bateria" and .app.slug == "github-actions"` e o hash do `run` do gate estão fixados no teste.
- Job `pareceres` sem `needs` (ci.yml:557): correto. Com `needs: [bateria]` um vermelho barato o pularia e o autor só veria o parecer faltando na rodada seguinte; o job leva menos de um minuto e roda em paralelo. O pulo não abriria o merge (o agregador reprova `skipped` em PR, ci.yml:684-685). O teste fixa `if` de PR e `needs == []`.
- Checklist de workflow: sem `pull_request_target`, sem segredo novo, sem `continue-on-error`, sem `[skip ci]`, nada escreve na `main` (R-MAIN, R-VERIFY ok). Nenhuma proteção de branch ou check exigido alterado (R-CONFORMIDADE).
- Ferramentas: `shellcheck` presente no PATH, sem script de shell novo; `actionlint` e `zizmor` ausentes, lacuna registrada (a mudança é só comentário, risco de sintaxe nulo; o CI do PR roda os dois). Não há PR aberto, então não há CI para citar. Máquina com carga ~13 em 12 CPUs: só o teste afetado rodou.
- Aviso: arquivo protegido de `.github/` muda, então o PR pede o rótulo `afrouxa-regra` do dono se a catraca o exigir (aqui só comentário; o tech-lead decide). O token do bot não tem escopo `workflow`: o envio de `ci.yml` pode precisar do dono.

## Custo e rollback
Sem custo novo (R-CUSTO): nenhum job, runner ou artefato adicionado; só comentário e teste local. Rollback: `git revert` dos commits da série; nada a migrar.
