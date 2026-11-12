---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-mutacao-bench
commit: 135b20d23a95d5ade9e358e6abb0126f63db930c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E7.10, melhoria/v046-mutacao-bench)

Revalidação por delta da E7.6 (aprovada no `e452582f`) depois da correção E7.9. Instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v046-mutacao-bench.md`, intervalo `e452582f..135b20d2`, no domínio `agents/qa-engineer.md`, `agents/tech-lead.md`, `bin/forge-mutante`, `changelog.d/v046-mutacao-bench.md`, `skills/qa-testing/SKILL.md`, `tests/mutantes/v046-mutacao-bench-3.json`, `tests/mutantes/v046-mutacao-bench.json`, `tests/test_forge_mutante.py`.

## Achados
- A1 (bloqueante) agents/qa-engineer.md:20 · o commit 135b20d2 estoura o orçamento de instrução: `test_orcamento_instrucao` falha (qa-engineer agente_caracteres 4175 > 3962, total 22044 > 21480, marcadores 49 > 45; tech-lead, linhas 26 e 42: 8875 > 8615, 29965 > 29861, 58 > 56). Em e452582f passa. Enxugue o texto; subir o teto é afrouxar.
- A2 (bloqueante) skills/qa-testing/SKILL.md:97 · a linha nova estoura `test_metricas_texto` (caracteres 12121 > 11761, frase_media_x10 194 > 192, linhas_longas 31 > 30); em e452582f passa. Encurte a frase ou troque por uma citação curta, sem subir a linha de base.
- A3 (recomendado) bin/forge-mutante:829 · a variável local `apoio` em `dirigir` sombreia o módulo global `apoio` (linha 92, `forge_apoio_testes`); hoje não quebra, porque `dirigir` não usa `apoio.` depois da linha 829, mas um uso futuro quebraria. Sugestão: `apoio_mudado`.

## Parecer
Reprovado pelos A1 e A2: o commit de texto 135b20d2 deixa vermelhos dois testes que o CI do PR roda, e o merge exige CI verde. O código da correção está certo e não volta.

Conferido e sem achado:
- O A4 da segurança (E7.7) está corrigido: `apoio_de_teste` (bin/forge-mutante:806) pega o arquivo de `tests/` fora de `test_*.py` e de `tests/mutantes/` e põe todos os mutantes no diff, com a linha `apoio de teste no diff:`. A sonda S2 virou `test_helper_de_tests_enfraquecido_poe_todos_os_mutantes_no_diff` (rc 1, `M1 · sobreviveu`, sem `fora do diff`), e o ramo contrário tem `test_teste_e_spec_de_outro_mutante_nao_poem_todos_no_diff`.
- Guardas do delta: `forge-mutante --cobertura --base e452582f --rev 135b20d2` sai rc 0, com `coberta` nas linhas 810 (M18, M19, M20), 830 (M16) e 835 (M17, M5). O `de` do M5 foi atualizado, e cada `de` das três specs (M1 a M20) aparece uma vez só na fonte (AR-12). Não refaço a mutação.
- Nenhum `tests/*.py` importa outro `test_*.py`, então a exclusão de `test_*.py` não deixa helper de fora hoje.
- O A1 da E7.6 (citação da `--base` e do bench por versão) foi atendido no conteúdo, em skills/qa-testing/SKILL.md:97, agents/qa-engineer.md:20 e agents/tech-lead.md:26 e 42; o que falta é caber no orçamento (A1 e A2).
- Decisão do dono de 11:06: placar e bench seguem por versão, e nada do delta entra no CI do PR. `test_forge_mutante`: 75 s antes e 70 s depois, segundo o autor; aqui deu 84 s, 110 testes, OK.
- Testes, um por vez (R-TETO): `bin/forge-testes tests/test_forge_mutante.py` e os 27 módulos de texto que `bin/forge-testes --listar` aponta para agents/ e skills/. 26 OK; `test_metricas_texto` e `test_orcamento_instrucao` falham (A1, A2). A suíte inteira fica no CI.
- Tamanho: o delta tem 45 linhas de código e teste (bin e tests/*.py; a spec fica fora da conta).
- Commits do delta: dois, Conventional Commits em português, um comportamento cada.
