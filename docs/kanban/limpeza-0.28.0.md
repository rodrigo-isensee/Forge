# Limpeza das branches remotas mescladas (IMPL-N-REG, E2)

Gerada na E1.1 em 2026-10-22, sobre `origin/develop` em 38c5824. Nada foi apagado.

## Resultado de `git branch -r --merged origin/develop`
Vazio (só a própria `develop`). Os PRs do Forge entram por squash, então nenhuma branch `melhoria/*` é ancestral da `develop`, e o critério literal do pedido (E2) não alcança nenhuma. A E2.1 só pode apagar as branches abaixo com a confirmação do dono ou do Jarvis de que o critério vale por PR mesclado.

## Proposta para a E2.1 (PR mesclado, pareceres já na develop ou neste registro)
Cada uma teve o PR mesclado e os commits posteriores ao head do PR tocam só o parecer registrado aqui (conferido com `git diff --name-only <head do PR> <ponta da branch>`).

| Branch remota | PR | Head do PR | Ponta da branch | Parecer só na branch (registrado aqui) |
|---|---|---|---|---|
| melhoria/conformidade-leitura | 270 | 445e769 | e77dbd0 | docs/qa/conformidade-leitura.md |
| melhoria/forge-check-lote | 252 | b69dbe9 | b3b165c | docs/reviews/forge-check-lote.md |
| melhoria/suite-paralela-d4 | 277 | b578714 | ad65236 | docs/qa/suite-paralela-d4.md |

Apagar só depois do merge deste registro, sem `--force`, uma branch por vez (`git push origin --delete <branch>`).

## Não apagar (fora do escopo)
| Branch remota | Situação |
|---|---|
| melhoria/lote-leitura-hook | sem PR; 36 commits sem equivalente na develop; pareceres de review (reprovado) e segurança (aprovado) só nela |
| melhoria/lote-forge-check-0.28.0 | sem PR; 19 commits sem equivalente; pareceres de review e segurança (aprovado) só nela |
| melhoria/impl-n-fechar-b | sem PR; 7 commits sem equivalente; sem parecer |
| melhoria/impl-n-cat1 | sem PR; 6 commits sem equivalente; sem parecer divergente (a entrega mesclou como impl-n-cat1-2, PR 282) |
| melhoria/ci-...-postinstall (o nome do meio é de uma ferramenta de stack, que a neutralidade barra no núcleo; ver `git branch -r`) | sem PR; 2 commits sem equivalente; sem parecer |
| melhoria/impl-n-doutor, impl-n-fechar-a, impl-n-qa, impl-n-qa2, impl-n-qa3, impl-n-tpl-a | rodadas anteriores (reprovado no review); a entrega mesclou por outra branch (doutor2 283, fechar-a2 284, qa4 285, tpl-a2 286) e a develop já tem o parecer final; commits sem equivalente na develop, só listadas |
