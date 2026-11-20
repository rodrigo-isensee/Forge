---
tipo: qa
contrato: 1
pedido: release-0.47.11
branch: melhoria/v0479-release-04711
commit: fe752d14857633363b9da383eeeb9321ff67b7fe
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: release 0.47.11 inteira (v0478, E42.4)

Head `fe752d14` (marca da 0.47.11 sobre a develop em `119aed79`). Cobre `git diff v0.47.10..fe752d14` (24 arquivos) e a junção dos dois itens, cada um já integrado com os próprios pareceres.

Itens da versão, todos com review, QA e segurança `parecer: aprovado` em `docs/{reviews,qa,security}/`:
- `forge-placar fases` com mediana, p75, corte por hora e horas paradas (#706): `v0479-meta85-placar`, commit `6f6aab30`.
- Sonda S1 e corpus sem dependência de relógio e carga (#701): `v0479-develop-relogio`, commit `76cbce17`.

Delta da marca: os arquivos alterados entre `119aed79` e `fe752d14` são só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md` e os dois fragmentos removidos de `changelog.d/`; nenhum arquivo de `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`. Por isso mutação e vermelho antes do verde não se aplicam a este head (o código de cada item teve os dois no parecer próprio).

Prova da suíte: o check-run `bateria` do CI do PR no mesmo sha. A suíte local não vale (I5) e falha por ambiente do sandbox (/proc e gh). Rodado aqui: `python3 -I -m unittest discover -s tests -p test_changelog.py` (89 testes, OK), `bin/forge-changelog conferir-release` (ok, rc 0) e `scripts/validar-plugin.sh` (os dois manifestos passaram; o validador registrou rede negada ao serviço da Anthropic, sem efeito no resultado).

Sem achados (o bloco `## Achados` fica de fora).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Os dois manifestos batem com o CHANGELOG | `plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.11"`; uma entrada `## [0.47.11] - 2026-11-20` | manifesto sem par | passou |
| Entrada em português com os dois itens | leitura da `[0.47.11]`: Adicionado (`forge-placar fases`, META85) e Corrigido (sonda S1 e corpus, E33.1/E33.6) | item sem entrada | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release`: ok | pasta só com README | passou |
| Testes do changelog | `test_changelog.py`: 89 testes, OK | n/a | passou |
| Plugin válido | `scripts/validar-plugin.sh`: Validation passed (raiz e dev) | n/a | passou |
| Os itens juntos, sem código após a marca | lista de arquivos do delta da marca: só versão, changelog e fragmentos | n/a | passou |
| Cada item com os três pareceres aprovados | `parecer: aprovado` nos 6 arquivos acima | portão faltando | passou |
