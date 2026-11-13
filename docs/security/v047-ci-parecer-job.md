---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ci-parecer-job
commit: bd28180e9129015578029dee765abd206960bac1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v047-ci-parecer-job

Pedido v047, etapa E1.21: revalidação por delta do parecer de segurança da E1.4 (job `bateria (pareceres)` no `ci.yml`) depois da volta E1.18, no head `bd28180e`. Parecer anterior: E1.12, reprovado no head `7ba85a05` (A1 a A3 bloqueantes, A4 e A5 recomendados). Controles J1 a J11 do modelo `docs/security/v047-e1-ameacas.md` (E1.5).

Delta lido (`forge-check parecer delta`, `7ba85a05..bd28180e`): no domínio, `.github/workflows/ci.yml` (só `timeout-minutes` 10 → 5 em :552), `agents/devops-engineer.md`:12, `stacks/node-react/pronto.md`:55, `stacks/python/pronto.md`:30 e `tests/test_catraca.py`:3321-3322; fora do domínio, mas lidos por serem a prova da guarda, `tests/test_ci_local.py`, `tests/test_suite_partes.py`:300 e `tests/mutantes/v047-ci-parecer-job.json`. O `run:` do agregador (:674) e o resto do job `pareceres` (:545-579) não mudaram.

## Gatilhos
`R-SEGURANCA`: mudança em `.github/workflows/` (portão de pareceres no servidor, check exigido `bateria`) e em texto de agente que ensina o pipeline aos projetos (`agents/devops-engineer.md`, `pronto.md` das stacks).

## Achados
- A1 (recomendado) tests/test_ci_local.py:317 · W7/J5: a guarda das permissões do job `pareceres` não vê `env:` de job; `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` posto no job sobrevive aos testes (sonda R1). Token só leitura e script da base: sem caminho de ataque hoje; conferir que o bloco antes de `steps:` não cita `secrets.`.

## Sondas

## Detalhe dos achados

### Situação dos achados da E1.12 no head bd28180e
| Achado | Situação | Prova |
|---|---|---|
| A1 (bloqueante) fiação do agregador sem `pareceres` | resolvido | `tests/test_suite_partes.py`:300 com `pareceres` no conjunto; `FiacaoDoCI` verde no head |
| A2 (bloqueante) condição do agregador sem teste | resolvido | `tests/test_ci_local.py`:320-347 executa o `run:` real do agregador (bash `-eo pipefail`) na tabela de J2/W3-W5; mutantes M1 a M4 mortos; S2 e S3 da E1.12 agora falham os testes |
| A3 (bloqueante) J11 sem "pulado ou cancelado em PR reprova" | resolvido | `agents/devops-engineer.md`:12, `stacks/node-react/pronto.md`:55, `stacks/python/pronto.md`:30 trazem as três condições (no agregador, entra no check exigido; só `success` em PR, `skipped` só fora de PR, sem `!contains(failure)`; fora do `needs` da suíte) |
| A4 (recomendado) exatamente um job, permissões | resolvido | `tests/test_ci_local.py`:314-318: `--modo pareceres` em exatamente um passo, permissões só `contents: read`; S4 da E1.12 agora falha os testes |
| A5 (recomendado) teto de 5 min (J9) | resolvido | ci.yml:552 `timeout-minutes: 5`; `tests/test_catraca.py`:3322 e mutante M6 morto |

Além disso: o `if:` do job (só `pull_request`) e a ausência de `needs` ficaram presos por teste (`test_job_pareceres_so_roda_em_pr_e_sem_needs`, mutante M5 morto; pôr `needs: [bateria]` no job falha os testes, sonda R2). `persist-credentials: true` no job também falha os testes (sonda R3).

### Controles J1 a J11 no head bd28180e
J1, J4, J6, J7, J8 e J10 sem mudança desde a E1.12 (ok). J2 e J3 agora com teste de comportamento e mutantes. J5 ok no código (só `contents: read`, sem `GH_TOKEN` nem `secrets`, `persist-credentials: false`), com a lacuna de teste do A1 acima. J9 ok (5 min). J11 ok nos três textos.

### A1 (recomendado)
Evidência: `tests/test_ci_local.py`:317 lê só as linhas de 6 espaços com valor sem espaço antes de `steps:`; um `env:` de job com `${{ secrets.GITHUB_TOKEN }}` não casa e passa. Caminho de ataque: nenhum realista hoje; o job tem só `contents: read`, roda o script da base (J4) e o modo `pareceres` não chama a API. Uma edição futura que exponha o token ao passo daria leitura do repositório a um script que já o lê pelo checkout. Severidade: informativa. Correção mínima: acrescentar ao teste que o bloco do job `pareceres` não contém `secrets.` nem `GH_TOKEN`. Esforço P. Dono: `devops-engineer`.

### Sondas desta revalidação (não provam bloqueante; ficam aqui)
- R1 · job `pareceres` com `env:` `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` antes de `steps:`, depois `unittest tests.test_ci_local tests.test_catraca.Workflows tests.test_suite_partes.FiacaoDoCI` · espera: FAILED · obtido: OK
- R2 · job `pareceres` com `needs: [bateria]`, os mesmos testes · espera: FAILED · obtido: FAILED (2)
- R3 · `persist-credentials: true` no job `pareceres`, os mesmos testes · espera: FAILED · obtido: FAILED (1)
- S2, S3 e S4 da E1.12 repetidas no head bd28180e · espera: FAILED · obtido: FAILED (1, 6 e 1 falhas)

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`; leitura do delta; `forge-mutante tests/mutantes/v047-ci-parecer-job.json` no head bd28180e (M1 a M6 mortos; o `--cobertura` não analisa yml); sondas de mutação no `ci.yml` (revertidas); testes afetados `tests.test_ci_local`, `tests.test_catraca.Workflows`, `tests.test_suite_partes.FiacaoDoCI` (82 testes, OK). Sem PR aberto, sem CI a citar: suíte inteira não rodada aqui (fica para o CI do PR). Lacunas: o linter de workflow e o auditor de ações não estão no PATH desta máquina; rodam no job de passos do CI.
