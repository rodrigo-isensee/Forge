---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/trava-agente-morto
commit: f77bb51df14bee2e20a1814f622e37e45427f793
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: TRAVA-AGENTE-MORTO (E23.72)

Classe C, passada única, head f77bb51d (diff a1318e88..f77bb51d). O parecer de segurança do cartão (C1 a C12) não está no head; os critérios foram lidos do docstring de `hooks/agentes.py` e dos nomes das classes de teste (C1 a C11).

## Achados
- A1 (bloqueante) hooks/hooks.json:18 · o gatilho `SendMessage` (a única entrada da C8) não tem teste nem mutante: removido o bloco, `tests.test_trava_agente_morto` fica OK (49) e `test_hooks` só exige `Agent|Task`. A lápide vira letra morta sem nada cair (R-QA, mutante por linha de guarda).
- A2 (recomendado) hooks/conformidade.json:50 · a spec de mutantes só cobre Python; as duas entradas da C10 têm teste (C10 em test_trava_agente_morto:372-389), mas sem mutante declarado; um por entrada fecharia a lista.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1 notificação só do Claude Code (cabeçalho ancorado, status, carimbo, sidechain, tool_result) | C1NotificacaoDoClaudeCode | cabeçalho fora do início, status fora da lista, carimbo fora da forma | passou |
| C2 task-id, tool-use-id e meta.json juntos, depois do `desde` | C2ConfereJuntos | meta ausente/fora da forma, divergência | passou |
| C3 só a sessão atual, sem link | C3SoDaSessaoAtual | sessão fora da forma, link no caminho | passou |
| C4 teto de bytes e de tempo, arquivo regular | C4Orcamento | alvo não regular, além do teto, prazo | passou |
| C5 a C7, C9, C11 liberação, `pesado`, log | classes do mesmo módulo | trava `pesado` vigente, log por link e giro | passou |
| C8 lápide e retomada recusada | C8Lapide (chama o hook direto) | erro na conferência recusa; branches não texto | passou; gatilho em hooks.json sem teste (A1) |
| C10 transcripts e meta protegidos | teste em test_trava_agente_morto:372-389 | memória do projeto segue livre | passou |

## Cenários e resultado real
- Módulo novo no head: `python3 -m unittest tests.test_trava_agente_morto` → `Ran 49 tests ... OK`.
- Vermelho à mão (teste do head copiado sobre a base a1318e88): `Ran 49 tests ... FAILED (failures=5, errors=69)`; as falhas são AttributeError das funções novas e 5 falhas de comportamento.
- Mutantes (um spec por vez, árvore limpa), 26 de 26 `morreu`, rc=0 nas quatro specs. M17, M19 e M22 saem com a nota `(erro) o teste declarado deu erro sob o mutante e passa sem ele`: morreram por erro, não por asserção; aceito, vira recomendação de leitura, não bloqueio.
- `forge-mutante --cobertura --base a1318e88`: 26 `coberta · declarado, não provado`; 2 `isenta` (agentes.py:353 atalho de desempenho; recusas.log, equivalente porque `run()` devolve `_run` já fixado, conferido em `_comum.py`); `não coberto: hooks/conformidade.json` e `hooks/hooks.json`.
- Prova do A1: cópia do head sem o bloco `SendMessage` de hooks.json; `tests.test_trava_agente_morto` → `Ran 49 tests ... OK`.
- `tests.test_hooks` inteiro não coube no prazo local; a bateria é do CI do PR (check-run `bateria` do mesmo sha). Falhas de pid e sessão na base, declaradas pelo autor, não reproduzidas aqui.
- Declarações do autor: C10 mais estreita que a pasta de projetos (confirmado: `memory/` fica livre, testado); teto excedido e docs/hooks.md sem atualização ficam para o review e o tech-lead.

## Para fechar o A1
Teste (do autor, num commit de teste) que lê `hooks/hooks.json` e afirma `SendMessage` entre os matchers de PreToolUse apontando para `agentes.py`, mais um mutante que remova o bloco.
