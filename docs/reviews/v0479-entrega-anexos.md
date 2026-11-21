---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-anexos
commit: 260e39c72536dc858766cccc6c8417173166cdc2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
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

## Revalidação E62.26 (head 0fc3623e)
Delta lido: `forge-check parecer delta docs/reviews/v0479-entrega-anexos.md`, intervalo `de63ff10..582e800a`. No domínio entram `bin/forge-check`, `docs/hooks-fixtures.md`, `docs/hooks.md` e `tests/test_selo_e_entrega.py`. O head mudou só pelo merge `0fc3623e` da develop (`c8e8a08d`, com o #752). Separei o que é da branch pelo `git diff c8e8a08d HEAD` e comparei linha a linha com o diff aprovado `d4f0b10a..de63ff10`: a parte da branch é igual à aprovada, salvo o contexto.
- A ajuda da `entrega` é a linha da develop (ENTREGA-MERGE-DA-DEVELOP e ENTREGA-MERGE-DE-PARECER-ANINHADO, do #752) com a frase do E62.1 no fim: os dois textos ficam.
- `bug_do_qa_na_volta` e o ramo em `linhas_de_entrega` não mudaram, só de lugar: agora `bin/forge-check:3149-3160` e `:3385`.
- `tests/test_selo_e_entrega.py`: +116/-0 sobre a develop. A classe `BugDoQaNaVolta` está intacta, e as classes do #752 vêm da base sem resolução à mão.
- Índice de fixtures: de 3199 para 3203 (+4, as mesmas quatro `pp-sessao-forge-*`). `scripts/indice-fixtures.py --conferir` dá `em dia`.
- O resto do delta (`vale_pelo_conferido`, `conferido_mais_novo`, `vindos_do_remoto_da_base`) é do #752. Já foi revisado no PR dele e fica fora deste parecer.
- `unittest discover -s tests -p test_selo_e_entrega.py -k BugDoQaNaVolta`: `Ran 10 tests ... OK` no head.
- CI do PR #745 no head `582e800a`: bateria e instalação `pass`, partes da suíte em andamento. O merge depende dele.

Os achados A1 e A2 seguem, com as linhas atualizadas.

## Revalidação E62.30 (head 260e39c7)
Delta lido: `forge-check parecer delta docs/reviews/v0479-entrega-anexos.md`, intervalo `0fc3623e..260e39c7`. No domínio entram `bin/forge-check`, `docs/hooks.md` e `docs/hooks-fixtures.md`. O head mudou só pelo merge `260e39c7` da develop (`8caa7f3d`, com o #758, o #762 e o #763), com conflito resolvido em `docs/hooks.md` e o índice regenerado. Separei a branch com `git diff origin/develop HEAD` (origin/develop = `8caa7f3d`) e comparei as linhas `+`/`-` com `git diff c8e8a08d 0fc3623e` (a parte aprovada): iguais em `bin/forge-check`, `docs/hooks.md`, `tests/test_selo_e_entrega.py`, `tests/mutantes/v0479-entrega-anexos.json` e no fragmento do changelog; as quatro fixtures `pp-sessao-forge-*-qa-bugs-*` são as mesmas.
- `bin/forge-check`: o subcomando `comparar` do delta é do #763 (some no diff contra a develop) e fica fora deste parecer.
- `docs/hooks.md`: a resolução manteve a linha PARECER-PELO-PAPEL da branch (a subpasta `docs/qa/bugs/` e o limite do A1 da segurança) e as linhas CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS, escrita no índice e substituição da develop intactas.
- Índice: 3368 da develop mais as 4 da branch, 3372. `scripts/indice-fixtures.py --conferir`: `em dia`. `unittest discover -s tests -p test_indice_fixtures.py`: `Ran 7 tests ... OK`; `-p test_reval_delta.py`: `Ran 10 tests ... OK`.
- CI do PR #745 no head `260e39c7`: `catraca` falha por `R-CONFORMIDADE: mudança em bin/forge-check`, que pede o rótulo `afrouxa-regra` do dono depois do último push (ADR 0008), não por defeito; `bateria (pareceres)` falha com o run em andamento (pareceres no head anterior, que os portões renovam); suíte pendente. O merge depende do CI verde e do rótulo.

## Achados
- A1 (recomendado) bin/forge-check:3160 · Remoção do registro num commit só de docs/qa/ sai como anexo com o rótulo "commitado", sem teste. A barreira do hook segura o autor: sonda S1 abaixo. Sugestão: teste do caso e rótulo próprio para a remoção.
- A2 (recomendado) tests/mutantes/v0479-entrega-anexos.json:10 · M1 troca startswith por tipo=="qa" e valido por valido or base_sha num mutante só; nem cada condição sozinha nem o not com_controle(nome) da linha 3385 têm prova própria. Sugestão: um mutante por condição.

## Sondas
- S1 · `bug_do_qa_na_volta` num repositório temporário, commit só com `git rm docs/qa/bugs/x.md`, autor `node-backend` · espera: remoção com prova própria · obtido: `True`, com o rótulo "commitado"
- S2 · fixture `pp-sessao-forge-wt-dev-redireciona-qa-bugs-bloqueia` com `rm docs/qa/bugs/x-01.md` e com `git rm -q docs/qa/bugs/x-01.md` · espera: código 2 · obtido: código 2 nas duas (`parecer de QA é do qa: docs/qa/`)

## Parecer
Aprovado no head `260e39c7`, revalidado pelo delta do merge da develop sobre o aprovado em `0fc3623e`, que revalidou o merge anterior sobre `de63ff10` (que já tinha sido revalidado pelo delta de texto sobre `df0aef74`). O item faz o que o item 2 da decisão do dono pede: espelha o E50.1 e o E50.6 sem o frontmatter, que o registro de bug não tem. A barreira de papel é a do hook, e as fixtures a provam na sessão do Forge.

Sonda de A1, que não bloqueia: com um repositório temporário, `fc.bug_do_qa_na_volta(r, de, "HEAD", "docs/qa/bugs/x.md", {"node-backend"}, {})` devolveu `True` depois de um commit só com `git rm docs/qa/bugs/x.md`. No hook, a fixture `pp-sessao-forge-wt-dev-redireciona-qa-bugs-bloqueia` com o comando trocado por `rm docs/qa/bugs/x-01.md` e depois por `git rm -q docs/qa/bugs/x-01.md` deu as duas vezes código 2 (`parecer de QA é do qa: docs/qa/`). A remoção tem, então, a mesma barreira da escrita, como a decisão manda. Os dois achados são recomendados e viram cartão depois do merge.
