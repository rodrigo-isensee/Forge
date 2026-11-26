---
tipo: qa
contrato: 1
pedido: release-0.47.19
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
# QA: release 0.47.19 (E12.42) (versão 0.47.19, head 17395e4d)

QA da versão inteira, 19 itens, renovada sobre o segundo anexo. A rodada anterior (head 0157977e, E12.33) aprovou 18; o delta `0157977e..17395e4d` soma o #908 (índice das fixtures dos hooks, `docs/hooks-fixtures.md` e `scripts/indice-fixtures.py`, mesclado antes do #907) e a linha do anexo do `CHANGELOG.md`. A marca (10 itens: #874, #877, #885, #886, #890, #892, #895, #896, #897, #898, mais a marca #905) foi aprovada em E12.24; o anexo (#907) soma 8 (#875, #878, #888, #901, #902, #903, #904, #906); o segundo anexo (#911) soma o #908. Modelo: `docs/qa/release-0.47.16.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos dois manifestos igual ao CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.19; `## [0.47.19] - 2026-11-26` | manifestos iguais | passou |
| CHANGELOG em português, `[Não publicado]` vazio | 27 linhas na seção, com id de origem | seção acima da 0.47.18 | passou |
| Os 19 itens estão na seção | 18 anteriores (rodadas E12.24 e E12.33); #908: linha literal em `### Alterado` | nenhum a menos | passou |
| Linha do anexo confere com os itens | `CHANGELOG.md:24` diz 9 itens, com o #908 e E12.40 | contagem e lista | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: ok | só `README.md` | passou |
| Índice das fixtures em dia (#908) | `scripts/indice-fixtures.py --conferir`: "em dia"; `test_indice_fixtures.py` 10 OK | arquivo gerado igual ao corpus | passou |
| Sem teste pulado indevido | só 2 `skipUnless` por capacidade (`os.mkfifo`, `signal.setitimer`), do #885; o #908 não adiciona pulo | n/a | passou |
| Controle com mutantes declarados | prova no parecer de cada item; o delta não toca guarda além do #908 (parecer `docs/qa/v0481-fixtures-gerada.md`, aprovado) | n/a | passou (não rerrodei) |
| Pareceres dos itens | QA aprovado de cada um dos 19 em `docs/qa/` | n/a | passou |
| Itens que afrouxam regra, listados e com aceite do dono | #877, #885, #895, #898 e os 8 do anexo seguem com `[afrouxa-regra: ...]`, motivo e decisão do dono; o #908 não afrouxa regra; #877 é exceção ao R-VERIFY à espera do dono (no CHANGELOG) | destaque, motivo, aceite | passou; a decisão do #877 fica com o dono (`R-DECISAO`) |

## Execução (revalidação incremental, E12.42)
- Módulos tocados, rodados de novo: `test_changelog.py` (91, OK), `test_conferir_release.py` (17, OK), `test_indice_fixtures.py` (10, OK); `conferir-release`: ok.
- Segurança e acessibilidade: sem tela; a segurança tem parecer próprio.
- ci: 17395e4d905fdbf24bbe21451050873b77261ba6 verde

## Parecer
Aprovado: os 19 itens e o resto da junção conferem.
