---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s3-registro
commit: d03cc57f22b83532dccb1a96acb43cb76ed6578a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E39.7 (BP3 S3, registro de interrompidos no hook agentes)

Base `004ce869`, head revisado `d03cc57f`, um commit (`feat(agentes)`, E39.3). Diff de código: `hooks/agentes.py` (+116 −9, abaixo do teto H1), um comportamento: a reserva guarda `briefs` (caminho e sha256) e o registro de sessão provadamente morta vai para `interrompidos` em vez de sumir.

## Achados
- A1 (recomendado) hooks/agentes.py:1299 · `caidos_da_sessao` refaz `sessao_morta` (novo `os.kill`) sobre a lista crua, depois do `vigentes` da linha 1295: o pid que morre entre as duas leituras fica nos agentes e no interrompidos, e volta duplicado no evento seguinte. Derivar os caídos da mesma avaliação do `vigentes`.

## Sondas

## Parecer
Aprovado. Lido o diff inteiro contra o escopo do E39.3:

- Faz o pedido e só ele: nenhuma recusa do R-TETO ou do R-BRIEF muda; a única guarda nova de recusa é `interrompidos` não-lista em `ler_estado` (linha 430), que segue a regra já existente do estado ilegível (HOOK-ESTADO-ILEGIVEL-LIBERA) e o docstring do topo foi atualizado.
- `briefs_da_reserva` grava só o trecho `docs/briefs/<nome>.md` de caracteres seguros e o hash dos bytes lidos; nada do prompt entra (teste `test_nenhum_byte_do_prompt_entra_no_registro`). `interrompido` copia só campos de forma conhecida, sem PID.
- Ordem de gravação coerente: com liberação, o estado com `interrompidos` sai antes da recusa e os vencidos vão ao `liberacoes.log` uma vez só (`vencidos = []`); sem gravação, nada é logado e o evento seguinte recalcula. `fechar_por_relancamento(…, agentes[-1])` só roda depois do `lancar`, que sempre reserva ou sai.
- `dentro_do_prazo` extraído do `vigentes` sem mudar a condição (M25, M26 mortos).
- A1 é corrida de microssegundos com efeito só cosmético (item duplicado, fechado pela mesma regra); não bloqueia (`R-REVIEW`).

Verificadores (rodados no head `d03cc57f`, só o módulo tocado; suíte inteira fica no CI do PR):
- `python3 -m unittest test_agentes_interrompidos` (em `tests/`): `Ran 23 tests … OK`.
- `bin/forge-mutante --cobertura --base 004ce869…`: todas as guardas do diff `coberta`, nenhuma descoberta.
- `bin/forge-mutante tests/mutantes/v0479-bp3-s3-registro.json` e `-2.json`: M1 a M29 `morreu` (M15, M25 a M29 por erro do teste declarado com controle verde, que conta como morto pela ferramenta).
