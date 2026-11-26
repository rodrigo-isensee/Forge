---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: ecb13af6dac68a1f57c173c7000e03bbb5a71054
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E7.52, #888, revalidação por delta, 4ª volta)

Gatilhos: hook de bloqueio (`hooks/_comum.py`: `prazo_vencido`), R-REVIEW, R-CONFORMIDADE, R-QA (mutantes).

## Resumo
- Delta lido: `git diff 4ab16b74..ecb13af6` e `forge-check parecer delta`. São dois commits próprios:
  - o merge `43937681` da develop (`34ab6714`, com o #885). Recalculei o merge automático com `git merge-tree --write-tree` (árvore `e1f01622`). Ele só difere do merge gravado em `docs/hooks-fixtures.md`, o único conflito, resolvido pelo índice regenerado. `tests.test_indice_fixtures` passou (7 testes), com 3590 fixtures em `tests/hooks/`. Os arquivos `hooks/_comum.py`, `hooks/conformidade.py` e `tests/test_hooks.py`, que o `parecer delta` lista no domínio, vêm inteiros de um dos pais: da develop, já revisada no PR de origem, ou do conteúdo da branch aprovado em `4ab16b74`. Nenhuma linha de controle foi escrita no merge;
  - `ecb13af6`: só `tests/mutantes/v0481-prazo-forge.json`, com a isenção de `hooks/_comum.py:2875(base)`.
- Conferi a isenção, e o motivo é verdadeiro. A guarda antiga (`34ab6714:hooks/_comum.py:2873-2876`) libera no `PostToolUse` e libera quando `critico is None and evento != "PreToolUse"`. Logo, ela recusa exatamente quando `evento != "PostToolUse" and (critico is not None or evento == "PreToolUse")`, que é a linha `hooks/_comum.py:2924` (De Morgan). A guarda foi reescrita, não removida. `bin/forge-mutante --cobertura --base 34ab6714 --rev ecb13af6` sai com rc 0: a `:2924` está coberta por `v0481-prazo-forge` M2 e também por `v0480-vigia-agentes-pesado` M1/M2 e `v0480-vigia-trava-critica` M1/M3/M4, e a isenção casa só a linha da base. Rodei `bin/forge-mutante tests/mutantes/v0481-prazo-forge.json --ids M2 --rev ecb13af6` e o resultado foi `M2 · morreu · hooks/_comum.py:2924`. O `--cobertura` resolve o item 3 da catraca da rodada anterior.
- **O que aperta:** nada novo neste delta.
- **O que é neutro:** tudo o que o delta mudou. A isenção só registra uma equivalência provada e não tira teste nem mutante. O índice de fixtures é gerado. O merge não escreve código.
- **O que afrouxa:** nada novo neste delta. O afrouxamento na margem da rodada anterior continua como estava: o prazo contado desde a partida do processo faz as travas de recurso (VIGIA-AGENTES-PESADO, a linha sem marcador crítico) desistirem mais cedo sob carga, e as travas de segurança continuam recusando. O dono aceitou esse afrouxamento em 25/11 às 21:15. Ele não vira risco aceito, porque não há caminho de ataque que libere uma linha crítica.
- **Achados anteriores:** A3, A6 e A7 resolvidos em `4ab16b74`, sem mudança. O cartão da isenção de `:2875(base)` está atendido por `ecb13af6`.
- **CI** (run 45737446078, `pull_request`, no head exato): estão verdes as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `teto de pulados` e `árvore já provada na develop`. Ficaram vermelhos `bateria (pareceres)` e o agregador `bateria`. O motivo é o parecer de review desatualizado pela regeneração de `docs/hooks-fixtures.md`, e os pareceres desta volta resolvem isso. A `catraca` (run 45737445624) falhou só por R-CONFORMIDADE, que pede o rótulo `afrouxa-regra` do dono em `hooks/_comum.py` e `hooks/conformidade.py`. A catraca não acusa mais a guarda apagada.

## Parecer
- ci: ecb13af6dac68a1f57c173c7000e03bbb5a71054 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas: `forge-check parecer delta`, `git diff`, `git merge-tree --write-tree`, `bin/forge-mutante` (`--cobertura` e `--ids M2`), `gh run view --log-failed` e o unittest `tests.test_indice_fixtures`. Não usei nada externo. O delta não traz dependência nem segredo.
