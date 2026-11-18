---
tipo: qa
contrato: 1
pedido: release-0.47.7
branch: melhoria/v0477-release-0477
commit: 55e4db4b0350421bac4f12c1e98ff78ffa3dd94a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: release 0.47.7 inteira (v0477, E3.4)

Head `55e4db4b` (marca da 0.47.7 sobre a develop em `fd1356b5`). Cobre `git diff efb25ff7 55e4db4b` (15 arquivos; `efb25ff7` é a marca da 0.47.6, pois a tag `v0.47.6` não existe neste clone) e a junção dos dois itens, cada um já integrado com os próprios pareceres.

Itens da versão, todos com review, QA e segurança `parecer: aprovado` em `docs/{reviews,qa,security}/`:
- Defeitos do `forge-check` (#667): `v0477-forge-check-defeitos` (`veredito_trocado` lê só as versões que citam o sha, `bin/forge-check`).
- Textos de processo (#668): `v0477-textos-processo` (`agents/tech-lead.md`, `docs/regras/R-LIMITES.md`, `skills/trabalho-em-paralelo/ritmo-e-corte.md`).

Delta da marca: `git diff --name-only fd1356b5 55e4db4b` lista só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md` e os dois fragmentos removidos de `changelog.d/`; nenhum código após a marca. O único arquivo de controle do diff da versão é `bin/forge-check`, com spec de mutantes própria (`tests/mutantes/v0477-forge-check-defeitos.json`), revalidada abaixo.

Prova da suíte: o check-run `bateria` do CI do PR no mesmo sha. A suíte local não vale (I5) e falha por ambiente do sandbox (/proc e gh); o CI do PR é o que decide a integração. O vermelho antes do verde de cada item está nos pareceres próprios; a marca não muda código.

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão sobe contra a main | `python3 scripts/conferir-release.py --base origin/main`: base 0.47.5, release 0.47.7 | versão igual à da base | passou |
| Os dois manifestos batem com o CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.7"`; uma entrada `## [0.47.7] - 2026-11-18` | manifesto sem par | passou |
| Entrada em português com os dois itens | leitura da `[0.47.7]`: Alterado (tech-lead, H8 e SIEG-G6), Corrigido (VEREDITO-TROCADO-LENTO) | item sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release`: ok | pasta só com README | passou |
| Os itens juntos, sem código após a marca | `git diff --name-only fd1356b5 55e4db4b`: só versão, changelog e fragmentos | n/a | passou |
| Cada item com os três pareceres aprovados | `parecer: aprovado` nos 6 arquivos `v0477-*` de reviews, qa e security | portão faltando | passou |
| Mutantes do controle `bin/forge-check` na junção | `bin/forge-mutante tests/mutantes/v0477-forge-check-defeitos.json`: M1 e M2 morreram (2 de 2) | falha do `git grep` conta como veredito trocado | passou |
| Testes do módulo alterado na junção | `python3 -I -m unittest discover -s tests -p test_selo_e_entrega.py`: 119 testes, OK | n/a | passou |
| Suíte no head | check-run `bateria` do CI do PR, mesmo sha | n/a | pendente do CI do PR (não é achado) |

## Provas
- `git rev-parse HEAD` = 55e4db4b0350421bac4f12c1e98ff78ffa3dd94a
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/main`: versão base: 0.47.5 | versão da release: 0.47.7
- `bin/forge-mutante tests/mutantes/v0477-forge-check-defeitos.json`: `M1 · morreu · bin/forge-check:2808`; `M2 · morreu · bin/forge-check:2816`
- `test_selo_e_entrega.py`: `Ran 119 tests ... OK`

## Notas
- Sem bugs abertos.
