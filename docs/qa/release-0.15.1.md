---
tipo: qa
contrato: 1
pedido: pos-release-0.15.0
branch: melhoria/release-0.15.1
commit: d69feef
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA - versão 0.15.1 (pós-release 0.15.0)

Sem UX nem API. Código testado: d155d29 (versão, CHANGELOG, fragmento removido) sobre bad3edd; o HEAD d69feef só acrescenta o parecer de review. Arquivo de comandos do dono (fora do repositório): `~/.forge-contrib/docs/briefs/pos-release-0.15.0-comandos.md`, versão após a volta 1.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1a | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 653 testes, OK |
| PQ-1b | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-1c | Instalação ponta a ponta | `bash tests/e2e-instalacao.sh` | n/a | ok (8 agentes, 9 skills) |
| PQ-1d | CI do PR de release: versão = última seção; sem fragmentos | `forge-changelog conferir-release`; plugin.json = 0.15.1, primeira seção datada do CHANGELOG = `[0.15.1]`, `[Não publicado]` vazia; `changelog.d/` inexistente | pasta ausente tratada sem erro | rc=0 |
| PQ-2 | Notas extraídas (awk do release.yml, cópia em $TMPDIR) | 0.14.0: 10 linhas; 0.15.0: 13 linhas, contém a entrada `scripts/ci-local` (#145) nas linhas 2 e 12; 0.15.1: 3 linhas | nenhuma saída vazia | ok |
| PQ-3 | Arquivo de comandos (escopo 2) | grep abaixo | SHA completo; sem `--force` | ok |
| PQ-4 | Limpeza local (escopo 3) | `git worktree list`, `git branch -a`, `git log -1` | ~/Forge = origin/develop | ok |

## Escopo 2: arquivo de comandos
- Merges: passo 1 `--squash` (develop), passo 2 `--merge` (homolog), passo 3 `--squash` (main, merge do dono), passo 7 `--merge` (sincronização main para develop). Confere com R-FLUXO "Métodos de merge".
- SHAs completos de 40 caracteres: `4d6087db...e8` (`plugin.json` 0.14.0, "Merge pull request #134") e `408c2ebb...78` (0.15.0, #150). Ambos existem como commit; o primeiro commit na main de cada versão (`git log origin/main --first-parent -- .claude-plugin/plugin.json` mostra 408c2eb, 4d6087d, a093c8f).
- Notas: o mesmo awk do release.yml, sobre `origin/main:CHANGELOG.md`; guarda `test -s`, guarda de tag existente e guarda de versão para a 0.15.1 (achados do review incorporados).
- Remoção de remotas: `git push origin --delete melhoria/release-0.15.0 melhoria/ci-local-jobs-consolidados` e, após o merge, `melhoria/release-0.15.1`. `--force`: 0 ocorrências; `--no-verify`: 0.
- Observação (não é bug): as notas da 0.15.0 só saem com a entrada do #145 depois do merge do passo 3, porque a fonte é `origin/main`; o arquivo avisa isso e a ordem dos passos garante.

## Escopo 3: limpeza local
- `git worktree list`: só ~/Forge (develop) e wt/release-0.15.1 (a branch desta entrega, remoção prevista no passo 5).
- `git branch`: develop, main, melhoria/release-0.15.1 e `backup/estado-ciclo-2026-10` (anterior ao pedido, fora das duas branches mescladas; o dono decide se apaga).
- `git -C ~/Forge log -1` = `bad3edd`, igual a `origin/develop` (bad3edd57380...).
- Resíduo em `.git/worktrees/` (autoria, ci-local-jobs-consolidados, release-0.15.0, ubuntu26) que o sandbox não remove: já vai como comando ao dono no passo 6 (`git worktree prune`). Não é bug.

## Lacunas
O sandbox nega `api.anthropic.com` e `datadoghq.com`; validação e e2e passaram mesmo assim. O `claude plugin validate . --strict` do CI não foi rodado literalmente; `scripts/validar-plugin.sh` o substitui. Os comandos `gh` e `git push` do arquivo não foram executados (sem credencial, fora do escopo); conferidos por leitura e pelos fatos do repositório.

## Resultado
APROVADO. Zero bugs abertos.
