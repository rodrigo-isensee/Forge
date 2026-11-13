---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/release-0.47.0
commit: 51c51139b04881506718924895678cecb0a55453
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: marca da release 0.47.0 (v047, E2.8)

Head `51c51139`. Escopo: versão nos dois `plugin.json`, entrada 0.47.0 do `CHANGELOG.md` contra os 22 fragmentos, linha do placar de mutação. Sem PR aberto para a branch (`gh pr list --head` vazio): sem check-run `bateria`; rodei só os testes afetados (`tests.test_changelog`, `tests.test_conferir_release`) e os cenários abaixo.

## Achados
- A1 (bloqueante) docs/engineering/placar-mutacao.md:20 · a linha 0.47.0 foi medida com --desde v0.45.5 e não com a tag anterior v0.46.0, e a spec envio-leve saiu rc=2 por carga. Com --desde v0.46.0: mortos=62 invalido=1 specs=9. Regravar a linha.
- A2 (recomendado) tests/mutantes/v0457-escopo-ponto-2.json:1 · mutante M10 sai inválido (trecho em bin/forge-check aparece 0 vezes): spec envelhecida, guarda mudada depois sem a spec acompanhar. Atualizar o trecho ou isentar a spec.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão 0.47.0 nos dois manifestos | `grep '"version"'` em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`; `scripts/conferir-release.py --base origin/develop` ("versão base: 0.46.0 \| versão da release: 0.47.0") | os dois manifestos iguais e acima da base | passou |
| CHANGELOG 0.47.0 com os 22 fragmentos | `git diff --diff-filter=D origin/develop...HEAD -- changelog.d` = 22 arquivos; cada linha `- ` dos 22 (23 itens, escopo-ponto traz 2) procurada em CHANGELOG.md: nenhuma ausente; seção tem 23 itens | fragmento sem entrada; `changelog.d/` só com README | passou |
| `changelog.d/` sem pendentes | `bin/forge-changelog conferir-release` ("ok: changelog.d/ sem fragmentos pendentes") | pasta vazia | passou |
| Testes do changelog e da release | `python3 -m unittest tests.test_changelog tests.test_conferir_release` (91 testes, OK) | n/a | passou |
| Linha do placar confere com o método | `scripts/placar-mutacao.py --desde v0.46.0 --versao 0.47.0` | tag anterior certa | reprovou (A1) |
| Spec envio-leve (rc=2 sem contar) | `bin/forge-mutante tests/mutantes/envio-leve.json` isolada: M1 a M5 morreu, rc=0 | carga da máquina (~15 em 12 CPUs) | julgado: falha de ambiente, não da spec |

## Cenários e resultado real
- Placar. A linha gravada (`mortos=49 ... specs=9`) não reproduz com a tag certa. Com `--desde v0.45.5` a amostra é a de `placar.json` mais envio-leve, fechar-medir-do-log (2), maq-i9-refazer-1, mp1311, trava-agente-morto (2 a 4): 54 mortos, `specs=9`, e 54 menos os 5 de envio-leve (rc=2 no autor) dá os 49 gravados. Ou seja, o autor mediu desde v0.45.5 e perdeu envio-leve. A tag anterior da release é `v0.46.0` (existe no remoto; `git ls-remote --tags origin 'v0.46.0'` = 5f83b58d); o modelo do próprio arquivo manda usar a tag da release anterior. Com ela a amostra é a `placar.json` mais mp1311, trava-agente-morto (todas), v0457-escopo-ponto-2 e -3: 62 mortos, 0 sobreviventes, 1 inválido (A2). O placar é medida e não portão: o que reprova é a linha gravada divergir do método, não o resultado da mutação.
- envio-leve. Nem entra na amostra certa (já estava na `v0.46.0`). Isolada, passa com rc=0 e 5 mortos, então o rc=2 foi falha de ambiente (diretriz 14: 2 tentativas, uma delas basta aqui).
- Vermelho antes do verde e mutação no diff: n/a, a marca não altera `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py` (diff: 4 arquivos modificados, 22 fragmentos removidos).

## Provas
- `git rev-parse HEAD` = 51c51139b04881506718924895678cecb0a55453
- `git diff --name-status origin/develop...HEAD`: 22 D (changelog.d) e 4 M (os dois plugin.json, CHANGELOG.md, placar-mutacao.md)
- `scripts/placar-mutacao.py --desde v0.46.0 --versao 0.47.0`: `placar: 0.47.0 mortos=62 sobreviveu=0 equivalente=0 invalido=1 sem-veredito=0 specs=9`
- `scripts/placar-mutacao.py --desde v0.45.5 --versao 0.47.0`: `placar: 0.47.0 mortos=54 sobreviveu=0 equivalente=0 invalido=0 sem-veredito=0 specs=9`
