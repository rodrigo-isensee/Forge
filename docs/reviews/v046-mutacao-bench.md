---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: 203e3554785746c600bd590fddb807d930eaa7a2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E7.14, melhoria/v046-mutacao-bench)

Revalidação por delta da E7.10 (reprovada no `135b20d2` pelos A1 e A2) depois da volta E7.13. Instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v046-mutacao-bench.md`, intervalo `135b20d2..203e3554`, no domínio `agents/qa-engineer.md`, `agents/tech-lead.md`, `bin/forge-mutante`, `skills/qa-testing/SKILL.md`, `tests/mutantes/v046-mutacao-bench-3.json`, `tests/mutantes/v046-mutacao-bench.json`.

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:96 · o enxugamento trocou "k maior só dentro da vez da trava da suíte" por "k > 1 dentro da vez da trava da suíte": sem o "só", a restrição lê como descrição. Sugestão, numa próxima mudança de texto: "k > 1 só dentro da vez da trava".

## Parecer
Aprovado. Os bloqueantes da E7.10 estão resolvidos e o A3 (recomendado) foi atendido.

- A1 da E7.10 (orçamento de instrução): `bin/forge-testes tests/test_orcamento_instrucao.py` OK no 203e3554, sem teto mudado (o delta não toca `tests/`).
- A2 da E7.10 (métricas de texto): `bin/forge-testes tests/test_metricas_texto.py` OK no 203e3554, sem linha de base mudada.
- A3 da E7.10: `apoio` virou `apoio_mudado` em `dirigir` (bin/forge-mutante:829-835); o módulo global `apoio` (linha 92) não é mais sombreado.
- Specs (AR-12): o `de` do M5, M16 e M17 acompanha o nome novo, e cada um casa uma vez só na fonte (`grep -cF` = 1). `forge-mutante --cobertura --base 8b5a44d5` (Base-sha) sai rc 0, com `coberta` em 830 (M16) e 835 (M17, M5). Contra `135b20d2` a saída traz `apagada · bin/forge-mutante:830(base) · apoio` (rc 1): a renomeação não é reconhecida como condição editada; a checagem que vale para o autor é contra o Base-sha. Não refaço a mutação, que é do QA.
- Frases exigidas: comparei os literais de `tests/*.py` e `tests/config.json` contra o texto antes e depois dos três arquivos; nenhuma frase exigida saiu. A única relevante, `bin/forge-mutante tests/mutantes/<pedido>.json`, saiu só de agents/tech-lead.md, e `test_forge_mutante.TextoQueMandaUsarAFerramenta` exige-a apenas na skill e no agente de QA, onde segue (SKILL.md:92, qa-engineer.md:20); o "um mutante por linha de guarda mudada" e o "sem mutante é achado" seguem nos dois.
- Conteúdo: a `--base <head aprovado>` da volta ficou no V2 (agents/tech-lead.md:25) e no agente e na skill de QA; placar e bench seguem por versão (tech-lead.md:41, "medidas, não portão"), fora do CI do PR, como manda a decisão do dono de 11:06.
- Testes, um por vez (R-TETO), no 203e3554: `bin/forge-testes tests/test_forge_mutante.py` OK (122 s), `tests/test_orcamento_instrucao.py` OK, `tests/test_metricas_texto.py` OK. Os 27 módulos do `--listar` são PQ do autor; a suíte inteira fica no CI.
- Tamanho: o delta tem 7 linhas de código e teste (bin/forge-mutante); o resto é texto e spec.
- Commits do delta: três (22b5e4d3, c241921e, 203e3554), Conventional Commits em português, um comportamento cada.
