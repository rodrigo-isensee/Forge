---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.7
branch: melhoria/v0477-release-0477
commit: 55e4db4b0350421bac4f12c1e98ff78ffa3dd94a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: release 0.47.7 (versão inteira)

Escopo: `git diff v0.47.6..55e4db4b`. A tag `v0.47.6` não está no clone; a base usada é a marca da 0.47.6 na develop, `efb25ff7` (#669, `plugin.json` em 0.47.6). São 15 arquivos: defeitos do forge-check #667 (`fd1356b5`), textos de processo #668 (`b1c26396`) e a marca da versão (`55e4db4b`, E3.1). Cada item entrou com os próprios pareceres aprovados; aqui se confere a junção.

Gatilhos: execução de comando git no `bin/forge-check` (`veredito_trocado`, conferência de portão), regra protegida com texto mexido (R-LIMITES, R-CUSTO) e a release usada por todos os projetos.

## Achados

## Sondas

## Detalhe dos achados
Sem achados novos. Junção conferida item a item: o patch mesclado de cada item (fora de `docs/{qa,reviews,security}`, `CHANGELOG.md` e `changelog.d/`) tem o mesmo `git patch-id --stable` que o patch que os três portões aprovaram, desde a base dele:
- Defeitos do forge-check #667: revisado `4603cde8` = mesclado (`9b2cb570`); pareceres de review, QA e segurança `v0477-forge-check-defeitos` aprovados no mesmo sha. O `git grep -l -F -e <sha>` só tira da leitura a versão que não contém o sha revisado, que nunca teria `commit:` igual a ele; a igualdade do frontmatter continua conferida depois; `grep` com código maior que 1 conta como trocado (falha fechada, teste `test_grep_que_falha_conta_como_veredito_trocado`). O sha vai depois de `-e` e as versões vêm do `rev-list`: sem injeção de opção.
- Textos de processo #668: revisado `447a4c8d` = mesclado (`f59eb499`); pareceres `v0477-textos-processo` aprovados. Em R-LIMITES só sai a palavra "também"; o alcance de R-CUSTO (autorização expressa do dono, melhoria vinda de qualquer projeto) fica igual, sem afrouxar. O ponteiro do H8 aponta para `skills/engineering-practices/tamanho-por-item.md:20`, que existe.
- Marca `55e4db4b`: fora do changelog, só `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.7; `CHANGELOG.md` com `[0.47.7] - 2026-11-18` em português e `[Não publicado]` vazio; os dois fragmentos apagados (`changelog.d/` só com o `README.md`), e as 2 entradas da [0.47.7] são os textos deles.

Recomendações abertas que seguem valendo sem recópia (não bloqueiam): `v0477-forge-check-defeitos` A1 (nome de parecer com aspas no `ls-tree`/`grep`, preexistente) e as listadas no parecer `release-0.47.6`.

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. Rodado em `55e4db4b`: `python3 -m unittest tests.test_changelog` (89, OK) e `python3 -m unittest tests.test_selo_e_entrega.ParecerDoPortao` (23, OK). A suíte inteira é do CI do PR (a local falha por ambiente: `/proc` e `gh` no sandbox); o estado do CI no head não foi lido aqui, e a promoção exige o CI verde. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; a versão não toca workflow (`.github/` sem diff).
