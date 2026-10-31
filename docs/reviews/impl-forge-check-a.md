---
tipo: review
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a1
commit: 992139162c02ddd8b7303752b2c9e0f46f898e12
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-forge-check-a (branch a1)

Diff lido na rodada 1: `234dbe0..0ba0a57` (1844275 C1, d4eea24 C2, 0ba0a57 fragmento). Rodada 2: delta `0ba0a57..48e2c5d` (`bin/forge-check:983-984`, `tests/test_forge.py:4846-4853`).
Revalidação (rodada 3): `forge-check delta --parecer` sobre o parecer anterior, intervalo `48e2c5d..9921391`; li só o que ele listou: `tests/mutantes/impl-forge-check-a.json:1-147` (+147, 9921391) e `tests/test_forge.py:4924-4930` (+7, b6187cd). Já lido e não relido: C1, C2, o fragmento, a guarda de `mesmo_pedido` e os pareceres de segurança e QA (cito, não refaço).

## Item entregue
E1 e E2 do pedido (FC-ENTREGA-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO, FC-PEDIDO-CAMINHO-DUPLO). A volta 2 responde ao QA: b6187cd é o teste do A1 do QA (pedido relativo só na raiz de brief) e 9921391 é a spec de mutantes do A2 do QA, 10 mutantes, M3 declarado equivalente.

## M14 (agents/tech-lead.md:19)
Cumpre. `git diff --numstat --no-renames origin/develop...HEAD`: `bin/forge-check` 39+7 e `tests/test_forge.py` 101+2, 149 linhas de código e teste, abaixo de 150; `tests/mutantes/` é corpus e fica fora, assim como pareceres e fragmento. Um comportamento só (a leitura do caminho do Pedido), sem `hooks/`. Sem exceção a pedir.

## Verificação (saída das ferramentas)
- `python3 -m unittest tests.test_forge.EntregasParalelas tests.test_forge.CaminhoDoPedido` no head: `Ran 17 tests`, `OK`.
- `bin/forge-mutante tests/mutantes/impl-forge-check-a.json` no head: M1, M2 e M4 a M10 `morreu`; M3 `equivalente`. O M5 (antes M13 do QA, `bin/forge-check:802`) agora morre: o teste de b6187cd fecha o A1 do QA.
- `bin/forge-mutante --cobertura --base 234dbe0`: 797 `só equivalente` (M3), 988 `sem mutante` (`valor.startswith('~/')`, embora o M8 declare a linha 988 e morra), o resto `coberta`.
- M3 não é equivalente, provado por execução: com o mutante aplicado, `caminho_do_pedido(repo, "q")` com `q` existindo no diretório corrente devolve `repo/docs/pedidos/q.md` em vez de `q`, e `docs/pedidos/p.md` existente no diretório corrente passa a ser o da raiz. A guarda `arquivo_existe(dado)` mantém o contrato que a base já tinha (`Path(pedido).is_file()` primeiro) e nenhum teste a trava.
- Shell: nenhum no diff. Segurança: `docs/security/impl-forge-check-a.md` (security-engineer); QA: `docs/qa/impl-forge-check-a.md`.

## Achados
- A1 (recomendado) bin/forge-check:983 · resolvido em 48e2c5d (guarda de valor vazio) com o teste em tests/test_forge.py:4846; segue fechado.
- A2 (bloqueante) tests/mutantes/impl-forge-check-a.json:46 · M3 declarado equivalente sem ser: tirar arquivo_existe(dado) de bin/forge-check:797 muda o retorno para caminho que existe no diretório corrente (q vira repo/docs/pedidos/q.md). Escrever o teste que o mata e tirar o equivalente.
- A3 (recomendado) bin/forge-check:988 · forge-mutante --cobertura acusa sem mutante em valor.startswith('~/') apesar do M8 declarar a linha e morrer; ajustar o de do M8 para o casamento da ferramenta ou registrar o motivo.

## Parecer
Reprovado no head 9921391 só pelo A2: a spec esconde um mutante vivo atrás de uma justificativa de equivalência que a execução desmente. A correção é um teste (e a retirada do campo `equivalente` do M3), sem mudar código de produção; revalidação por delta.
