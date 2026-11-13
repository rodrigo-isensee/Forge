---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ci-serie
commit: 2a0bebc2e9924a9fc0335e0d476ed1b0d8b3aa75
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (série de CI, E1.84)

Head revisado: 2a0bebc2 (base b27f6985). Diff: `.github/workflows/ci.yml` (+9, só comentário), `tests/test_ci_local.py` (+58/-1), fragmento de changelog. Classe C, bem abaixo do teto de 150 linhas, um comportamento só (o teste da guarda).

## Achados
- A1 (recomendado) tests/test_ci_local.py:30 · `permissoes_e_env_do_job` só lê `env:` com recuo 6 sob recuo 4; env com outro recuo ou em bloco inline (`env: {GH_TOKEN: x}`) escapa; hoje o ci.yml não usa essa forma.

## Sondas

## Parecer
Aprovado. Sem bloqueante.

- **CI-GUARDA-PERMISSOES-ENV (muda comportamento do teste):** a regex antiga (`\S+$`) não via `GH_TOKEN: ${{ github.token }}` por causa do espaço no valor. O teste novo prova isso de forma negativa (`antiga == [("contents","read")]` com env injetado) e exercita o leitor novo em quatro casos: env no job, token sem `permissions:`, token no passo sem `permissions:`, e `permissions:` declarada sem acusação. O ramo de falha tem teste de comportamento. Rodei `python3 -I tests/test_ci_local.py`: 73 testes, OK. Não há PR aberto, então não há CI para citar. O único guarda novo está no código de teste, não no de controle, e não pede mutante declarado.
- **CI-ATALHO-COMMIT-SO-PARECER (sem mudança, julgado):** manter o gate lendo o agregador `bateria` está certo. O custo é uma rodada de suíte a mais no commit que traz o parecer, e nunca um merge indevido, porque o agregador do commit novo ainda exige pareceres e suíte verdes. Ler os jobs da suíte exigiria confiar em `skipped` de commits só de parecer encadeados, que não se distinguem de um pulo por falha, e amarraria o gate aos nomes da matriz. O motivo está registrado no ci.yml e o teste fixa o filtro do agregador (`name == "bateria"` e `app.slug == "github-actions"`).
- **CI-PARECERES-SEM-NEEDS (sem mudança, julgado):** manter o job sem `needs` está certo. Com `needs: [bateria]`, um vermelho barato pularia o job e o autor só veria o parecer faltando na rodada seguinte. O job leva menos de um minuto e roda em paralelo. O pulo não abriria o merge, porque o agregador reprova `skipped` em PR. O teste já fixa `needs == []` e agora também o motivo escrito.

Os dois testes de "motivo registrado" leem o texto do ci.yml (`assertIn` do comentário). Isso é legítimo aqui, porque o entregável é o comentário e não há ramo de guarda. O teste do gate também confere o filtro do `run`, que é comportamento. Os commits são um por cartão, com mensagem em português e escopo, e o fragmento de changelog está em `changelog.d/`.
