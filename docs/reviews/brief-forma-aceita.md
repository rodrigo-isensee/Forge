---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/brief-forma-aceita
commit: 93225dfda6dea43f5004deaaa6ec3001b3edd30f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review: versao-035, E7 BRIEF-FORMA-ACEITA

Etapa E2.4 (outra instância; não implementei o E7). Diff lido: `d9b26bb3e6b11e7d45c8b7ed81c7da7a8a325503...93225dfda6dea43f5004deaaa6ec3001b3edd30f`, dois commits: e0b4fa0 (`bin/forge-check` e `tests/test_brief_forma_aceita.py`) e 93225df (só `changelog.d/brief-forma-aceita.md`). Lidos: a seção `## E7.` do desenho (`docs/arquitetura/versao-035-desenho.md`) e a linha do Histórico de 15:32 do pedido.

## Teto (M14) e forma
- `bin/forge-check` +8, `tests/test_brief_forma_aceita.py` +67: 75 linhas contadas, abaixo de 150. Um comportamento só. Não toca `hooks/` nem caminho de `PROTEGIDOS`. O teto do desenho (30 no script, 70 no teste) foi respeitado.
- O fragmento em `changelog.d/` está presente. `R-NEUTRO` e `R-CUSTO`: sem efeito. Sem gatilho de segurança (desenho, E7), então não há parecer do `security-engineer` a citar.
- Os commits seguem Conventional Commits, em português, e cada um é coerente.

## Testes rodados (só os tocados, D-5)
`python3 -m unittest test_brief_forma_aceita -v` (de `tests/`): 4 testes, OK. O `bin/forge-testes` com `tests/test_etapa_do_brief.py` junto passou do teto de 540 s e foi encerrado sem resultado, então não conta como prova. Os três pontos do desenho estão cobertos: (a) a seção aparece com cada forma; (b) ela não aparece no review; (c) cada forma de commit passa pelo hook `conformidade` como `forge:tech-lead`, com um controle que prova que o hook está de pé (`--no-verify` dá 2). A forma heredoc da constante é a K3 da ADR 0011 (`"$(cat <<'EOF'⏎…⏎EOF⏎)"` como valor de `-m`), copiada do ADR e não de memória.

## Defeito provado: a seção nova entra no `## Pronto quando` e cria uma reprovação no `forge-check brief`
`secoes_por` (`bin/forge-check:4584`) só abre uma seção nova num cabeçalho de `SECOES_BRIEF`. `## Formas aceitas pelos hooks` não é um deles, então as linhas da seção viram linhas do `Pronto quando`. Como elas contêm a palavra `commit`, `conferir_brief` (`bin/forge-check:5297-5299`) passa a exigir um PQ do conferente. Prova com dois briefs iguais, gerados pelo `brief gerar` desta branch e preenchidos, com um único `PQ-1 (cmd)` de verificador autor e um `Entregar` sem a palavra commit; a única diferença entre eles é a seção nova:
- sem a seção: `forma: ok`
- com a seção: `forma: sem PQ que o conferente confira` (reprova)

O cartão existe para tirar rodadas de conferência reprovadas por forma. A oferta não pode criar uma razão nova de reprovar, e o desenho diz "Nada de checagem nova no conferente" (E7, item 3). A correção é do autor. Caminhos possíveis: o leitor de seções fechar a seção corrente em qualquer `## ` fora de `SECOES_BRIEF`, ou a seção sair antes do `## Pronto quando`, num lugar que não alimente checagem. Em qualquer caso, com um teste que gera o brief, o preenche e confere `forma: ok` com e sem a seção.

## Achados do conferente de 15:32
- Linha do merge duplicada com o `pq_de_merge` nas etapas de merge: confirmada (`bin/forge-check:5965` e `:5969` emitem o mesmo `git merge-base --is-ancestor <mergeCommit> origin/<base>`). Não quebra nada provado. Recomendação: nas etapas de `ETAPAS_DE_MERGE`, a seção traz só as formas de commit, porque o PQ do merge já vem pronto.
- Constante `FORMAS_DE_COMMIT` sem o merge, quando o desenho pede `FORMAS_ACEITAS` com as três formas: é um desvio de forma do desenho, sem defeito. O merge ficou numa f-string na linha 5969, e o teste (a) o cobre. Recomendação: uma constante só, como no desenho, para a oferta ter uma fonte única.
- Nome do teste (`test_brief_forma_aceita.py`, contra `test_brief_formas_aceitas.py` no desenho) e a forma heredoc num bloco cercado em vez de "linha pronta de PQ": divergências de forma sem efeito no comportamento, que seguem o brief da implementação. Não devolvem.

## Achados
- A1 (bloqueante) bin/forge-check:5967 · a seção nova não é cabeçalho de SECOES_BRIEF, entra no Pronto quando pelo secoes_por e a palavra commit nela faz o forge-check brief reprovar com sem PQ que o conferente confira um brief que passava; o desenho do E7 veda checagem nova
- A2 (recomendado) bin/forge-check:5969 · nas etapas de merge a linha do merge repete o PQ que o pq_de_merge já emitiu na linha 5965; ofertar ali só as formas de commit
- A3 (recomendado) bin/forge-check:4567 · a constante FORMAS_DE_COMMIT não traz o merge, que ficou numa f-string; o desenho pede FORMAS_ACEITAS como fonte única das três formas
- A4 (recomendado) tests/test_brief_forma_aceita.py:34 · o teste do review não afirma rc 0 do gerar; um gerar que falhe também passa no assertNotIn

## Parecer
Reprovado por A1. É um defeito provado: a oferta das formas cria uma reprovação nova no `forge-check brief`, o contrário do que o cartão quer. O resto está correto e dentro do teto: as formas batem com a ADR 0011 e com o hook, e o teste (c) mantém a oferta presa ao hook. A volta é o A1, com o teste de conferência. A2 a A4 são recomendações e não devolvem.
