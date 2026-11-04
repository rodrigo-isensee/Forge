# L08-1 - a linha `conferida <sha40>` do Histórico vale mesmo negada ou no meio de outra frase (E7)
- Severidade: baixa
- Responsável sugerido: forge:tech-lead (bin/forge-check, CONFERIDA em :907)
- Ambiente: melhoria/lote-l08 @ 874c89e, python3

## Passos para reproduzir
1. Repositório de teste de `RepoComOrigem` (tests/test_forge.py): branch `melhoria/x` com a entrega c1 e os pareceres em dia.
2. `docs/pedidos/p1.md` com `## Histórico` e a linha `- 2026-11-04 09:00: entrega NÃO conferida <c1>` (ou `- não: entrega conferida <c1>`).
3. `forge-check pr p1 --ref melhoria/x --base develop`.

## Resultado esperado
rc 1 com `conferência: nenhuma linha entrega conferida <sha40> ... cobre o head` (só a linha afirmativa `entrega conferida` cobre o head).

## Resultado obtido
rc 0, `pr: veredito: aprovado`. A expressão `^\s*-\s.*\bconferida ([0-9a-f]{40})\b` (herdada, não mudou no lote) aceita qualquer item do Histórico com `conferida <sha40>`, sem exigir `entrega` antes nem excluir negação. O E7 passou a usá-la como portão.

## Evidência
Reproduzido em sessão do QA (3 variantes; a de sha abreviado e a sem marcador `-` reprovam como esperado). Contorno simples: o Jarvis é quem grava o Histórico. Não bloqueia.
