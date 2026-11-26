---
tipo: qa
contrato: 1
pedido: v0481
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
# QA: anexo da 0.47.19 (E12.29) (versão 0.47.19, head da7b59be)

QA do #907, 1ª rodada completa. Diff `8ae4d6c6..da7b59be` (merge-base com a `develop` igual à Base-sha): 9 arquivos, +15 -22; só `CHANGELOG.md` e 8 fragmentos apagados de `changelog.d/`. Itens anexados: #875, #878, #888, #901, #902, #903, #904, #906. Versão não muda. Sem código, sem teste novo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão nos manifestos igual ao CHANGELOG | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.19; `## [0.47.19] - 2026-11-26` | manifestos iguais | passou |
| Os 8 fragmentos estão na seção | script: 14/14 linhas `- ` dos 8 fragmentos (base 8ae4d6c6) achadas literal no CHANGELOG | nenhum a menos | passou |
| `changelog.d/` sem fragmentos | `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes` | só `README.md` | passou |
| Linha do anexo diz o que anexou | `CHANGELOG.md:24`: "os 7 itens ... (#875 ... #904)"; o diff anexa 8 (o #906 está em `CHANGELOG.md:36`) | contagem e lista = itens anexados | FALHOU (A1) |
| Seção `[0.47.19]` | 26 linhas `- ` (11 da marca, 14 do anexo, a do anexo); `[Não publicado]` vazio | marca não perdeu linha | passou |
| Módulos do assunto | `python3 -I -m unittest discover -s tests -p test_changelog.py` (91, OK); `test_conferir_release.py` (17, OK) | n/a | passou |
| Pareceres dos 8 itens | `docs/qa/v0481-{ae2-quadro-anda,g2-1-publicar,prazo-forge,autorizacoes-fixas,voltas-alinhada,d2-no-brief,entrega-desde-revisar,rotulo-base-alheia}.md`: todos `aprovado` | n/a | passou |
| Itens com afrouxa-regra e aceite do dono | os 8 PRs trazem `[afrouxa-regra: ...]` no título, com o motivo e a decisão do dono (24/11, 25/11 07:31, 07:52, 17:07, 21:15), e o rótulo `afrouxa-regra` (`gh pr view`) | destaque e rótulo | passou |
| Sem teste pulado | `git diff b224ee09..HEAD -- 'tests/*.py'`: só 2 `skipUnless` por capacidade (`os.mkfifo`, `signal.setitimer`), já da marca; nenhum nos 8 itens | n/a | passou |

Sem suíte local nem mutante: nada de código no diff.

## Achados
- A1 (bloqueante) CHANGELOG.md:24 · A linha do anexo diz "os 7 itens" e omite o #906 (anexado em da7b59be, CHANGELOG.md:36). Corrigir: "os 8 itens", incluir #906 (e E12.27). Mesmo achado do review.

## Parecer
Reprovado (A1, só texto do CHANGELOG; o resto confere). Sem linha `- ci:`: a suíte do da7b59be foi cancelada (10 partes e teto de pulados `cancelled`) pelo push do parecer de review (80cd983c, run 45825600313), e a volta muda o head. Verdes no da7b59be: `bateria (pareceres)`, `bateria (passos)`, `bateria (verificações longas)`, `catraca`, `instalação`, `árvore já provada na develop`. Na revalidação, só a linha 24 do CHANGELOG muda.
