---
tipo: qa
contrato: 1
pedido: release-0.47.0
branch: melhoria/release-0.47.0-b
commit: 0867f7157f37ca5ea76ef31824cbb159c215086f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: marca refeita da release 0.47.0 (v047, E2.23)

Head `0867f715`, base `12196ade` (develop com os PRs 541, 544, 542 e 543). Julguei a entrada da 0.47.0 e, contra a `main` (0.46.0), o domínio do QA. Sem PR aberto: sem check-run `bateria`; rodei os testes afetados e os cenários abaixo (carga ~14 a 18 em 12 CPUs).

## Achados
- A1 (recomendado) tests/mutantes/v0457-escopo-ponto-2.json:1 · herdado do parecer anterior: M10 segue inválido (guarda movida pelo PR 536); a nota da 0.47.0 no placar declara e adia a spec. Atualizar o trecho ou isentar a spec na próxima versão.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Os 4 fragmentos (PRs 541, 544, 542, 543) estão na entrada 0.47.0 | cada linha `- ` dos 4 fragmentos (`git show <pr> -- changelog.d`) procurada em CHANGELOG.md com `grep -F`: 4 de 4 presentes, cada uma na seção do fragmento (3 em Alterado, 1 em Corrigido) | fragmento sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` | pasta só com README | passou |
| Versão segue 0.47.0 e sobe contra a main | `scripts/conferir-release.py --base origin/main` (base 0.46.0, release 0.47.0); `plugin.json` = 0.47.0 | versão acima da main | passou |
| Entrada 0.47.0 íntegra | 28 itens na seção 0.47.0 (24 anteriores + 4); sem duplicata dos 4 | item duplicado ou perdido | passou |
| Testes do changelog e da release | `python3 -m unittest tests.test_changelog tests.test_conferir_release` | n/a | passou (91, OK) |
| Pareceres e docs no formato | `bin/forge-check docs` | formato do parecer | passou (rc=0) |
| Placar da 0.47.0 segue válido | os 4 PRs não tocam `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` (`git diff --name-only d8b633e0 HEAD`: 0); a spec nova `v047-caminho-runner` ordena depois das 8 já na amostra (teto 8 do `scripts/placar-mutacao.py`), logo sai `fora da amostra` e a linha `mortos=62 invalido=1 specs=9` não muda | amostra com teto | passou (por leitura do método; a re-execução completa foi interrompida pela carga e não é prova) |
| Mutação e vermelho no diff | n/a: a marca não altera código de controle; cada PR tem parecer próprio (`docs/qa/v047-ci-serie.md`, `v047-caminho-runner.md`, `v047-jarvis-parte2.md`, `mp1311-worktree-jarvis.md`) | n/a | n/a |

## Provas
- `git rev-parse HEAD` = 0867f7157f37ca5ea76ef31824cbb159c215086f
- `bin/forge-check docs`: rc=0
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/main`: versão base: 0.46.0 | versão da release: 0.47.0
- `unittest tests.test_changelog tests.test_conferir_release`: Ran 91 tests, OK
