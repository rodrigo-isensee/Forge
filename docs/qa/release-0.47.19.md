---
tipo: qa
contrato: 1
pedido: release-0.47.19
branch: melhoria/v0481-release-04719-anexo
commit: 0157977e02dc38058c1b762b01d301985f85573f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: release 0.47.19 (E12.33) (versão 0.47.19, head 0157977e)

QA da versão inteira, 18 itens, revalidada sobre o anexo. A rodada anterior (head da7b59be, E12.29) reprovou só por A1; o delta `da7b59be..0157977e` no domínio do QA é só a linha 24 do `CHANGELOG.md` (+1 -1). A marca (10 itens: #874, #877, #885, #886, #890, #892, #895, #896, #897, #898, mais a marca #905) foi aprovada em E12.24; o anexo (#907) soma 8: #875, #878, #888, #901, #902, #903, #904, #906 (parecer próprio em `docs/qa/v0481-release-04719-anexo.md`). Modelo: `docs/qa/release-0.47.16.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.19; `## [0.47.19] - 2026-11-26` | manifestos iguais | passou (o delta não os toca) |
| CHANGELOG em português, `[Não publicado]` vazio | 26 linhas na seção, com id de origem (rodada anterior) | seção acima da 0.47.18 | passou |
| Os 18 itens estão na seção | 10 da marca: 21/21 linhas achadas (E12.24); 8 do anexo: 14/14 achadas literal | nenhum a menos | passou |
| Linha do anexo confere com os itens (A1 resolvido) | `CHANGELOG.md:24` no 0157977e diz 8 itens, com o #906 e E12.27 | contagem e lista | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: ok (rodado de novo) | só `README.md` | passou |
| Junção | `git merge-base --is-ancestor b224ee09 HEAD`: ok (rodada anterior; o delta não toca) | corte contém a marca anterior | passou |
| Sem teste pulado indevido | só 2 `skipUnless` por capacidade (`os.mkfifo`, `signal.setitimer`), do #885 | n/a | passou |
| Controle com mutantes declarados | prova no parecer de cada item; o delta não toca código | n/a | passou (não rerrodei) |
| Pareceres dos itens | QA aprovado de cada um dos 18 em `docs/qa/` | n/a | passou |
| Itens que afrouxam regra, listados e com aceite do dono | #877, #885, #895, #898 e os 8 do anexo com `[afrouxa-regra: ...]`, motivo e decisão do dono; #877 é exceção ao R-VERIFY à espera do dono (no CHANGELOG) | destaque, motivo, aceite | passou; a decisão do #877 fica com o dono (`R-DECISAO`) |

## Execução (revalidação incremental, E12.33)
- Módulos tocados, rodados de novo: `test_changelog.py` (91, OK) e `test_conferir_release.py` (17, OK); `conferir-release`: ok.
- Segurança e acessibilidade: sem tela; a segurança tem parecer próprio. O descendente 9dfbc65f só traz pareceres de segurança.
- ci: 0157977e02dc38058c1b762b01d301985f85573f verde via 9dfbc65f22b831fdc981654e0215228dea38c754

## Parecer
Aprovado: A1 resolvido; os 18 itens e o resto da junção conferem.
