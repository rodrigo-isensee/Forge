---
tipo: qa
contrato: 1
pedido: conferente-c2c3
branch: melhoria/conferente-c2c3
commit: a2cb36d03c266fcfd3bbb643bcb900ecb64ae25a
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: conferente-c2c3 (CONFERENTE-VELOCIDADE-REV, E3.1)

## Achados
- A1 (bloqueante) bin/forge-check:4293 · A fiação do comando do pr em `avaliar_brief` (`linhas += linha_do_comando_pr(texto)`) não tem teste: mutante que a remove sobrevive; os testes chamam só a função, nenhum roda `forge-check brief` e vê a linha `etapa: comando forge-check pr ...`.
- A2 (bloqueante) bin/forge-check:4176 · A fiação do bloco idêntico em `conferir_brief` (`saida += blocos_identicos(...)`) não tem teste: mutante que a remove sobrevive (C3 só provado na função, não no `forge-check brief --anterior`).
- A3 (bloqueante) bin/forge-check:619 · Guardas sem teste, mutante sobrevive: uso_do_pr com branch só em origin/ (620) e regex do id (619); base não validada no comando impresso (4278); bloco ausente no anterior marcado idêntico (4177). Cada uma precisa de teste que falhe sem ela.
- A4 (recomendado) bin/forge-check:622 · Mutante que lê o pedido só da raiz do worktree (sem `raiz_principal`) sobrevive; teste com o pedido só na cópia principal.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C2 comando do pr com slug sem `melhoria/` | ComandoDoPr (função) | etapa fora de pr/merge, branch `a;b` | passou na função; fiação sem teste (A1) |
| C2 id do pedido recusado rc=2 | RecusaDoIdDoPedido (3 casos, CLI) | slug sem pedido, branch homônima local | passou; branch remota e regex sem teste (A3) |
| C3 bloco idêntico da volta | VoltaIdentica (função) | bloco alterado | passou na função; fiação sem teste (A2) |
| C3 rótulo do verificador ok | VerificadorOk | cmd do conferente e do autor | passou; Q5 equivalente (o rótulo só tem 2 valores) |
| C1 `--desde` em pr/merge | Entrega (5 testes em test_volta_por_delta) | sem `--desde` = branch inteira, `--desde` inválido, merge da base no intervalo | passou, 5/5 mutantes mortos |
| Ato de PR/merge não mudou | diff + `forge-check pr x --desde` | `--desde` só existe em `entrega` | passou (ver abaixo) |

## Cenários e resultado real
- Módulos tocados: `python3 -m unittest tests.test_etapa_do_brief tests.test_volta_por_delta tests.test_conferencia_base_dono tests.test_forge`: `Ran 552 tests in 150.392s OK`.
- `bin/forge-mutante tests/mutantes/conferente-c2c3.json`: C1, C2, C3, C4 morreram, rc=0.
- `bin/forge-mutante tests/mutantes/conferente-c1.json`: C1 a C5 morreram, rc=0.
- Conferência da lista contra o diff (linhas de guarda sem mutante), 11 mutantes meus em `$TMPDIR/qa-engineer-conferente-c2c3/` (qa-a.json, qb.json): morreram Q3 (filtro de etapa), Q8 (comando sem --base), Q11 (rc=2 no CLI); sobreviveram Q1, Q2, Q4, Q6, Q7 (guardas de uso_do_pr, base, bloco ausente), Q9 e Q10 (fiação no brief) e Q5 (equivalente).
- Ato de PR e merge: `git diff -U0` não toca `cmd_pr`, `ETAPAS_DE_MERGE` (934, 1318, 4699) nem a checagem de checks/merge; só `cmd_entrega` perdeu o recuo de `--desde`. `forge-check pr x --desde <sha>` sai `unrecognized arguments`: o ato não aceita `--desde`.
- Vermelho antes do verde: não rodei `forge-testes --vermelho` (fora do escopo do brief: sem suíte completa); a prova do vermelho é a mutação acima (cada C morto = teste que falha sem o comportamento), exceto A1, A2 e A3.
- Bugs de comportamento abertos: nenhum (`docs/qa/bugs/` não alterado).
