---
tipo: qa
contrato: 1
pedido: release-0.28.0
branch: melhoria/release-0.28.0
commit: 450d7fa27e133cddbafd9ce09f19f63548f86a31
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: release-0.28.0

Código testado: 450d7fa (HEAD remoto 00dfd97 difere só pelos pareceres de devops, segurança e review; `git diff 450d7fa HEAD --stat` toca só docs/reviews, docs/security e docs/devops). Sem especificação de UX: a release agrega 18 PRs (#257 a #274), cada um com QA próprio aprovado; aqui vale o critério de integração (R-QA).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte inteira verde (R-VERIFY) | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q` na worktree: 1338 testes, 304 s | n/a | passou (OK, rc 0) |
| Plugin válido | `scripts/validar-plugin.sh` | n/a | passou (Validation passed; sondas de rede negadas pelo sandbox, sem efeito) |
| Versão nas duas cópias | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em cópia `git archive` de 00dfd97 | n/a | 0.28.0 nas duas |
| CHANGELOG cobre os 18 PRs | cada linha `- ` dos 18 fragmentos de `changelog.d/` em 8b047d4 achada literal na entrada [0.28.0] (`grep -qxF`); entrada tem 20 linhas | nenhum PR de fora | passou (0 faltas) |
| Instalação limpa | `bin/forge-init` da cópia em projeto novo em $TMPDIR | projeto vazio | 21 arquivos criados, hook ativado |
| doutor | `bin/forge-doutor` no projeto novo | projeto sem develop/homolog | roda, rc 1 com 3 avisos esperados (sandbox, branches) |
| forge-check fila | `bin/forge-check fila` | fila vazia | "0 podem começar, 16 vagas de 16", rc 0 |
| forge-fechar --dry-run | `forge-fechar release-0.28.0 --ref melhoria/release-0.28.0 --dry-run` | sem rede, sem gh | imprime os 7 passos, "log:" na 1ª linha, "fim: código 0" |
| pre-push dirigido | `bash -n` e `--status` do hook da cópia; caminho curto coberto por `test_pre_push_parecer` na suíte | falha fechada | sintaxe ok, status "nenhuma suíte rodando"; testes verdes |
| forge-testes dirigido | `forge-testes --listar` | sem base legível | cai na suíte completa (falha fechada, como documentado) |

## Cenários e resultado real
- Vermelho antes do verde e mutação: não se aplicam aqui; a release não traz teste novo próprio, os dos PRs foram vistos nos pareceres de QA de cada um.
- O pre-push real (fila e flock) não foi disparado numa cópia para não duplicar a suíte (R-TETO); o envio deste parecer o exercita.
- Sem rede: nada de CI nem `gh` consultado. Sondas só em $TMPDIR.
- Recomendação baixa de segurança (cmd_fila imprime campos sem `caminho_impresso`) segue como cartão, não bloqueia.
