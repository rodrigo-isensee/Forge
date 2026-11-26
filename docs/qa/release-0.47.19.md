---
tipo: qa
contrato: 1
pedido: release-0.47.19
branch: melhoria/v0481-release-04719-anexo
commit: da7b59be13063ef51235c1e82f53bfda493cc25f
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: release 0.47.19 (E12.29) (versão 0.47.19, head da7b59be)

QA da versão inteira, 18 itens, revalidada sobre o anexo. A rodada anterior (head 9487d956, E12.24) aprovou a marca (10 itens: #874, #877, #885, #886, #890, #892, #895, #896, #897, #898, mais a marca #905); `git diff b224ee09..da7b59be` (`b224ee09` é a marca da 0.47.18): 222 arquivos. O anexo (#907) soma 8 itens que entraram na `develop` depois: #875, #878, #888, #901, #902, #903, #904, #906 (parecer próprio em `docs/qa/v0481-release-04719-anexo.md`). Modelo: `docs/qa/release-0.47.16.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.19; `## [0.47.19] - 2026-11-26` | manifestos iguais | passou |
| CHANGELOG em português, `[Não publicado]` vazio | leitura: 26 linhas na seção (Adicionado, Alterado, Corrigido), com id de origem | seção acima da 0.47.18 | passou |
| Os 18 itens estão na seção | 10 da marca: 21/21 linhas dos fragmentos achadas (rodada E12.24); 8 do anexo: 14/14 linhas achadas literal | nenhum a menos | passou |
| Linha do anexo confere com os itens | `CHANGELOG.md:24` diz 7 itens, sem o #906; são 8 | contagem e lista | FALHOU (A1) |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: ok | só `README.md` | passou |
| Junção | `git merge-base --is-ancestor b224ee09 HEAD`: ok; marca (#905) e os 8 PRs sob o anexo | corte contém a marca anterior | passou |
| Sem teste pulado indevido | `git diff b224ee09..HEAD -- 'tests/*.py'`: 2 linhas `skipUnless` por capacidade (`os.mkfifo`, `signal.setitimer`), do #885; nenhum `skip` incondicional nem `expectedFailure` | n/a | passou |
| Controle com mutantes declarados | `bin/`, `hooks/` e `tests/catraca.py` mudaram nos 18 itens | n/a | passou (prova no parecer de cada item; não rerrodei) |
| Pareceres dos itens | QA aprovado de cada um dos 18 em `docs/qa/` | n/a | passou |
| Itens que afrouxam regra, listados e com aceite do dono | #877, #885, #895, #898 e os 8 do anexo trazem `[afrouxa-regra: ...]` no título com o motivo; os 8 do anexo têm também o rótulo `afrouxa-regra` e citam decisão do dono (24/11, 25/11 07:31, 07:52, 17:07, 21:15); #877 é exceção ao R-VERIFY à espera do dono (no CHANGELOG) | destaque, motivo, aceite | passou; a decisão do #877 fica com o dono (`R-DECISAO`) |

## Execução
- Sem suíte local (diff do anexo só de texto). Módulos tocados: `test_changelog.py` (91, OK) e `test_conferir_release.py` (17, OK).
- Sem linha `- ci:`: a suíte do da7b59be foi cancelada pelo push do parecer de review (80cd983c); a volta muda o head.
- Segurança e acessibilidade: sem tela; a segurança tem parecer próprio.

## Achados
- A1 (bloqueante) CHANGELOG.md:24 · A linha do anexo diz "os 7 itens" e omite o #906 (CHANGELOG.md:36). Corrigir: "os 8 itens" e incluir #906.

## Parecer
Reprovado só por A1; os 18 itens e o resto da junção conferem.
