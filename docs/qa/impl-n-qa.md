---
tipo: qa
contrato: 1
pedido: impl-n-qa
branch: melhoria/impl-n-qa4
commit: 738cfff89e751d0543ff977bde075c0ea45ffe13
parecer: aprovado
revisor: qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-22
---
# QA: impl-n-qa (itens 34, 65 e 36)

Links: `docs/pedidos/impl-n-qa.md`, desenho `docs/propostas/discovery-0.29.0/n-qa.md`, adendo `docs/security/ameacas/n-qa.md`, review `docs/reviews/impl-n-qa.md`, segurança `docs/security/impl-n-qa.md`. Sem UX nem API. Tudo offline, em cópias em `$TMPDIR` (`R-CUSTO`); a worktree compartilhada não foi tocada. Código testado: 738cfff (o HEAD 2161bf8 só soma os pareceres de segurança e review). O commit da EXT-1 está fora do diff, como pedido.

## Achados

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Item 34: `--vermelho` dá prova por teste, saída 0 só com prova e nada caindo no HEAD | `tests.test_testes_tocados` (58 testes) e sondas S-D, S-E | teste novo com produção nova; teste existente com asserção mudada | passou: S-D `prova (API ausente)` rc 0; S-E `prova (asserção)` rc 0 |
| Item 34, borda negativa: import novo em módulo existente, sem teste novo | sonda S-A | teste herdado não prova | passou: `não prova (herdada da base)`, rc 1 |
| Item 34, borda negativa: falha de preparação de classe nova | sonda S-B | idem | passou: rc 1 |
| Item 34, borda negativa: falha de preparação de módulo nova | sonda S-C | idem | passou: rc 1 |
| Item 34: teste que cai no HEAD bloqueia | sonda S-F | regressão | passou: `regressão`, rc 1 |
| Item 34: árvore suja, base ilegível, uso inválido | sondas S-G, S-H | entrada inválida | passou: rc 2 nos três |
| Item 65: `forge-mutante` morre/sobrevive/inválido e nunca "morreu" sem veredito | `tests.test_forge_mutante` (36 testes) | de 0 ou 2 ocorrências, link simbólico, 9 mutantes, prazo, controle vermelho | passou |
| Item 36: matriz da família no texto de segurança | invariantes em `tests/config.json`, no `tests.test_forge` | texto presente | passou |
| Neutralidade, changelog e invariantes | suíte completa | n/a | passou |
| P3 = B: cada commit se reverte sozinho e a suíte que sobra fica verde | reverts em cópia | commits 76670d1, 66fdc39, bd1b485, 738cfff | passou (abaixo) |

## Resultado real
- Suíte completa em cópia limpa de 2161bf8: 1437 testes, OK (skipped=1, o salto é anterior ao diff), 358 s.
- Módulos tocados (`test_testes_tocados`, `test_forge_mutante`): 94 testes OK em 17 s.
- Vermelho antes do verde: `python3 bin/forge-testes --vermelho base --modulos test_testes_tocados,test_forge_mutante` (base = a3dbe22, HEAD = 738cfff): rc 0; contagem `prova (asserção)=34; prova (API ausente)=25; não prova (passa na base)=35`. Os 35 são, em sua maioria, casos negativos (saída 2 de entrada inválida) que passam sem a produção por natureza (amostra conferida em `test_forge_mutante`); os testes de regra do diff têm prova.
- Sondas do item 34 (repositório mínimo, base e topo): S-A, S-B e S-C saem 1 com "nenhum teste prova a mudança" e o teste antigo marcado `não prova (herdada da base)`; S-D e S-E saem 0; S-F sai 1; S-G (árvore suja) e S-H (base inexistente) saem 2.
- P3 = B, `git revert` de cada commit sobre 738cfff, sem conflito, e rodados `test_forge`, `test_changelog` e os módulos que sobram: sem o 76670d1, 506 OK; sem o 66fdc39, 511 OK (o módulo do item some junto, como decidido em 10:38); sem o bd1b485, 541 OK; sem o 738cfff, 541 OK.
- Mutação: o diff não traz spec declarada (`tests/mutantes/`); o QA escreveu 8 mutantes sobre as guardas do diff e rodou `bin/forge-mutante`: M2 (árvore suja), M4 (sem veredito sai 2), M5 (link simbólico), M7 (erro de carga não é "morreu") e M8 (controle vermelho) morreram; M1 (herança só da classe) deu inválido (erro de execução no módulo, não conta como morto); M3 e M6 sobreviveram (abaixo).

## Recomendações (não bloqueiam)
- M6 sobrevive: trocar a guarda "trecho exatamente uma vez" por "ao menos uma" não derruba teste, porque o caso de duas ocorrências do teste usa um trecho cuja troca quebra a sintaxe e cai em "inválido" por outro caminho. Falta um caso com duas ocorrências e troca válida. `bin/forge-mutante` não é portão.
- M3 sobrevive: nenhum teste ponta a ponta cobre "base do módulo ilegível" (só a unidade de `da_base` com `TodosExistiam`). Fecha o mesmo vão da R8.
- R8 (média) e R9 (baixa) da segurança: de acordo, viram cartão próprio já registrado no pedido; a R8 é falha aberta (herança vinda de outro módulo conta como teste novo), reproduzida pela segurança, não repetida aqui.
- Saída 1 de `--vermelho` com `não prova (passa na base)` listado nos módulos modificados: legível, mas longa; sem ação.

Sem bugs abertos; nada em `docs/qa/bugs/`.
