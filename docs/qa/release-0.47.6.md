---
tipo: qa
contrato: 1
pedido: release-0.47.6
branch: melhoria/v0476-release-0476
commit: 00fa5c76561332e52eed0dca9c077f4db8adc15c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: release 0.47.6 inteira (v0474, E4.43)

Head `00fa5c76` (marca da 0.47.6 sobre a develop em `9ae3e442`). Cobre `git diff v0.47.5..00fa5c76` (194 arquivos) e a junção dos cinco itens, cada um já integrado com os próprios pareceres.

Itens da versão, todos com review, QA e segurança `parecer: aprovado` em `docs/{reviews,qa,security}/`:
- MP6, disco (#659): `v0476-mp6`, commit `93d21712`.
- Diretriz 36 (#661): `v0475-dir36`, commit `42af552e`.
- MP3, teto flexível entre projetos (#662): `v0476-mp3`, commit `2be06289`.
- Núcleo do Jarvis volta ao teto (#666): `v0476-nucleo-teto`, commit `8a91fe3b`.
- Dependências da stack na cópia (#660): `v0476-stack-deps`, commit `8727471d`.

Delta da marca: `git diff --name-only 9ae3e442 HEAD` lista só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md` e os cinco fragmentos removidos de `changelog.d/`; nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`. Por isso mutação e vermelho antes do verde não se aplicam a este head (o código de cada item teve os dois no parecer próprio).

Prova da suíte: o check-run `bateria` do CI do PR no mesmo sha. A suíte local não vale (I5) e falha por ambiente do sandbox (/proc e gh). Na hora deste parecer o CI do push da develop em `9ae3e442` (run 44315751912) ainda estava em andamento; o CI do PR é o que decide o merge.

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão sobe contra a main | `python3 scripts/conferir-release.py --base origin/main`: base 0.47.5, release 0.47.6 | versão igual à da base | passou |
| Os dois manifestos batem com o CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.6"`; uma entrada `## [0.47.6] - 2026-11-18` | manifesto sem par | passou |
| Entrada em português com os cinco itens | leitura da `[0.47.6]`: Adicionado (MP3, MP6, `--instalar`), Alterado (diretriz 36 e voltas), Corrigido (núcleo do Jarvis) | item sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release`: ok | pasta só com README | passou |
| Os itens juntos, sem código após a marca | `git diff --name-only 9ae3e442 HEAD`: só versão, changelog e fragmentos | n/a | passou |
| Cada item com os três pareceres aprovados | `parecer: aprovado` nos 15 arquivos acima | portão faltando | passou |
| Suíte no head | check-run `bateria` do CI do PR, mesmo sha | n/a | pendente do CI do PR (não é achado) |

## Provas
- `git rev-parse HEAD` = 00fa5c76561332e52eed0dca9c077f4db8adc15c
- `bin/forge-changelog conferir-release`: ok: changelog.d/ sem fragmentos pendentes
- `scripts/conferir-release.py --base origin/main`: versão base: 0.47.5 | versão da release: 0.47.6

## Notas
- Sem bugs abertos.
