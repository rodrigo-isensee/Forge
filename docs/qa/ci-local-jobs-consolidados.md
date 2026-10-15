---
tipo: qa
contrato: 1
pedido: develop-vermelha-ci-local
branch: melhoria/ci-local-jobs-consolidados
commit: 5d623443be6f7acab6a401fbfecaa988b428341c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA - ci-local acompanha os jobs consolidados (rapida, bateria)

Links: pedido `~/.forge-contrib/docs/pedidos/develop-vermelha-ci-local.md`; review `docs/reviews/ci-local-jobs-consolidados.md`; devops `docs/devops/ci-local-jobs-consolidados.md`. Sem UX nem API. Código testado em 5d62344; os pareceres vieram depois.

## Critério -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | `rapida`, `bateria`, `catraca` lidos; pulos só de actionlint/zizmor | leitura real dos workflows com as funções do `scripts/ci-local` (abaixo) | passo opcional x obrigatório | Passou, com a lacuna do modo local (abaixo) |
| PQ-2 | suíte verde | `env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests` (uptime 0.40 antes) | n/a | Passou: 653 testes, OK |
| PQ-3 | plugin e changelog | `scripts/validar-plugin.sh`; `forge-changelog conferir --base origin/develop` | fragmento exigido | Passou: "Validation passed"; rc=0 |
| VV | teste novo falha sem a correção | `scripts/ci-local` de origin/develop sobre os testes novos | script antigo | Vermelho: 2 falhas (`test_actionlint_ausente_pula_so_o_passo...`, `test_nenhum_job_e_opcional...`); com a correção, 49 OK |
| MUT | mutante no diff | troquei `ausentes and ausentes <= FERRAMENTAS_OPCIONAIS` por `ausentes` | só opcionais podem ser pulados | Morto: 2 falhas (`test_ferramenta_ausente_pula_como_ausencia`, `test_ferramenta_obrigatoria_ausente_continua_reprovando...`); script restaurado |

## PQ-1, cenário real e lacuna
- `scripts/ci-local` exige o número de um PR e usa `gh` (rede e credencial): não há modo local sem PR, e o sandbox não tem `gh` nem rede. Lacuna registrada: a execução completa não foi feita; a validação foi pela leitura real dos workflows e pelos testes.
- Leitura real (`ler_jobs` sobre `.github/workflows/ci.yml` e `catraca.yml` da branch): `rapida` 3 passos, `bateria` 18, `catraca` 3; todos obrigatórios (`NAO_OBRIGATORIOS` vazio).
- Sem actionlint e zizmor no PATH: `bateria` 18 -> 15 passos; avisos de pulo só para 3 passos (o de baixar as ferramentas, `actionlint` e `zizmor`). `rapida` e `catraca` ficam intactos.
- Observação, sem defeito: neste sandbox o `shellcheck` também está ausente, então um `ci-local` completo marcaria a `bateria` como pulada por ferramenta ausente e obrigatória (`failure`), que é o comportamento desenhado e testado (`test_ferramenta_obrigatoria_ausente_continua_reprovando...`). Numa máquina com shellcheck, a bateria roda.

## Bugs
Nenhum aberto.
