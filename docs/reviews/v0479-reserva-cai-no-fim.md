---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: 0998e8ab569bf2d5eff92324dc3811365d179ba6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E60.6 (RESERVA-NAO-CAI-NO-FIM, revalidação no head 0998e8ab)

Revalidação pelo delta `50e06ac6..0998e8ab` (`forge-check parecer delta`): no domínio, `hooks/agentes.py` (1294-1295), `tests/mutantes/v0479-reserva-cai-no-fim.json` (M4 reescrito, M6 a M12 novos) e `tests/test_agentes_interrompidos.py` (seis testes novos). O resto do parecer anterior (head 50e06ac6) segue valendo.

## Parecer
Aprovado. O A1 está resolvido: as guardas de 1210, 1266 e 1269 ganharam M8, M9 e M10, cada uma com teste do ramo de falha. O A2 também: `if uso:` (1294) tem o M11 e o filtro do fim (1384) tem o M12.

A mudança de 1295 corrige uma ordem errada. Antes, `in (uso, None)` deixava a reserva antiga, sem `tool_use_id`, competir com a do próprio disparo. Como o desempate é pelo tipo e pela mais antiga, ela podia ganhar. Agora a reserva do próprio disparo vem primeiro, e a antiga só entra quando ela não existe. Com o `tool_use_id` provado e sem nenhuma das duas, `par` fica None e a reserva de outro disparo não casa. O teste `test_reserva_do_proprio_disparo_vem_antes_da_antiga_sem_tool_use_id` prova esse caso, e o M7 (a forma antiga) morre nele. O `a.get("escrita", [])` em `presas` só torna o auxiliar do teste tolerante à reserva sem branch.

Ferramentas: `bin/forge-mutante --processos 1` da spec deu de M1 a M12 mortos (o M2 não existe na spec). `forge-mutante --cobertura --base 50e06ac6` mostrou só 1295 como coberta (M4, M6 e M7), sem linha `sem mutante`. Rodaram aqui as duas suítes do item (`tests.test_agentes_interrompidos` e `tests.test_hooks_agentes_autor`): 49 testes OK. A suíte inteira fica no CI do PR.
