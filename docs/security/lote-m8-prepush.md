---
tipo: revisao-seguranca
contrato: 1
pedido: lote-m8-prepush
branch: melhoria/lote-m8-prepush
commit: a15a5697609a207eb56aca0b0c64e6f26c1a1e1d
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-m8-prepush

Escopo: diff `3c66b881af31817ce5d2dde996c7ca56d54cb511...a15a5697609a207eb56aca0b0c64e6f26c1a1e1d` (EST-M8, REVERSAO-MAPA, FORGE-TESTES-CAMINHOS): `.githooks/pre-push`, `bin/forge-testes`, os testes `tests/test_pre_push_afetados.py` e `tests/test_testes_tocados.py` e o fragmento do changelog.

## Gatilhos
`R-SEGURANCA`, controles do Forge: o pre-push (bloqueios de `R-MAIN`, `R-VERIFY`, `R-FLUXO` e a prova de árvore verde) passa a depender do plano do `bin/forge-testes`, que vira filtro de um portão local.

## Achados
- A1 (bloqueante) bin/forge-testes:88 · classe mapa mais estreito que os testes que executam o arquivo: no envio dirigido, hooks/agentes.py e hooks/_comum.py não rodam test_agentes_hash_brief e test_agentes_clone, hooks/vigia.py não roda test_textos_dono_f10, bin/forge-changelog (linha 76) não roda test_conferir_release
- A2 (recomendado) .githooks/pre-push:253 · o plano é decidido pela cópia do bin/forge-testes da própria branch: um diff que muda o script e tira o nome dele de ALTERA_O_MAPA (bin/forge-testes:110) obtém plano dirigido; conferir no hook, sem o script, se o diff toca bin/forge-testes, tests/config.json ou .githooks/
- A3 (recomendado) .githooks/pre-push:252 · a base curta origin/develop é ambígua: uma ref local refs/heads/origin/develop vence a remota no rev-parse e no merge-base; usar refs/remotes/origin/develop no hook e no --base
- A4 (recomendado) .githooks/pre-push:241 · o comentário diz que só a suíte inteira anota a árvore verde, mas o caminho so_parecer (classes curtas) também anota, porque mantém completa=1; o comportamento vem de antes, mas o texto deve dizer isso

## Detalhe dos achados
**A1 (bloqueante; requisito E1 "roda só os testes afetados", com gatilho em controle do Forge).** Evidência: `bin/forge-testes:88` mapeia `hooks/.*` para `test_hooks, test_catraca, test_sugerir, test_forge, test_doutor, test_testes_tocados`. Só que `tests/test_agentes_hash_brief.py:18,63` e `tests/test_agentes_clone.py:19,39` executam `hooks/agentes.py` (teto de agentes `R-TETO` e conferência do hash do brief `R-BRIEF`) pelo caminho `HOOKS / "agentes.py"`. Já `tests/test_textos_dono_f10.py:29` lê `hooks/vigia.py`, e `tests/test_conferir_release.py:51-52` copia `bin/forge-changelog` para testá-lo (o mapa da linha 76 só traz `test_changelog` e `test_forge`). Reprodução local: `python3 bin/forge-testes --listar hooks/agentes.py` dá `dirigido (test_catraca, test_doutor, test_forge, test_hooks, test_sugerir, test_testes_tocados)`. Antes, isso era só o plano de iteração do autor. Agora é o que o pre-push roda (`.githooks/pre-push:243-263`). Por que a conferência `MapaCobreOQueOsTestesLeem` não pegou: a expressão em `tests/test_testes_tocados.py:130` só reconhece `RAIZ / "literal"`. Escapam `HOOKS = ...parent.parent / "hooks"`, `ler("...")` e `RAIZ / rel` com variável.
Caminho do problema: não é ataque. É uma regressão num controle do Forge (por exemplo, a conferência do hash do brief em `hooks/agentes.py`) que passa no pre-push verde e chega à branch remota. O CI do PR ainda a barra antes da `develop`, o que limita o impacto. Severidade: média (controle do Forge; o portão final segue de pé).
Correção mínima: (a) em `hooks/.*`, incluir `test_agentes_hash_brief`, `test_agentes_clone` e `test_textos_dono_f10` (ou uma regra mais específica antes, para `hooks/(agentes|_comum)\.py` e `hooks/vigia\.py`). (b) Em `bin/forge-changelog`, incluir `test_conferir_release`. (c) Fazer a conferência reconhecer as outras formas de citar um caminho (`HOOKS / ...`, `ler("...")`, laço `for rel in (...)` com `RAIZ / rel`), para que a família inteira fique coberta e não só estas quatro ocorrências. Esforço: P. Dono: `tech-lead` (autor do lote).
Varredura da família: rodei cada arquivo de `hooks/`, `bin/` e `scripts/` com plano dirigido contra os textos de todos os `tests/test_*.py`. Os únicos que restaram depois de tirar o ruído (nome citado como texto, cópia de semente) são os quatro acima.

