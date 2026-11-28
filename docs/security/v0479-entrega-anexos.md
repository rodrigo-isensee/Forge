---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-anexos
commit: 260e39c72536dc858766cccc6c8417173166cdc2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: registro de bug do QA como anexo do portão na volta (v0478 E62.1, revalidação E62.29)

Esta é uma revalidação por delta (`R-REVIEW`) sobre o parecer aprovado em `0fc3623e`. A rodada anterior fica no git. Li o `forge-check parecer delta` de `0fc3623e..260e39c7`. O head mudou só pelo merge da develop `8caa7f3d` (#756, #758, #762 e #763), que resolveu conflitos em `docs/hooks.md` e `docs/hooks-fixtures.md`. Arquivos no domínio: `bin/forge-check` e `docs/hooks.md`. Fora do domínio: `docs/hooks-fixtures.md`.

Gatilhos: controle do Forge (`bin/forge-check entrega`, barreira de papel do hook `conformidade`) e afrouxa-regra com condição do dono (DECISÃO DO DONO 2026-11-20 17:29, item 2).

## Detalhe

**Delta lido.** O delta de `bin/forge-check` é o subcomando `comparar` (AE7.1). Ele veio todo da develop, pelo #763, que tem revisão própria, e não foi revisado de novo aqui.

Separei o que é da branch com `git diff origin/develop HEAD`. As linhas `+`/`-` da branch no head são iguais às da branch em `0fc3623e` contra a base `c8e8a08d`. A única diferença é a contagem do índice de fixtures, além dos pareceres. Não mudaram:
- `BUGS_DO_QA` e `bug_do_qa_na_volta`;
- o ramo em `linhas_de_entrega`;
- o teste e os mutantes;
- as quatro fixtures `pp-sessao-forge-wt-*-qa-bugs-*`;
- o fragmento do changelog.

**Resolução do conflito** (`git show --cc 260e39c7`):
- `docs/hooks.md`: o item "Pastas de parecer na sessão do Forge" fica com o texto da branch, que traz o trecho de `docs/qa/bugs/` e a frase "Limite (A1 da segurança, v0478 E62.3)". Os três itens novos da develop ficam intactos: CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS, CONFORMIDADE-ESCRITA-NO-INDICE e CONFORMIDADE-SUBSTITUICAO-NO-PROJETO. Contra a develop, o arquivo difere só nesse item.
- `docs/hooks-fixtures.md`: foi regenerado. O total passou a 3372 fixtures (3368 + 4), com `conformidade` em 2541 e `pp-*` em 42. `scripts/indice-fixtures.py --conferir` dá `em dia`.

**Condições do anexo `docs/qa/bugs/`.** Seguem as mesmas do parecer aprovado. A barreira de papel continua em `hooks/conformidade.json:73`, e o limite A1 continua documentado.

**Suíte.** Rodei `python3 -m unittest tests.test_selo_e_entrega.BugDoQaNaVolta`: 10 testes, OK. A suíte inteira roda no CI do PR #745. Na hora da leitura, ela estava `pending`. `bateria (pareceres)` e `catraca` estavam `fail`, porque os pareceres ainda apontavam para `0fc3623e`. O merge depende do CI verde.

## Riscos aceitos e ferramentas
Este parecer não aceita nenhum risco. O resíduo do A1 segue no cartão CONFORMIDADE-ESCRITA-NO-INDICE (E63).

Ferramentas usadas: `forge-check parecer delta`, `git diff`, `git show --cc`, `scripts/indice-fixtures.py --conferir` e `unittest` da classe `BugDoQaNaVolta`. `gitleaks` e o SAST não estão no PATH, e essa lacuna fica registrada. O delta não traz segredo nem dependência.
