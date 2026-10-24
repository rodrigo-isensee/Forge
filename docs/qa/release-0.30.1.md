---
tipo: qa
contrato: 1
pedido: release-0.30.1
branch: melhoria/release-0.30.1
commit: 7af2bd4f5207e3b49376751d3e07a524336f5715
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: release-0.30.1

Base `cb653db0aca58a97d5ed60f53ae92746ebfa6094`, head `7af2bd4`. Diff de 5 arquivos: `CHANGELOG.md` (+6), `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` (0.30.0 para 0.30.1), e os dois fragmentos `changelog.d/est-030-l2.md` e `est-030-l3.md` apagados. Sem código de produção, sem `bin/`, `hooks/` nem `tests/catraca.py` no diff, então não há mutantes a declarar nem teste novo de regra (vermelho antes do verde não se aplica).

## Achados

## Critério → teste → resultado
Não há especificação de UX nem `CA-n`; as obrigações vêm do pedido REL-0301 (E1) e da decisão "C" do dono (versão 0.30.1).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: `release` junta os 2 fragmentos de #311 e #313 e os apaga | reprodução em cópia: `bin/forge-changelog release 0.30.1 2026-10-24` sobre a base e `diff` com o CHANGELOG do commit | os 2 fragmentos da base, nenhum sobra | passou (diff vazio, `changelog.d/` sem fragmentos) |
| E1 e decisão C: versão 0.30.1 nos dois manifestos | leitura dos dois `plugin.json` e `tests.test_changelog` (versão do manifesto x CHANGELOG) | os dois manifestos iguais entre si e ao CHANGELOG | passou |
| Integridade do CHANGELOG e dos fragmentos | `tests.test_changelog` | formato, seção `[Não publicado]` vazia | passou |
| Conferência da release | `tests.test_conferir_release` | n/a | passou |
| Plugin válido | `scripts/validar-plugin.sh` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_changelog tests.test_conferir_release`: `Ran 45 tests ... OK (skipped=1)`. O skip é do teste `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, que se auto-dispensa porque a worktree está em HEAD destacado (`branch 'HEAD' não é de melhoria`); o CHANGELOG do commit não tem fragmento novo, então a regra não tem o que checar. Nenhum skip foi posto por mim.
- `scripts/validar-plugin.sh`: `Validation passed`. O sandbox negou rede a `api.anthropic.com` e ao Datadog (telemetria do `claude`); não afetou o resultado.
- Reprodução ponta a ponta: `git archive cb653db` em `$TMPDIR/qa-engineer-release-0.30.1/base`, `bin/forge-changelog release 0.30.1 2026-10-24` (`[0.30.1]: 2 fragmento(s) juntado(s) e apagado(s)`), `diff CHANGELOG.md` contra o do commit: vazio (`DIFF_VAZIO`).
- Texto do CHANGELOG conferido contra os fragmentos da base: as duas entradas (Adicionado L2/M15, Alterado L3/M9) batem palavra por palavra, sob `## [0.30.1] - 2026-10-24`, acima do `[0.30.0]`.
- `docs/engineering/achados-recorrentes.md` (PA-7): sem item registrado ("nenhum ainda"), nada a conferir.
- Suíte completa não rodada por mim (brief: só os testes do lote; a completa roda no pre-push e no CI).
