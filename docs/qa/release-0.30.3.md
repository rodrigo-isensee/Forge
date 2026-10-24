---
tipo: qa
contrato: 1
pedido: release-0.30.3
branch: melhoria/release-0.30.3
commit: 6f0b82473ac50b4031e73657808604514ce2ae32
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: release-0.30.3

Base `c96f62299eace19f3abceac44d4cbc23978c89ac` (`origin/develop`, com #319 e #320), head `6f0b82473ac50b4031e73657808604514ce2ae32` (`chore(release): versão 0.30.3 (#319 e #320)`). Diff de 5 arquivos, 8 inserções e 6 remoções: `CHANGELOG.md` (+6: seção `## [0.30.3] - 2026-10-24` com `### Adicionado` do LOTE-FECHAR-031 e `### Corrigido` do CHANGELOG-JSON-LINK), `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` (0.30.2 para 0.30.3) e os fragmentos `changelog.d/lote-fechar-031.md` e `changelog.d/changelog-json-link.md` apagados. Sem código de produção, sem `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` no diff: não há mutantes a declarar. Não há teste novo nem regra nova no diff, então vermelho antes do verde não se aplica. Sem especificação de UX nem `CA-n`; as obrigações vêm do pedido REL-0303 (E1 e E2.2), do REL-0303-REV (E3) e das decisões "A", "B" e "C" do dono (versão 0.30.3, exceção ao SemVer, corte 4 do QA junto com o review).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| REL-0303 E1: `forge-changelog release 0.30.3 2026-10-24` sobre a base reproduz o CHANGELOG do commit | clone local em `$TMPDIR/qa-engineer-release-0.30.3/rep` posicionado em `c96f622`, `bin/forge-changelog release 0.30.3 2026-10-24` da worktree e `git diff --quiet 6f0b824` na cópia | os dois fragmentos entram e somem; nenhuma linha de `[Não publicado]` sobra; a seção 0.30.3 fica acima da 0.30.2 | passou (`[0.30.3]: 2 fragmento(s) juntado(s) e apagado(s)`, rc=0; `git diff --quiet 6f0b824` vazio, ou seja, árvore reproduzida idêntica ao commit, incluindo as duas remoções) |
| REL-0303 E1: versão 0.30.3 nos dois manifestos, iguais entre si e ao CHANGELOG | leitura dos dois `plugin.json` no commit, `grep -rn "0\.30\.2"` fora de `docs/` e do `.git` | os dois manifestos iguais; a única ocorrência de 0.30.2 fora de `docs/` é a seção histórica `## [0.30.2]` do CHANGELOG | passou (`"version": "0.30.3"` nos dois; `## [0.30.3]` no topo, `## [0.30.2]` logo abaixo) |
| REL-0303 E1: fragmentos removidos, sem sobra em `changelog.d/` | `bin/forge-changelog conferir-release` (gate da main) na worktree | fragmento que sobrou recusa a promoção | passou (`ok: changelog.d/ sem fragmentos pendentes`, rc=0) |
| Integridade do CHANGELOG, dos fragmentos e da conferência de release (REL-0303-REV E3) | `python3 -m unittest tests.test_changelog tests.test_conferir_release -v` na worktree | formato do fragmento, seção `[Não publicado]`, versão já existente recusada, manifesto sem `version` ou link simbólico recusado, homolog e main | passou (`Ran 52 tests in 3.819s`, `OK (skipped=1)`, rc=0; o skip é o de `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, já existente, que se dispensa com HEAD destacado porque o commit não traz fragmento novo) |
| Plugin válido com a versão nova (REL-0303-REV E3) | `scripts/validar-plugin.sh` na worktree | manifesto do plugin raiz e do `dev/` | passou (`Validation passed`, rc=0; avisos `ICON_MISSING` e `README_MISSING` já existem na base e não são do diff, então não viram achado) |
| Decisão "C": release pequena sobe só o último número | leitura da versão da base (0.30.2) e do commit (0.30.3) | salto no último número, não no do meio | passou (0.30.2 para 0.30.3) |
| Decisão "A", corte 2: commit só de parecer passa pelo `forge-check docs` no pre-push | `python3 bin/forge-check docs` na worktree | frontmatter e bloco de achados do parecer | passou (rc=0) |
| PA-7 (achados recorrentes) | leitura de `docs/engineering/achados-recorrentes.md` | itens registrados que este parecer deve checar | `nenhum ainda`: nada a conferir |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog tests.test_conferir_release -v` na worktree `wt-qa-release-0.30.3` (HEAD `6f0b824`): `Ran 52 tests in 3.819s`, `OK (skipped=1)`, rc=0. Log em `$TMPDIR/qa-engineer-release-0.30.3/unit.log`.
- Reprodução ponta a ponta: `git clone` local de `~/Forge` em `$TMPDIR/qa-engineer-release-0.30.3/rep`, `git checkout c96f622`, `python3 bin/forge-changelog release 0.30.3 2026-10-24` com o `bin/forge-changelog` da base. Resultado: `git status` mostra só `.claude-plugin/plugin.json`, `CHANGELOG.md`, `dev/.claude-plugin/plugin.json` modificados e os dois fragmentos apagados, o mesmo conjunto de 5 arquivos do commit. `git diff --quiet 6f0b824` na cópia: vazio.
- Texto da entrada conferido contra os fragmentos da base: as duas linhas do `### Adicionado` (forge-fechar) e do `### Corrigido` (forge-changelog release) saem palavra por palavra iguais aos fragmentos.
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0. Log em `$TMPDIR/qa-engineer-release-0.30.3/validar.log`. A CLI tentou alcançar `api.anthropic.com` e o intake de logs e o sandbox negou; é telemetria do `claude` e não alterou o resultado.
- `bin/forge-changelog conferir-release`: rc=0. `python3 bin/forge-check docs`: rc=0.
- Suíte completa não rodada por mim (brief: só os testes do lote; a completa roda no pre-push e no CI).
- Vermelho antes do verde e mutação: não se aplicam, porque o commit não tem teste novo, regra nova nem arquivo de guarda.

## Riscos
- Nenhum risco aberto para este commit. As duas entradas viviam só nos fragmentos de `changelog.d/` (a base não as tinha no corpo do CHANGELOG); a reprodução confirma a conversão completa do texto e a remoção dos fragmentos.