**A2 (recomendado).** Evidência: `.githooks/pre-push:253` roda `python3 bin/forge-testes --listar` da árvore da própria branch. Hoje, `ALTERA_O_MAPA` (`bin/forge-testes:110`) põe o próprio script na suíte inteira, e `tests/test_testes_tocados.py:109-112` prova isso. Mas a versão nova do script julga o próprio diff. Para escapar, um erro precisaria de duas edições coordenadas: tirar o nome do conjunto e ajustar o teste. Caminho de ataque realista: nenhum além do que já existe, porque o hook vem do mesmo checkout (`core.hooksPath=.githooks`) e quem edita a branch já pode editar o hook. Por isso é recomendação. Correção mínima: antes do `--listar`, o hook confere por conta própria `git diff --name-only $(git merge-base origin/develop HEAD) HEAD -- bin/forge-testes tests/config.json .githooks/`. Se a saída não for vazia, roda a suíte inteira. Esforço: P. Dono: `tech-lead`.

**A3 (recomendado).** Evidência: `.githooks/pre-push:252-253` e `BASE_PADRAO` em `bin/forge-testes`. Pela ordem de resolução do git, `refs/heads/origin/develop` vem antes de `refs/remotes/origin/develop`. Essa ref só existe por ação local de quem empurra; um push não a cria. Base forjada também conferida: com a base igual ao HEAD, o plano diz "nada alterado", essa saída não casa com o padrão `forge-testes: dirigido (`, e o hook roda a suíte inteira. Uma base antiga só aumenta o diff. Severidade: baixa. Correção mínima: usar `refs/remotes/origin/develop` nas duas chamadas do hook. Esforço: P. Dono: `tech-lead`.

**A4 (recomendado).** Evidência: `.githooks/pre-push:241` e `:293`. No caminho `so_parecer`, `completa` fica em 1 e a árvore é anotada depois das classes curtas, como já acontecia antes do lote. Isso é seguro por indução: a árvore remota já estava verde e o delta só traz pareceres. A frase do comentário, porém, está errada. Correção: ajustar o texto. Esforço: P. Dono: `tech-lead`.

**Conferido sem achado.**
- Os bloqueios de `main`, `homolog` e `develop` e o de envio não fast-forward correm no laço das refs (`.githooks/pre-push:106-132`), antes do filtro. A remoção só de refs e o "nada a enviar" também vêm antes (`:136-147`), e `tests/test_pre_push_afetados.py:127` prova a ordem.
- Caminho sem regra cai na suíte inteira (`planejar`, retorno `sem mapa`), inclusive os nomes que o git cita entre aspas (caractere especial): esses não casam com nenhuma regra.
- O dirigido falha fechado em mais de uma ref, ref que não é branch, HEAD diferente do enviado, árvore suja, script ausente ou link, base ausente e saída diferente de `forge-testes: dirigido (`.
- Quando o dirigido rodou, a árvore verde não é anotada (`completa=0`, `:261` e `:293`); `tests/test_pre_push_afetados.py:72` prova isso. A suíte parcial não alimenta o `so_parecer` seguinte, porque a árvore remota dirigida não entra no arquivo verde e o envio seguinte roda a suíte inteira.
- Se o `--listar` e a execução real divergirem, o efeito é rodar mais testes e sem anotação, o lado conservador.
- O `--listar` roda depois da trava (`R-TETO`).
- Os caminhos da linha de comando (`caminhos_pedidos`) recusam o que sai do repositório. O hook não os usa.
- `R-CUSTO`: nada pago.
- Os achados recorrentes (PA-7, `docs/engineering/achados-recorrentes.md`) estão vazios; nada a conferir.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck` sobre `.githooks/pre-push` (limpo). Rodei `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados` (86 testes, OK) e uma varredura própria do mapa contra os testes (só leitura). Faltaram no PATH, e ficam como lacuna (não instalo nada): `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner`. O diff não traz dependência, segredo nem workflow.
