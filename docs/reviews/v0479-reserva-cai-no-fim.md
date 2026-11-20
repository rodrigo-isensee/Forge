---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: 50e06ac60ee54707c6a089a2b6e9a261fd649150
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E60.2 (RESERVA-NAO-CAI-NO-FIM, head 50e06ac6)

Diff `ed5bfa02...50e06ac6`: `hooks/agentes.py` (+37/-5, dentro do H1), teste novo `FimDoAgente`, spec `tests/mutantes/v0479-reserva-cai-no-fim.json` e M13 do H2 acompanhando a linha nova.

## Achados
- A1 (bloqueante) hooks/agentes.py:1210 · guardas de forma do diff (1210 tool_use_id do disparo, 1266 forma do aid antes do meta, 1269 forma do toolUseId do meta) sem mutante declarado nem teste do ramo de falha: o mutante que tira cada uma sobrevive (S1 a S3; R-REVIEW, qa-testing 'Mutantes declarados')
- A2 (recomendado) hooks/agentes.py:1294 · `if uso:` e o filtro de 1386 sem mutante declarado; o `if True` em 1294 morre na suíte do item, só falta a linha na spec (`forge-mutante --cobertura`)

## Sondas
- S1 · hooks/agentes.py:1210 `if isinstance(uso, str) and USO_DE_AGENTE.fullmatch(uso)` trocado por `if True` · espera: teste vermelho · obtido: tests.test_agentes_interrompidos e tests.test_hooks_agentes_autor OK (43 testes)
- S2 · hooks/agentes.py:1266 `if real and isinstance(aid, str) and ID_DE_AGENTE.fullmatch(aid)` trocado por `if real` · espera: teste vermelho · obtido: as duas suítes do item OK
- S3 · hooks/agentes.py:1269 `if isinstance(uso, str) and USO_DE_AGENTE.fullmatch(uso)` trocado por `if True` · espera: teste vermelho · obtido: as duas suítes do item OK

## Parecer
Reprovado só pelo A1. A lógica está certa: o disparo grava o `tool_use_id` (1257), o início filtra as reservas pelo `toolUseId` do meta (1293-1295) e o fim solta o que `e_do_agente` prova (1384-1386). Sem prova dos dois lados, volta o casamento por id de antes. A reserva de `SendMessage` (749) não tem `tool_use_id` e por isso cai pelo id, sem regressão.

Ferramentas: `bin/forge-mutante` da spec nova deu M1, M3, M4 e M5 mortos, e o M13 do H2 morreu na linha nova (1384). `forge-mutante --cobertura --base ed5bfa02` listou `sem mutante` em 1210, 1266, 1269, 1294, 1383 e 1386. A 1383 (`if aid`) gera mutante equivalente, porque `uso_do_agente(hook, None)` já devolve None, e não entra nos achados. A suíte inteira fica no CI do PR. Aqui rodaram só as duas suítes do item, verdes.

Correção do A1: declare um mutante por guarda (1210, 1266, 1269) e escreva para cada uma um teste de comportamento do ramo de falha. Exemplos: um `tool_use_id` fora da forma não entra na reserva, um `agent_id` fora da forma não lê o meta, e um `toolUseId` fora da forma no meta deixa o casamento pelo id. Na volta, rode `--cobertura --base 50e06ac6`.
