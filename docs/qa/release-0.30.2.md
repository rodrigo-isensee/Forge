---
tipo: qa
contrato: 1
pedido: release-0.30.2
branch: melhoria/release-0.30.2
commit: ce8e54c56025a899819aa26c5b7ff4e841442acf
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: release-0.30.2

Base `82cd515bc6a1943e2fa62bdbd5d1c520f69453fa` (`origin/develop`, #315), head `ce8e54c56025a899819aa26c5b7ff4e841442acf` (`chore(release): versão 0.30.2 (#315)`). Diff de 4 arquivos: `CHANGELOG.md` (+4: seção `## [0.30.2] - 2026-10-24` com o `### Alterado` do MAQ-LOTE-A), `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` (0.30.1 para 0.30.2) e o fragmento `changelog.d/maq-lote-a.md` apagado. Sem código de produção, sem `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` no diff, então não há mutantes a declarar e teste novo de regra não se aplica (vermelho antes do verde não se aplica). Sem especificação de UX nem `CA-n`; as obrigações vêm do pedido REL-0302 (E1) e da decisão "C" do dono (versão 0.30.2, exceção ao SemVer).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `forge-changelog release 0.30.2 2026-10-24` sobre a base reproduz o CHANGELOG do commit | reprodução ponta a ponta em cópia (`git archive 82cd515` em `$TMPDIR`), `bin/forge-changelog release` da worktree e `diff` com o `CHANGELOG.md` do commit; e árvore inteira comparada com `diff -r` | o único fragmento da base (`maq-lote-a.md`) entra e some; nenhuma linha antiga de `[Não publicado]` sobra | passou (`CHANGELOG.md` idêntico; `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` idênticos; `diff -r` só difere por `changelog.d/` vazia, que o git não versiona) |
| E1: versão 0.30.2 nos dois manifestos, iguais entre si e ao CHANGELOG | leitura dos dois `plugin.json` no commit e `grep -rn "0\.30\.1"` fora de `docs/` (o `.git` fica de fora) | os dois manifestos iguais; a única ocorrência de 0.30.1 fora de `docs/` é a seção histórica `## [0.30.1]` do CHANGELOG | passou |
| E1: fragmento removido, sem sobra em `changelog.d/` | `bin/forge-changelog conferir-release` (gate da main) | fragmento que sobrou recusa a promoção | passou (`ok: changelog.d/ sem fragmentos pendentes`, rc=0) |
| E1: PR de release sem fragmento novo passa na checagem do CI | `bin/forge-changelog conferir --base refs/remotes/origin/develop` | PR sem entrada de changelog e sem mudança de versão reprova; com versão nova só confere na promoção | passou (`PR de release (versão mudou)`, rc=0) |
| Integridade do CHANGELOG, dos fragmentos e da conferência de release | `tests.test_changelog` e `tests.test_conferir_release` | formato do fragmento, seção `[Não publicado]`, versão já existente recusada, manifesto sem `version` ou link simbólico recusado, homolog e main | passou (45 testes, `OK (skipped=1)`; ver cenários) |
| Plugin válido com a versão nova | `scripts/validar-plugin.sh` | manifesto do plugin e do `dev/` | passou (`Validation passed`, rc=0) |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog tests.test_conferir_release -v` na worktree `wt-qa-release-0.30.2` (HEAD `ce8e54c`): `Ran 45 tests in 2.361s`, `OK (skipped=1)`, rc=0. O skip é de `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, que se dispensa porque a worktree está em HEAD destacado (`branch 'HEAD' não é de melhoria`); o commit não traz fragmento novo, então a regra não tem o que checar. Skip não foi posto por mim.
- Reprodução ponta a ponta: `git archive 82cd515` em `$TMPDIR/qa-engineer-release-0.30.2/rep`, `python3` com o `bin/forge-changelog` da worktree, `release 0.30.2 2026-10-24` → `[0.30.2]: 1 fragmento(s) juntado(s) e apagado(s)`, rc=0. `diff` do `CHANGELOG.md` contra o do commit: vazio. Texto da entrada conferido contra o fragmento da base: `- Primeiro lote da máquina (MAQ-LOTE-A): pesos da divisão regravados com teste de 20% sem peso, push de código em segundo plano e V2 do autor dirigida e na fila.`, igual palavra por palavra, sob `### Alterado`, acima de `## [0.30.1]`.
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0. Há avisos do validador de diretório (`ICON_MISSING` no plugin raiz; `README_MISSING` no `dev/`). Ambos já existem na base (`dev/README.md` não existe em `82cd515`) e não são do diff da release; o `--strict` do validador passa, então não viram achado. Registrado como risco.
- Sandbox: a validação tentou alcançar `api.anthropic.com` e o intake de logs do `claude`, e o sandbox negou; isso é telemetria da CLI e não alterou o resultado.
- `docs/engineering/achados-recorrentes.md` (PA-7): sem item registrado ("nenhum ainda"), nada a conferir.
- Suíte completa não rodada por mim (brief: só os testes do lote; a completa roda no pre-push e no CI).
