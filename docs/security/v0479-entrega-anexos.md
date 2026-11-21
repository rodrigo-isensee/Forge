---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-anexos
commit: 0fc3623eb2aa597b6829350aa07266a3ae1c8a00
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: registro de bug do QA como anexo do portão na volta (v0478 E62.1, revalidação E62.25)

Esta é uma revalidação por delta (`R-REVIEW`). Li o `forge-check parecer delta` de `de63ff10..0fc3623e`. O head mudou pelo merge da develop `c8e8a08d` (#752 e #755), que resolveu o conflito com o #752. Arquivos no domínio: `bin/forge-check` e `docs/hooks.md`. Fora do domínio: `docs/hooks-fixtures.md` e `tests/test_selo_e_entrega.py`. A rodada anterior (aprovado em `de63ff10`) fica no git e não é recopiada.

Gatilhos: controle do Forge (`bin/forge-check entrega`, barreira de papel do hook `conformidade`) e afrouxa-regra com condição do dono (DECISÃO DO DONO 2026-11-20 17:29, item 2).

## Detalhe

**Delta lido.** O delta inclui o código do #752 que veio da base: `vindos_do_remoto_da_base`, `conferido_mais_novo`, `vale_pelo_conferido` e a correção de `remoto_da_branch`. Esse código já tem parecer próprio (`docs/security/v0479-entrega-merges.md`, E62.21, aprovado) e não foi revisado de novo aqui. O que a branch muda em relação à develop (`git diff c8e8a08d 0fc3623e`) é o mesmo que foi aprovado em `de63ff10`:
- `BUGS_DO_QA` e `bug_do_qa_na_volta`, em `bin/forge-check:3146-3160`.
- O ramo do `linhas_de_entrega`, em `bin/forge-check:3385-3387`.
- `docs/hooks.md:55`.
- O fragmento do changelog.

Comparei as linhas `+`/`-` desse diff com o diff da branch em `de63ff10` e elas são iguais, fora a linha da ajuda. `docs/hooks.md` e o fragmento têm o mesmo patch-id antes e depois do merge.

**Resolução do conflito.** Na ajuda de `bin/forge-check:112`, a resolução usa o texto da develop (ENTREGA-MERGE-DA-DEVELOP e ENTREGA-MERGE-DE-PARECER-ANINHADO) e acrescenta, no fim, a frase do E62.1. Nenhuma frase das duas fontes se perdeu (`git show --cc 0fc3623e`). A classe `BugDoQaNaVolta` de `tests/test_selo_e_entrega.py:1874` é a mesma de `de63ff10`; mudou só a posição no arquivo. A `MergeDeParecerAninhado` (`:1990`) veio da develop.

**Condições do anexo `docs/qa/bugs/`.** Todas continuam no head:
- Todo commit do intervalo que muda o arquivo muda só `docs/qa/`, ou é merge sem resolução à mão (`commit_so_de_parecer`).
- Com o qa-engineer autor da volta, ou sem autor lido, o anexo só vale com o blob do último `parecer conferido` (falha fechada, E50.6).
- O caminho que passa por `com_controle` fica de fora.
- A barreira de papel continua em `hooks/conformidade.json:73`: `docs/qa/` só para o `qa`, com a subpasta pelo prefixo. As quatro fixtures `pp-sessao-forge-wt-*-qa-bugs-*` continuam no corpus.
- O limite A1 (escrita pelo índice do git, cartão CONFORMIDADE-ESCRITA-NO-INDICE, trilha E63) continua documentado em `docs/hooks.md:55` e na docstring `bin/forge-check:3150-3153`.

O autor não gravou em nenhuma pasta de parecer: o merge `0fc3623e` traz `docs/qa/`, `docs/reviews/` e `docs/security/` só pelos pareceres já commitados pelos portões.

**Suíte.** Rodei `python3 -m unittest tests.test_selo_e_entrega.BugDoQaNaVolta`: 10 testes, OK. Rodei também `MergeDeParecerAninhado`: 10 testes, OK. `ast.parse` de `bin/forge-check` passa. A suíte inteira roda no CI do PR #745, que estava pendente na leitura (`gh pr checks 745`). O CI verde é condição de merge.

## Riscos aceitos e ferramentas
Este parecer não aceita nenhum risco. O resíduo do A1 segue no cartão CONFORMIDADE-ESCRITA-NO-INDICE (E63).

Ferramentas usadas: `forge-check parecer delta`, `git diff`, `git show --cc`, `git patch-id`, `ast.parse` e `unittest` das duas classes. `gitleaks` e o SAST não estão no PATH; essa lacuna fica registrada. O delta não traz segredo nem dependência.
