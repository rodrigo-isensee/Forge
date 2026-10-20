---
tipo: qa
contrato: 1
pedido: dv-6
branch: melhoria/dv-6
commit: e316b0b1665442f203bde8489531ca125594836f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA: dv-6 (forge-changelog conferir aceita PR que só fecha fragmentos)

Sem UX nem API. Diff `e9c81e0..e316b0b` (`bin/forge-changelog`, `tests/test_changelog.py`, `changelog.d/dv-6.md`). Não escrevi o diff. Review (`d16780c`) e segurança (`6e394d3`) aprovados; os commits depois de `e316b0b` só trazem esses dois pareceres.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 (fechamento com todas as linhas passa) | `test_fechamento_com_todas_as_linhas_no_changelog_passa`; simulação 1 | só fragmento apagado + CHANGELOG + parecer | passou |
| E1 (falta linha: reprova citando a linha) | `test_fechamento_sem_a_linha_no_changelog_reprova`; simulação 2 | linha ausente do CHANGELOG | passou |
| E2 (fragmento apagado + outra mudança da fábrica exige fragmento novo) | `test_apagar_fragmento_com_outra_mudanca_da_fabrica_exige_fragmento_novo`, `test_fechamento_com_docs_regras_continua_exigindo_fragmento`; simulação 3 | `docs/regras/` não é parecer | passou |
| Volta 1 (parecer do próprio PR não conta) | `test_fechamento_com_parecer_em_docs_reviews_passa`; simulação 1 | `docs/reviews/` | passou |
| E3 (fragmento) | `changelog.d/dv-6.md` presente, formato lido por `ler_fragmento` | n/a | passou |

## Simulação do caso do #210 (repositório temporário em `$TMPDIR`, `bin/forge-changelog` da worktree)
1. Apaga `changelog.d/x.md`, move a linha para o `CHANGELOG.md`, traz `docs/reviews/x.md`: `ok: fechamento de 1 fragmento(s), linhas no CHANGELOG`, rc=0.
2. Mesmo PR sem a linha no `CHANGELOG.md`: `changelog.d/x.md: a linha apagada não está no CHANGELOG.md: - corrige a coisa X (DV-9).`, rc=1.
3. Caso 1 mais `docs/regras/R-X.md`: `Registre a mudança num fragmento novo em changelog.d/ ...`, rc=1.

## Vermelho antes do verde
Cópia do HEAD em `$TMPDIR` com `bin/forge-changelog` de `e9c81e0` (`git show e9c81e0:bin/forge-changelog`): `python3 -m unittest tests.test_changelog -q` deu `Ran 29 tests` / `FAILED (failures=3, skipped=1)`; falharam o teste de fechamento que passa (`'fechamento de 1 fragmento(s)' not found`), o de linha ausente (`AssertionError: 0 == 0`) e o de fechamento com parecer. Os dois testes de "exige fragmento" passam sem a mudança, como esperado (é o comportamento antigo que a mudança preserva). O `skipped=1` é pré-existente (testes condicionais ao ambiente, `tests/test_changelog.py:298,302`).

## Execução
- `python3 -m unittest discover -s tests -q` na worktree (HEAD `6e394d3`): `Ran 870 tests in 156.538s` / `OK`.
- `scripts/validar-plugin.sh`: `Validation passed` nos manifestos do marketplace e do plugin.
- Mutação: sem ferramenta gratuita de mutação configurada para este código; o vermelho antes do verde faz o papel. Lacuna declarada.

## Riscos conhecidos (não bloqueantes)
A conferência é por substring no `CHANGELOG.md` inteiro (A1 do review e informativo da segurança); virou o cartão DV-6-LINHA-INTEIRA, fora deste pedido.
