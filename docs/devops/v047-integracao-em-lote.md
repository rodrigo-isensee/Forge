---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-integracao-em-lote
commit: 13cb874d23ef51f505f3dfcb3248c78c6ffea22c
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-14
---
# Review de devops: v047 (integracao-em-lote, E1.266)

## Achados

## Detalhes
Sem achados. O A1 do review anterior (commit c6b0b788) está resolvido.
- A1 resolvido (R-FLUXO): o passo "Nada pula degrau" (ci.yml:508-519) chama `tests/catraca.py --modo degrau`, da cópia da develop do servidor, com a tabela única PROMOCOES. Simulado: promocao/0.47.1 -> homolog com head na develop rc=0; develop -> homolog e homolog -> main rc=0; feature/x -> homolog, develop -> main, promocao/1.2.3-rc -> homolog e head de fork rc=1.
- Workflow: entradas do PR (HEAD_REF, HEAD_SHA, HEAD_REPO) vão por `env`, nunca interpoladas em `run:`; o código executado é o da develop (não o do autor); o job tem `contents: read` e `fetch-depth: 0`, então `origin/develop` existe. Em arvore-testada, o par do PR vem da mesma tabela e o job continua em falha fechada.
- bin/forge-fechar: `--item-de-lote` só com FORGE_FECHAR_LOTE_PAI igual ao `$PPID`; o CI acompanhado no lote é o do topo da develop no servidor, com aviso se a leitura falha; P5 descarta PR de fork (`isCrossRepository`); `par_de_promocao` consulta a tabela antes de criar o ramo.
- R-MAIN: nada escreve na main. R-VERIFY: sem `--force`, `--no-verify` nem check pulado. R-CONFORMIDADE: nenhuma proteção, ruleset ou segredo alterado. R-CUSTO: nenhum runner, serviço ou artefato novo.
- Ferramentas: `shellcheck bin/forge-fechar` rc=0; `python3 -m py_compile scripts/arvore-testada.py` ok. `actionlint` ausente do PATH (lacuna; o CI roda actionlint e zizmor no job bateria).
- Aviso ao tech-lead: `.github/workflows/ci.yml` é arquivo protegido; o PR pede o rótulo `afrouxa-regra` do dono se a catraca o exigir. O token do bot não tem o escopo `workflow`: o envio do ci.yml é do dono.

## Custo e rollback
Sem minutos de CI nem recursos novos (`R-CUSTO`); um `git worktree add` a mais por PR de promoção. Volta: `git revert` dos commits na develop; a tabela PROMOCOES volta junto.
