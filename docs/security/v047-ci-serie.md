---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ci-serie
commit: 2a0bebc2e9924a9fc0335e0d476ed1b0d8b3aa75
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047 (série de CI, E1.85)

Head revisado: 2a0bebc2 (base b27f6985). Diff: `.github/workflows/ci.yml` (só comentários, 9 linhas), `tests/test_ci_local.py` (+58) e o fragmento de changelog. Sem PR aberto: rodei `python3 -m unittest tests.test_ci_local` (73 testes, OK); a suíte inteira fica para o CI do PR.

## Gatilhos
`R-SEGURANCA`: toca workflow e controle de permissões do CI.

## Achados
- A1 (recomendado) tests/test_ci_local.py:41 · `token_sem_permissao` trata `permissions: read-all` (escalar) como ausente e acusaria falso positivo; falha para o lado seguro, só ruído se alguém adotar essa forma.

## Sondas

## Detalhe dos achados
A1: evidência no `if ... not permissoes` (o parser só lê chaves de recuo 6). Hoje nenhum job usa a forma escalar, então não há efeito. Severidade informativa; correção mínima: aceitar valor escalar na seção; esforço P; dono tech-lead.

Julgamento dos três cartões:
- CI-GUARDA-PERMISSOES-ENV (muda comportamento do teste): fecha lacuna real. A regex antiga `\S+$` não via `GH_TOKEN: ${{ github.token }}` (valor com espaço); o teste novo prova isso e que o parser novo vê o env do job. Passa a acusar GH_TOKEN/GITHUB_TOKEN no job ou no passo sem `permissions:` próprio, e o job `pareceres` fica fixado em `contents: read` e sem env. Endurece o controle; sem afrouxamento. Aprovado.
- CI-ATALHO-COMMIT-SO-PARECER (só comentário): o gate segue lendo o check `bateria` do app github-actions, que falha fechado e reúne suíte e pareceres. O custo (uma rodada a mais no commit que traz o parecer) é de tempo, não de segurança; nenhum merge indevido. Motivo coerente; manter como está é correto. Aprovado.
- CI-PARECERES-SEM-NEEDS (só comentário): sem `needs`, o job roda em paralelo com `contents: read` e sem token. O pulo não abriria o merge porque o agregador reprova `skipped` em PR, como o comentário afirma. Manter é correto. Aprovado.

Os comentários novos não alteram o `run` do gate (o hash fixado no teste continua valendo; o teste passa).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas de workflow (actionlint, zizmor) não rodadas aqui; o CI do PR as cobre.
