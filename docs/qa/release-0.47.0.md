---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/release-0.47.0
commit: 72bb40084ec4b32d979dbbd8ba7379934aa5d055
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: marca da release 0.47.0 (v047, E2.12)

Head `72bb4008`. Delta desde o parecer anterior (`51c51139`, reprovado por A1): junção da `develop` (PR 540, teste-carga) com o fragmento na 0.47.0 e linha do placar regravada. Sem PR aberto para a branch: sem check-run `bateria`; rodei os testes afetados e os cenários abaixo.

## Achados
- A1 (bloqueante) docs/engineering/placar-mutacao.md:20 · RESOLVIDO: a linha agora traz `mortos=62 invalido=1 specs=9`, igual ao `--desde v0.46.0` reproduzido neste head, com nota do M10.
- A2 (recomendado) tests/mutantes/v0457-escopo-ponto-2.json:1 · M10 segue inválido (trecho ausente em bin/forge-check); a nota da 0.47.0 declara e adia a spec. Atualizar o trecho ou isentar a spec na próxima versão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão 0.47.0 nos dois manifestos | `grep '"version"'` nos dois `plugin.json`; `scripts/conferir-release.py --base origin/develop` | manifestos iguais e acima da base 0.46.0 | passou |
| CHANGELOG 0.47.0 com os 23 fragmentos (24 itens) | cada linha `- ` dos fragmentos removidos (`git diff --diff-filter=D origin/develop...HEAD -- changelog.d`) procurada em CHANGELOG.md: nenhuma ausente; seção com 24 itens; inclui a linha do v047-teste-carga | fragmento sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` | pasta só com README | passou |
| Testes do changelog e da release | `python3 -m unittest tests.test_changelog tests.test_conferir_release` (91, OK) | n/a | passou |
| Linha do placar confere com o método | `scripts/placar-mutacao.py --desde v0.46.0 --versao 0.47.0` | tag anterior certa; invalido declarado | passou (A1 resolvido) |
| Mutação e vermelho no diff | n/a: a marca não altera `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`; o PR 540 já tem parecer próprio (`docs/qa/v047-teste-carga.md`) | n/a | n/a |

## Provas
- `git rev-parse HEAD` = 72bb40084ec4b32d979dbbd8ba7379934aa5d055
- `placar: 0.47.0 mortos=62 sobreviveu=0 equivalente=0 invalido=1 sem-veredito=0 specs=9` (rc=0; spec v0457-escopo-ponto-2 rc=2 com invalido=1, as outras 8 rc=0)
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/develop`: versão base: 0.46.0 | versão da release: 0.47.0
- `unittest tests.test_changelog tests.test_conferir_release`: Ran 91 tests, OK
