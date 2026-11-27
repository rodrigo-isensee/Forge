---
tipo: qa
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20
commit: 1e301536467df853dae1e7229952b930078c979d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: release 0.47.20 (E43.4) (versão 0.47.20, head 1e301536)

QA da leva `main..1e301536` (PR #935, 26 commits, 23 itens: #909, #910, #913, #914, #916 a #934). Marca `3bf1456e` mais o #933 e o #934, anexados por merge da develop `8855671d`. Modelo: `docs/qa/release-0.47.19.md`. Os itens já têm parecer de QA em `docs/qa/`; não rerrodei a suíte (R-QA, G3).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.20; `## [0.47.20] - 2026-11-27` | manifestos iguais | passou |
| `[Não publicado]` vazio, seção em português | CHANGELOG linhas 5 a 7 | seção acima da 0.47.19 | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: ok | só `README.md` | passou |
| Os 23 itens estão na seção | 24 entradas (Adicionado 7, Alterado 9, Corrigido 8) para 23 itens | nenhum a menos | passou |
| Testes dos módulos tocados pela junção | `test_changelog` e `test_conferir_release`: 108 OK (33 s) | n/a | passou |
| CI do head | `gh pr checks 935`: rc=0, suíte 5/5, instalação 3.14, catraca, pareceres, passos, longas verdes | n/a | passou |
| Sem teste pulado indevido | nenhum `skip` novo achado no diff da junção | n/a | passou |
| 7 regras afrouxadas (#909, #918, #920, #928, #929, #931, #932) | commits e títulos trazem `[afrouxa-regra: ...]` com motivo; rótulo `afrouxa-regra` em 6 de 7 | destaque, motivo, aceite | passou, com A1 e A2 |
| Pareceres dos itens | QA aprovado dos itens em `docs/qa/` (17 arquivos no diff) | n/a | passou |

## Execução
- Cópia própria em `~/.forge-contrib/wt/v0481-release-0-47-20-qa-engineer`, head igual ao remoto.
- Sem tela: acessibilidade n/a. Segurança e review têm parecer próprio.
- ci: 1e301536467df853dae1e7229952b930078c979d verde

## Parecer
Aprovado: marca, junção e CHANGELOG conferem. Os dois achados abaixo são do texto do PR da main e do rótulo, não do código.

## Achados
- A1 (recomendado) docs/qa/release-0.47.20.md:1 · o corpo do PR #935 não lista as 7 regras afrouxadas (#909, #918, #920, #928, #929, #931, #932) nem o aceite do dono; o corpo do PR da main deve trazer a tabela "Itens que afrouxam regra", como na 0.47.19.
- A2 (recomendado) docs/qa/release-0.47.20.md:1 · o #918 (ato `rotulo-pelo-time`) tem `[afrouxa-regra]` no título mas não o rótulo `afrouxa-regra`; as outras seis têm. Confirmar com o dono antes do merge na main.
