---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-prometido
commit: afc7083d568d98634c39a498fef1954cc4f3dc1f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E110.2, MEDIR-DE-NOVO-O-PROMETIDO)

Escopo: `bin/forge-placar propostas` com `prometido: <N>%` na Métrica, o real medido como no `comparar` ao lado, `sem medida` sem janela fechada, fonte ou base; teste novo, peso em `tests/pesos-d4.json`, specs de mutante e fragmento do changelog. Base 900bfdfe, head afc7083d, cerca de 35 linhas de código (H1 dentro do teto).

## Achados
- A1 (bloqueante) bin/forge-placar:593 · R-QA: a catraca (MUTANTES-SPEC-HOOKS) barra as condições das linhas 593 e 594 sem mutante: M7 (`... or True`) e M6 (`fontes = None`) trocam fora do nó da condição. Declare um mutante dentro de cada nó (`forge-mutante --cobertura` sai limpo).
- A2 (recomendado) docs/melhoria-continua.md:17 · o checklist do `forge-placar propostas` descrito aqui e em skills/kanban-metricas/SKILL.md:37 não cita o `prometido: <N>%` nem a linha `prometido:` nova; só a docstring do script diz como declarar.
- A3 (recomendado) bin/forge-placar:592 · o real sai sem o piso de amostra do `comparar` (`--minimo`, rc 3 inconclusivo): com poucas delegações o `real -60%` aparece como medida firme; marcar `amostra pequena` ao lado.

## Sondas
- S1 · python3 -I tests/catraca.py --modo regras --base 900bfdfe --head afc7083d --raiz . · espera: rc 0 · obtido: rc 1, R-QA guarda de bin/forge-placar mudada sem mutante declarado: 593 e 594
- S2 · bin/forge-mutante --cobertura --base 900bfdfe · espera: rc 0, toda condição coberta · obtido: rc 1, sem mutante 593 e 594 (a troca sai do nó da condição, M7 e M6)

## Parecer
Reprovado só por A1: o CI do PR roda a catraca e ela sai rc 1 neste head, então o item não entra assim. A lógica está certa e consistente com o `comparar` (mesmas janelas `[início - dias, início)` e `[início, início + dias)`, mesmo `medir`), as fontes só são lidas quando alguma proposta anuncia ganho, fonte ausente e base zero saem `sem medida` (nunca 0) e a métrica fora do placar não quebra.

Ferramentas citadas, sem refazer: `bin/forge-mutante` nas duas specs, 9 de 9 mortos (M1 a M9); `--conferir --base 900bfdfe`: trechos no lugar; `test_placar_prometido.py` 12 OK e `test_placar*.py` 80 OK no head. Teste com subprocesso limpa o ambiente e chama Python com `-I`. Suíte inteira: fica no CI do PR (ainda não há run nesta branch).

Correção de A1 (do autor): em `tests/mutantes/v0478-placar-prometido.json`, troque M6 e M7 por mutantes que mudem só o texto do nó apontado pela `--cobertura` (o `com` da linha 594 e o `(m := ...)` da 593) e rode `bin/forge-mutante --cobertura --base 900bfdfe24352def4272749213a74baceb69cc21` até rc 0. A2 e A3 viram cartão depois do merge.
