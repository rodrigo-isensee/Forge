---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-anexos
commit: de63ff10d81d574f47bfa12365fcde7e2df9d319
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: registro de bug do QA como anexo do portão na volta (v0478 E62.1, E62.3, revalidação E62.7)

Revalidação por delta (`R-REVIEW`): `forge-check parecer delta` de `df0aef74..de63ff10`. No domínio: `bin/forge-check` (só a docstring de `bug_do_qa_na_volta`, `:3109-3115`) e `docs/hooks.md:55`. Fora do domínio: `changelog.d/v0479-entrega-anexos.md` e os pareceres de review, QA e segurança. A rodada anterior (parecer aprovado em `66c73710`, sobre `df0aef74`) fica no git e não é recopiada.

Gatilhos: controle do Forge (`bin/forge-check entrega`, barreira de papel do hook `conformidade`), afrouxa-regra com condição do dono (DECISÃO DO DONO 2026-11-20 17:29, item 2).

## Detalhe

**Achados anteriores.** O A1 (recomendado), `docs/hooks.md:55` e docstring de `bin/forge-check:3108`, está **corrigido** em `de63ff10`. `docs/hooks.md:55` ganhou a frase "Limite (A1 da segurança, v0478 E62.3)". Ela diz que o hook confere só o caminho escrito no comando e que `git apply` de patch gravado fora, `git update-index --cacheinfo` e `git cherry-pick` levam arquivo de `docs/qa/bugs/` e das pastas de parecer ao commit de qualquer papel. A frase também aponta o cartão CONFORMIDADE-ESCRITA-NO-INDICE (trilha E63). A docstring em `bin/forge-check:3112-3114` registra o mesmo resíduo, as mesmas três rotas e o mesmo cartão. As três rotas são as que sondei na rodada anterior. O texto não promete mais do que o hook entrega.

**Código.** O diff de `bin/forge-check` muda só a docstring. Nenhuma linha executável mudou, e `ast.parse` do arquivo passa. A lógica aprovada em `df0aef74` segue igual, e o veredito e as provas dela continuam valendo.

**Suíte.** A suíte inteira roda no CI do PR, que o brief não abre. O delta é só texto, então não há teste novo de abuso para rodar. O CI verde continua sendo condição de merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. O resíduo do A1 está documentado e vai para o cartão CONFORMIDADE-ESCRITA-NO-INDICE (E63). Ferramentas: `forge-check parecer delta`, leitura do diff e `ast.parse`. `gitleaks` e o SAST não estão no PATH (lacuna). O delta não traz segredo nem dependência.
