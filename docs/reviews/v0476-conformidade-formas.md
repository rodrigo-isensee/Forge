---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-conformidade-formas
commit: 391011df0cac676754564741cc370fb38c656ec9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.95, item E3.50)

Escopo: diff `3d8ad440..eb18768b` (um commit, `fix(hooks)`), 68 linhas de código e teste em `bin/`, `hooks/` e `tests/*.py`, abaixo do teto de M14; uma classe de comportamento em `hooks/` (texto das recusas), com corpus próprio (10 fixtures `e350-*`).

## O que foi conferido
- **Nada mais frouxo que a ADR 0011.** A decisão do hook não muda: o diff de `hooks/conformidade.py` e `hooks/_comum.py` toca só o texto do `Corrigir:` (`forma_aceita`, `nao_modelada`, `gramatica_de_leitura`, recusa do `<<` não provado) e a constante `FORMA_DO_HEREDOC`. Prova: as 10 fixtures `e350-*` rodadas contra o hook da base (`origin/develop`, 3d8ad440) dão o mesmo código de saída; as 5 de liberação passam na base e as 5 de recusa recusam na base, só com o texto antigo. A forma do heredoc citada (`<<'EOF'` ou `<<'FIM'`, sem `-`, linha de fim igual) é mais estreita que o item 2 da ADR (que aceita também aspas duplas), nunca mais larga.
- **Texto único do heredoc.** `FORMA_DO_HEREDOC` em `hooks/_comum.py` é citada pela recusa do `<<` não provado, pela recusa de `heredoc` com ação crítica e pelo rótulo do brief (`forma_do_heredoc()` em `bin/forge-check`, lida do hook só quando o brief traz as formas). O teste `test_brief_traz_a_forma_do_heredoc_do_hook` compara com a constante importada, não com o texto da fonte.
- **Laço da skill `esperar-estado`.** Sem `$log`, com o caminho literal nas três vezes; `fim=rc=<n>` quando há a linha, `fim=teto` e código 1 sem ela, também com o log ausente (`test -f` evita o 2 do `grep`). A fixture `e350-laco-do-log-da-skill-com-caminho-literal-libera` prova que passa com `.forge/` no caminho, e a `e350-laco-do-log-com-variavel-bloqueia` que o laço antigo segue recusado. Os mutantes do PN5 foram reescritos para o texto novo e seguem morrendo. Nenhuma outra cópia do laço antigo no repositório (`grep` por `log=<log>` e `fim=$(grep`).
- **Guardas e mutantes.** As quatro condições novas (`achado.startswith("$")`, `achado == "heredoc"`, `sinal == "$"`, `"\n" not in cmd`) e as duas da skill têm um mutante cada em `tests/mutantes/v0476-conformidade-formas.json`; `forge-mutante --cobertura --base 3d8ad440` lista as três do hook cobertas; `forge-mutante` no head: M1 a M6 morreram, e PN5 M1 a M5 morreram.
- **Suíte:** sem PR nesta etapa, não há CI a citar; rodei os módulos do item no head (`tests.test_hooks.Hooks.test_fixtures_do_e350`, `tests.test_brief_forma_aceita`, `tests.test_esperar_estado`): 34 testes, OK. O teste de fixtures afirma um mínimo de 10 itens.

## Achados
- A1 (recomendado) hooks/conformidade.py:1905 · Recusa por `$` no papel só de leitura perdeu a forma aceita quando o `$` não é variável: `grep -n fim$ docs/a.md` diz só "caminho literal no lugar da variável"; a base dizia "sinais só entre aspas simples", o que passa. Sugestão: "valor literal ou $ entre aspas simples".
- A2 (recomendado) hooks/conformidade.py:821 · Com `${{` entre aspas duplas o achado é `${` e a recusa diz "valor literal no lugar de ${", que não nomeia variável; a segunda parte (aspas simples) resolve. Sugestão: no ramo de `${`, citar só a forma entre aspas simples.

## Sondas

## Revalidação no head b4bd700e (E3.145)
Delta lido: `forge-check parecer delta docs/reviews/v0476-conformidade-formas.md`, intervalo `eb18768b..b4bd700e`.
- `skills/esperar-estado/SKILL.md` e `skills/esperar-estado/envio-longo.md` (commit b4bd700e, E3.139): o laço do log e a linha de código seguem iguais; só o porquê do caminho literal e o caso do `bin/forge-fechar --espera` passam ao arquivo de apoio, com ponteiro na skill e sem perder regra. `tests.test_esperar_estado` e `tests.test_metricas_texto`: 17 testes, OK.
- `bin/forge-check` no delta: as linhas mudadas são todas do #646 (E3.49), vindas da `develop` pelos merges 0d61a5e0 e 08b94cbf; a mudança própria da branch em `bin/forge-check` (desde 9db0705e) é idêntica à revisada em eb18768b (desde 3d8ad440). Nada novo a revisar.
- Delta sem guarda nova; a `catraca` acusa só o rótulo `afrouxa-regra` pelos arquivos de controle já tocados (`R-CONFORMIDADE`), nenhuma guarda sem mutante.
- A1 e A2 seguem abertos (o delta não toca `hooks/`), recomendados.

## Revalidação no head 391011df (E3.189)
Delta lido: `forge-check parecer delta docs/reviews/v0476-conformidade-formas.md`, intervalo `b4bd700e..391011df`, sem o que veio da base.
- Merge 57a8cc8c (`origin/develop` f8e9c377): `git merge-tree --write-tree` dos dois pais dá a mesma árvore do merge (diff vazio), sem resolução à mão. `bin/forge-check`, `hooks/conformidade.py` e `tests/test_hooks.py` aparecem no delta porque os dois lados os tocaram; o lado da branch é idêntico ao aprovado em b4bd700e. Nada novo a revisar.
- `docs/hooks-fixtures.md` (391011df): gerado, soma as 10 fixtures `e350-*` (2913 para 2923; `conformidade` 2146 para 2156). `tests.test_indice_fixtures`: 7 testes, OK. `test_fixtures_do_e350` e `test_fixtures_do_v0474_tag` (este vindo da base) no head: 2 testes, OK; o `test_hooks` inteiro fica com o CI do PR.
- `catraca --base origin/develop`: só o rótulo `afrouxa-regra` pelos arquivos de controle (`R-CONFORMIDADE`), nenhuma guarda sem mutante.
- A1 e A2 seguem abertos, recomendados; só a linha mudou com o merge.

## Parecer
Aprovado. O item faz o que E3.50 pede: cada recusa por construção não modelada diz a forma aceita, o heredoc tem um texto só citado pelo hook e pelo brief, e o laço da skill passa no hook sem variável de caminho. A decisão do hook é idêntica à da base (fixtures da E3.50 rodadas nas duas versões), então nada fica mais frouxo que a ADR 0011 e não cabe rótulo `afrouxa-regra`. Os dois achados são de texto de mensagem, sem efeito na decisão do hook, e não devolvem (`R-REVIEW`).
