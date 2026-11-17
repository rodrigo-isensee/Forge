---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-estado-ilegivel
commit: a99c1a9fbb88229ad6b5d24dd25d2f664d0309e6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047, lote A (HOOK-ESTADO-ILEGIVEL-LIBERA)

Revalidação por delta `d2d82ffa..a99c1a9f` (pedido v0474, E1.7), pela `forge-check parecer delta`: "nenhum arquivo do domínio mudou". O delta é a junção do próprio remoto da branch (`c5c1792c`, só pareceres) e `a99c1a9f`, que realinha o `de` de M22 e M32 em `tests/mutantes/v047-hook-erro-libera-3.json` e `-4.json` (fora do domínio, lidos). `git diff --quiet d2d82ffa a99c1a9f -- hooks bin scripts .githooks .github` rc 0; a junção da develop no intervalo é a de `5b1aacd5` (ancestral do head), já revalidada na volta `d2d82ffa`. Os dois `de` novos casam uma vez cada em `hooks/agentes.py` (linhas 947 e 961) e mutam a mesma guarda de antes (`if raiz is None` e `if recusa is None`), só com o contexto atualizado (`pasta_ilegivel = False`, `try:`); nenhum alvo de mutante muda de sentido. Histórico: `bc129c11` reprovado (A1 bloqueante, A2 recomendado); `c3f86d7a`, `b09916f7`, `05d68fce` e `d2d82ffa` aprovados; este os substitui.

## Gatilhos
`R-SEGURANCA`: guarda em hook de controle (o teto de agentes, `R-TETO`), com leitura de estado que um agente pode corromper.

## Achados

## Sondas

## Detalhe dos achados
Nenhum achado novo no delta `d2d82ffa..a99c1a9f`. A1 e A2 anteriores seguem resolvidos (texto e sondas S1/S2 na volta `c3f86d7a`, no git); `hooks/agentes.py` é idêntico ao de `d2d82ffa`, então as provas valem.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; não conferi o CI deste head (sem `gh` no ambiente); o portão do PR segue exigindo o CI verde. Nesta volta conferi por script (`python3 -I`) que o `de` de M22 e M32 ocorre uma vez em `hooks/agentes.py`; `bin/forge-mutante` foi recusado pelo R-TETO (tarefa pesada de outra sessão), lacuna que fica com o CI e o QA. Varreduras de segredo e de workflow não se aplicam ao delta (só specs de mutante e pareceres).
