---
tipo: review
contrato: 1
pedido: registro-pareceres-0.27.0
branch: melhoria/registro-pareceres-0.27.0
commit: 960f680644fa82482c419e42af4061fef9153f07
parecer: aprovado
revisor: forge:tech-lead (outra instância, E1.2)
data: 2026-10-21
---
# Review: registro-pareceres-0.27.0

Escopo: a entrega inteira, `341837724182e9012a4fb5a4746d55e24f5ac269..960f680` (4 arquivos, todos adicionados): `docs/reviews/release-0.27.0.md`, `docs/security/release-0.27.0.md`, `docs/devops/release-0.27.0.md` e `changelog.d/registro-pareceres-0.27.0.md`. O revisor não é o autor (E1.1), conforme D-ETAPAS-INST = A.

Veredito sobre `960f680`: **APROVADO**, sem achados bloqueantes.

## Achados

## O que foi conferido
1. **Fidelidade dos pareceres.** `git diff 4727325 960f680 -- docs/reviews/release-0.27.0.md docs/security/release-0.27.0.md docs/devops/release-0.27.0.md` sai vazio (rc=0): os três são byte a byte o estado do commit `4727325` da release. Nenhum parecer foi reescrito.
2. **Escopo do diff.** `git diff --name-status 341837724182e9012a4fb5a4746d55e24f5ac269 960f680`: só os quatro arquivos acima; nenhum código, teste, `CHANGELOG.md` ou `plugin.json` tocado (E1 pede só os pareceres; E2 pede só o fragmento).
3. **Contrato da ADR 0004.** `./bin/forge-check docs` na worktree sai com 0 (rc=0): os frontmatters dos três pareceres são válidos (`tipo`, `contrato`, `pedido`, `branch`, `commit`, `parecer`, `revisor`, `data`). Os três têm `## Achados` com a seção vazia, coerente com `parecer: aprovado`.
4. **Fragmento.** `changelog.d/registro-pareceres-0.27.0.md` usa `### Alterado`, o único tipo que `bin/forge-changelog` aceita para este caso (`TIPOS = Adicionado, Alterado, Corrigido`). Nome segue `<branch-sem-prefixo>.md`. A escolha do tipo é correta, não é desvio do brief.
5. **Neutralidade (`R-NEUTRO`).** `python3 -m unittest discover -s tests -k neutr -v`: 4 testes OK, incluindo `Neutralidade.test_sem_termos_de_projeto`. O commit `4727325` já tinha tirado o termo de stack do parecer de devops, e a cópia atual não o reintroduz.
6. **Commit (checklist item 9).** Conventional Commits em português (`docs(pareceres): ...`), imperativo, corpo explica o motivo e cita a decisão do dono de 2026-10-21. Um commit só, coerente.
7. **Regras da fábrica.** `R-FLUXO`: a branch parte da `develop` no Base-sha do brief. `R-CUSTO`: zero custo, sem rede. `R-VERIFY`: nenhum `--no-verify`/`--force`. `R-REVIEW`: este parecer é de instância que não escreveu o conteúdo revisado.
8. **Regras "ferramenta" da prática do projeto.** Não se aplicam: a fábrica não tem `docs/engineering/praticas.md` com regras de ferramenta para docs. A suíte completa roda no pre-push do envio (`R-VERIFY`).

## Recomendações (não bloqueiam)
- R1 · A descrição do PR de registro (na 0.28.0) deve dizer que a release 0.27.0 não tem `docs/qa/release-0.27.0.md` por decisão do dono (B, 2026-10-21), para que o registro não pareça QA feito. Hoje a ausência só existe no pedido.
- R2 · O parecer de review da release (`docs/reviews/release-0.27.0.md`, achado R1 do próprio parecer) aponta para `b3b165c`, que só existe na branch remota `melhoria/forge-check-lote` (`git cat-file -t b3b165c` ok; `git ls-remote` confirma). Este registro não resolve isso: a branch não deve ser apagada antes de o re-review ser levado à `develop` ou o sha ser registrado no pedido do lote. Registrar o risco na descrição do PR.
- R3 · O fragmento não termina em ponto final, como o padrão dos demais fragmentos da 0.27.0. Cosmético; não mexer no commit por isso.
