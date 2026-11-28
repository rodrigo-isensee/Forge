---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v0481-ambiente-claude-path
commit: 75f2e456414d0cb3e8e6e32c3afd1752798db61d
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: ambiente (DEVCONTAINER-CLAUDE-NO-PATH, E13.5, classe C), delta df4b2bf9..75f2e456

Delta de código: uma linha, `# shellcheck disable=SC2016` acima de scripts/preparar-estacao.sh:197, sem mudança de comportamento. Conteúdo aprovado; a reprovação é só pelo CI do head (R-QA, PARECER-LE-O-CI).

## Achados
- A1 (bloqueante) .github/workflows:0 · CI do 75f2e456 sem verde: `bateria (passos)` falha por caminho pessoal no parecer de segurança (docs/security/v0481-ambiente-claude-path.md:28, fora do código); `bateria` e `bateria (pareceres)` vermelhas. Regravar a linha ci: no head novo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: SC2016 do shellcheck na linha 197 | `shellcheck scripts/preparar-estacao.sh` | linha de regex com `\$HOME` literal | passou (sem saída, rc 0) |
| Comportamento da linha 197 inalterado | `python3 -m unittest tests.test_ambiente_recriacao tests.test_guia_varios_projetos` | linha no fim, já na frente, `$HOME`/`${HOME}`/`/root` | passou (22 testes, OK) |

## Cenários e resultado real
- Mutantes: `bin/forge-mutante tests/mutantes/v0481-ambiente-claude-path.json` · M1 a M8 `morreu` (devcontainer.json:32 x4, preparar-estacao.sh:198 x2, :488, README.md:47); rc 0. O delta é só comentário: nenhum mutante novo.
- Vermelho: do delta nada a provar (comentário); o vermelho da rodada anterior segue valendo (base a19718532c83).

## CI
- ci: NÃO verde no 75f2e456414d0cb3e8e6e32c3afd1752798db61d (`gh pr checks`: `bateria`, `bateria (pareceres)` e `bateria (passos)` falham; run 46166972749). Não gravo `ci: verde`.
