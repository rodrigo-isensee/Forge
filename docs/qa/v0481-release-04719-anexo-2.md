---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-release-04719-anexo-2
commit: 17395e4d905fdbf24bbe21451050873b77261ba6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: segundo anexo da 0.47.19 (E12.42) (versão 0.47.19, head 17395e4d)

Delta contra a base 53e879cf: `CHANGELOG.md` (+2 -1) e a remoção do fragmento `changelog.d/v0481-fixtures-gerada.md`. Sem código. O #908 (índice das fixtures, d1ffc325, E18.1) tem parecer de QA aprovado próprio (`docs/qa/v0481-fixtures-gerada.md`).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fragmento do #908 entra na `[0.47.19]` | `CHANGELOG.md`: linha "Índice das fixtures dos hooks" em `### Alterado`, texto igual ao fragmento removido | nenhum item a menos | passou |
| Linha do anexo cita os 9 itens | `CHANGELOG.md:24` lista #875, #878, #888, #901, #902, #903, #904, #906, #908 e E12.40 | contagem e lista | passou |
| Versão igual | `plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.19 | manifestos | passou |
| `changelog.d/` sem fragmento | `bin/forge-changelog conferir-release`: ok | só `README.md` | passou |
| Seção com 19 itens | 27 linhas na seção (26 + 1 do #908) | n/a | passou |
| Índice em dia | `scripts/indice-fixtures.py --conferir`: "em dia" | arquivo gerado | passou |

## Execução
- Módulos tocados, rodados: `test_changelog.py` (91, OK), `test_conferir_release.py` (17, OK), `test_indice_fixtures.py` (10, OK).
- Sem mutante novo: o delta não muda linha de guarda.
- Segurança e acessibilidade: sem tela; a segurança tem parecer próprio.
- ci: 17395e4d905fdbf24bbe21451050873b77261ba6 verde

## Renovação do parecer `release-0.47.19` (19 itens)
Versão inteira no head 17395e4d: marca (10 itens, E12.24) + anexo #907 (8) + anexo #911 (#908) = 19. O #908 mudou só `docs/hooks-fixtures.md` e `scripts/indice-fixtures.py` (com teste e mutantes, parecer aprovado em `docs/qa/v0481-fixtures-gerada.md`); o índice confere em dia neste head. Os 18 anteriores não mudam neste delta.
- Itens com `afrouxa-regra`: #877, #885, #895, #898 e os do anexo #907 seguem listados no `CHANGELOG.md` com motivo e decisão do dono (o #877 segue exceção ao R-VERIFY à espera do dono, `R-DECISAO`). O #908 não afrouxa regra e não traz marca. Nada saiu da lista.
