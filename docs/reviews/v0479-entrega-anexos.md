---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-anexos
commit: de63ff10d81d574f47bfa12365fcde7e2df9d319
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E62.2 (melhoria/v0479-entrega-anexos)

Escopo: o diff `d4f0b10a..df0aef74` (Base-sha do brief até o Revisar-sha), dois commits do E62.1: `06bbe4b6` (o `bug_do_qa_na_volta` e o ramo novo em `linhas_de_entrega`, o teste e o mutante) e `df0aef74` (quatro fixtures `pp-sessao-forge-*` de `docs/qa/bugs/`, índice e `docs/hooks.md`).

## Requisito
DECISÃO DO DONO (2026-11-20 17:29), item 2: na conferência da entrega, `docs/qa/bugs/` vira anexo do portão de QA, como os pareceres, com a mesma barreira de papel (só o QA grava ali). O que entrou:
- `bin/forge-check:3105-3117`: o registro de bug vale na volta (`valido`, a conferida ou o Revisar-sha) quando todo commit do intervalo que o muda só muda `docs/qa/` ou é merge sem resolução à mão (o mesmo `commit_so_de_parecer` do E50.1). Com o qa-engineer autor da volta, ou sem autor lido, vale só com o blob do último `parecer conferido` (falha fechada, como o E50.6).
- `bin/forge-check:3337-3339`: o ramo vem depois do E50.1 e só para `docs/qa/bugs/`. O `docs/qa/` sem frontmatter fora de `bugs/` segue fora, e há teste disso.
- Barreira de papel: o código do hook não muda; a regra de `docs/qa/` já cobria a subpasta pelo prefixo. As fixtures novas provam isso na sessão do Forge em `wt/*`: dev pelo Bash, tech-lead pelo Write e segurança pelo Edit bloqueiam; o qa pelo Write libera.
- Nada além do pedido. Fragmento `changelog.d/v0479-entrega-anexos.md` presente; `docs/hooks.md` e a ajuda do `forge-check` atualizados.

## Leitura (checklist)
- Tamanho (H1): cerca de 18 linhas de código, dentro do teto, e um comportamento só.
- Mudanças nas guardas e mutantes: as linhas mudadas `3114`, `3117` e `3337` têm M1 a M5 declarados, e o `forge-mutante --cobertura --base d4f0b10a` deixa as três cobertas. O ramo de falha de cada uma tem teste de comportamento: o autor no commit do código, o commit com arquivo fora de `docs/qa/`, o merge resolvido à mão, a entrega sem conferida, o qa autor da volta e o rev-list que falha ou vem vazio.
- O falso de `git` em `test_rev_list_que_falha_ou_vazio_recusa` casa o nome exato do arquivo (`args[-1] == self.REL`), não um prefixo (item 12).
- `test_fixtures_do_parecer_pelo_papel` seleciona as fixtures pela `descricao` e afirma um mínimo; as quatro fixtures novas entram nesse lote (item 11).
- Commits em Conventional Commits, em português, com o ID da etapa.
- `R-MAIN`, `R-VERIFY`, `R-NEUTRO`: nada tocado.

## Ferramentas (cito a saída, sem refazer)
- `python3 -m unittest tests.test_selo_e_entrega.BugDoQaNaVolta`: `Ran 10 tests ... OK`.
- `bin/forge-mutante --processos 1 tests/mutantes/v0479-entrega-anexos.json`: M1 a M5 `morreu`.
- `bin/forge-mutante --cobertura --base d4f0b10a…`: `coberta` em 3114, 3117 e 3337.
- `python3 -m unittest -k test_fixtures_do_parecer_pelo_papel tests.test_hooks`: OK. `scripts/indice-fixtures.py --conferir`: `em dia`.
- Suíte inteira: não rodei aqui (brief: sem suíte local). Ela roda no CI do PR, que ainda não existe; o merge depende dele.

## Revalidação E62.6 (head de63ff10)
Delta lido: `forge-check parecer delta docs/reviews/v0479-entrega-anexos.md`, intervalo `df0aef74..de63ff10`, no domínio só `bin/forge-check` (docstring de `bug_do_qa_na_volta`, 2 linhas), `changelog.d/v0479-entrega-anexos.md` e `docs/hooks.md`. Volta só de texto: registra o limite do hook (só o caminho escrito no comando; `git apply`, `git update-index --cacheinfo`, `git cherry-pick`) apontado no A1 da segurança e o cartão CONFORMIDADE-ESCRITA-NO-INDICE. Nenhuma guarda nem comportamento muda; `ast.parse` do `bin/forge-check` sem erro. O texto bate com o A1 da segurança e não amplia o escopo. Os achados A1 e A2 abaixo seguem como estavam.

## Achados
- A1 (recomendado) bin/forge-check:3117 · Remoção do registro num commit só de docs/qa/ sai como anexo com o rótulo "commitado", sem teste. A barreira do hook segura o autor: sonda S1 abaixo. Sugestão: teste do caso e rótulo próprio para a remoção.
- A2 (recomendado) tests/mutantes/v0479-entrega-anexos.json:10 · M1 troca startswith por tipo=="qa" e valido por valido or base_sha num mutante só; nem cada condição sozinha nem o not com_controle(nome) da linha 3337 têm prova própria. Sugestão: um mutante por condição.

## Sondas

## Parecer
Aprovado no head `de63ff10` (revalidado pelo delta de texto sobre o aprovado em `df0aef74`). O item faz o que o item 2 da decisão do dono pede: espelha o E50.1 e o E50.6 sem o frontmatter, que o registro de bug não tem. A barreira de papel é a do hook, e as fixtures a provam na sessão do Forge.

Sonda de A1, que não bloqueia: com um repositório temporário, `fc.bug_do_qa_na_volta(r, de, "HEAD", "docs/qa/bugs/x.md", {"node-backend"}, {})` devolveu `True` depois de um commit só com `git rm docs/qa/bugs/x.md`. No hook, a fixture `pp-sessao-forge-wt-dev-redireciona-qa-bugs-bloqueia` com o comando trocado por `rm docs/qa/bugs/x-01.md` e depois por `git rm -q docs/qa/bugs/x-01.md` deu as duas vezes código 2 (`parecer de QA é do qa: docs/qa/`). A remoção tem, então, a mesma barreira da escrita, como a decisão manda. Os dois achados são recomendados e viram cartão depois do merge.
