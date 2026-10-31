---
tipo: review
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: db6c9de50dcc6c82617c2260987b949b9f630bc5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-forge-check-a (branch a1)

Diff lido na rodada 1: `234dbe0..0ba0a57` (1844275 C1, d4eea24 C2, 0ba0a57 fragmento). Rodada 2: delta `0ba0a57..48e2c5d` (`bin/forge-check:983-984`, `tests/test_forge.py:4846-4853`).
Revalidação (rodada 3): `forge-check delta --parecer` sobre o parecer anterior, intervalo `48e2c5d..9921391`; li só o que ele listou: `tests/mutantes/impl-forge-check-a.json:1-147` (+147, 9921391) e `tests/test_forge.py:4924-4930` (+7, b6187cd). Já lido e não relido: C1, C2, o fragmento, a guarda de `mesmo_pedido` e os pareceres de segurança e QA (cito, não refaço).

Revalidação (rodada 4): `forge-check delta --parecer` sobre o parecer anterior, intervalo `9921391..db6c9de`; li só o que ele listou: `tests/test_forge.py:4909` (+1, d591bcc) e `tests/mutantes/impl-forge-check-a.json:45` (+1 -2, db6c9de). Já lido e não relido: C1, C2, o fragmento, a guarda de `mesmo_pedido`, os testes de b6187cd, o resto da spec e os pareceres de segurança e QA (cito, não refaço).

## Item entregue
E1 e E2 do pedido (FC-ENTREGA-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO-DUPLO). A volta 2 responde ao QA: b6187cd é o teste do A1 do QA (pedido relativo só na raiz de brief) e 9921391 é a spec de mutantes do A2 do QA, 10 mutantes, M3 declarado equivalente.

## M14 (agents/tech-lead.md:19)
Cumpre. `git diff --numstat --no-renames origin/develop...HEAD` no head db6c9de: `bin/forge-check` 39+7 e `tests/test_forge.py` 102+2, 150 linhas de código e teste, no teto (até 150, inclusive); rodada 3: 149 linhas de código e teste, abaixo de 150; `tests/mutantes/` é corpus e fica fora, assim como pareceres e fragmento. Um comportamento só (a leitura do caminho do Pedido), sem `hooks/`. Sem exceção a pedir.

## Verificação (saída das ferramentas, head db6c9de)
- `python3 -m unittest tests.test_forge.EntregasParalelas tests.test_forge.CaminhoDoPedido`: `Ran 17 tests`, `OK`.
- `bin/forge-mutante tests/mutantes/impl-forge-check-a.json`: M1 a M10 `morreu`, nenhum `equivalente` declarado. O M3 (`bin/forge-check:797`) morre pela asserção nova de d591bcc: com o cwd em `home/r`, `docs/pedidos/p.md` existe no cwd e na raiz do repo e o cwd vence, que é o contrato da base (`Path(pedido).is_file()` primeiro). O `os.chdir` do teste volta pelo `addCleanup` do `setUp`.
- `bin/forge-mutante --cobertura --base 234dbe0`: linhas 793 a 802, 983, 985, 989 e 1011 `coberta`; 988 `sem mutante` (`valor.startswith('~/')`), o A3 de antes, recomendado; 980 da base `apagada`.
- Shell: nenhum no diff. Segurança: `docs/security/impl-forge-check-a.md` (security-engineer); QA: `docs/qa/impl-forge-check-a.md` (o último parecer de QA, no head 7f5a1f8, é reprovado e precisa revalidar no head novo; `forge-check pr` o acusa).

## Achados
- A1 (recomendado) bin/forge-check:983 · resolvido em 48e2c5d (guarda de valor vazio) com o teste em tests/test_forge.py:4846; segue fechado.
- A2 (recomendado) tests/mutantes/impl-forge-check-a.json:45 · resolvido em d591bcc (asserção em tests/test_forge.py:4909 que mata o M3) e db6c9de (spec sem o campo equivalente); forge-mutante no head: M3 morreu.
- A3 (recomendado) bin/forge-check:988 · forge-mutante --cobertura acusa sem mutante em valor.startswith('~/') apesar do M8 declarar a linha e morrer; ajustar o de do M8 para o casamento da ferramenta ou registrar o motivo.

## Parecer
Aprovado no head db6c9de. O A2 da rodada 3 está fechado: a spec não declara mais equivalente e os 10 mutantes morrem. O A3 segue como recomendação, sem devolver. M14 cumprida no teto exato (150 linhas, um comportamento, sem `hooks/`).
