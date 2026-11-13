---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/trava-agente-morto
commit: 31f2e643e22c22ceedcf927a07c4cf5676032ed4
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: TRAVA-AGENTE-MORTO (E23.72)

Classe C, passada única, head f77bb51d (diff a1318e88..f77bb51d). O parecer de segurança do cartão (C1 a C12) não está no head; os critérios foram lidos do docstring de `hooks/agentes.py` e dos nomes das classes de teste (C1 a C11).

## Achados
- A5 (recomendado) hooks/hooks.json:19 · a checagem --cobertura do forge-mutante lista hooks.json e conformidade.json como não coberto (só lê Python); M28 a M32 cobrem à mão. Resolvidos: A1 e A2 anteriores. Nenhum bloqueante aberto.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1 notificação só do Claude Code (cabeçalho ancorado, status, carimbo, sidechain, tool_result) | C1NotificacaoDoClaudeCode | cabeçalho fora do início, status fora da lista, carimbo fora da forma | passou |
| C2 task-id, tool-use-id e meta.json juntos, depois do `desde` | C2ConfereJuntos | meta ausente/fora da forma, divergência | passou |
| C3 só a sessão atual, sem link | C3SoDaSessaoAtual | sessão fora da forma, link no caminho | passou |
| C4 teto de bytes e de tempo, arquivo regular | C4Orcamento | alvo não regular, além do teto, prazo | passou |
| C5 a C7, C9, C11 liberação, `pesado`, log | classes do mesmo módulo | trava `pesado` vigente, log por link e giro | passou |
| C8 lápide e retomada recusada | C8Lapide (chama o hook direto) | erro na conferência recusa; branches não texto | passou; gatilho em hooks.json com teste e M28 |
| C10 transcripts, meta, pastas de projeto e de sessão protegidos | teste da C10 em test_trava_agente_morto, 4 fixtures `home-claude-projects-*`, M29 a M32 | memória do projeto segue livre; mv/rm da pasta; pasta forjada | passou |

## Cenários e resultado real
- Módulo novo no head: `python3 -m unittest tests.test_trava_agente_morto` → `Ran 49 tests ... OK`.
- Vermelho à mão (teste do head copiado sobre a base a1318e88): `Ran 49 tests ... FAILED (failures=5, errors=69)`; as falhas são AttributeError das funções novas e 5 falhas de comportamento.
- Mutantes (um spec por vez, árvore limpa), 26 de 26 `morreu`, rc=0 nas quatro specs. M17, M19 e M22 saem com a nota `(erro) o teste declarado deu erro sob o mutante e passa sem ele`: morreram por erro, não por asserção; aceito, vira recomendação de leitura, não bloqueio.
- `forge-mutante --cobertura --base a1318e88`: 26 `coberta · declarado, não provado`; 2 `isenta` (agentes.py:353 atalho de desempenho; recusas.log, equivalente porque `run()` devolve `_run` já fixado, conferido em `_comum.py`); `não coberto: hooks/conformidade.json` e `hooks/hooks.json`.
- Prova do A1: cópia do head sem o bloco `SendMessage` de hooks.json; `tests.test_trava_agente_morto` → `Ran 49 tests ... OK`.
- `tests.test_hooks` inteiro não coube no prazo local; a bateria é do CI do PR (check-run `bateria` do mesmo sha). Falhas de pid e sessão na base, declaradas pelo autor, não reproduzidas aqui.
- Declarações do autor: C10 mais estreita que a pasta de projetos (confirmado: `memory/` fica livre, testado); teto excedido e docs/hooks.md sem atualização ficam para o review e o tech-lead.

## Revalidação por delta (E23.100), f77bb51d..31f2e643 (head da branch 6861a9de só soma o parecer do review)
`forge-check parecer delta` listou no domínio: bin/forge-testes, docs/hooks.md, hooks/agentes.py, hooks/conformidade.json, 4 fixtures, specs de mutantes -4 e -5, tests/test_trava_agente_morto.py. Retestado:
- `python3 -m unittest tests.test_trava_agente_morto` → `Ran 51 tests ... OK` (eram 49; +2: gatilho do hooks.json e C8Gatilho).
- `bin/forge-mutante tests/mutantes/trava-agente-morto-4.json tests/mutantes/trava-agente-morto-5.json` → M25, M26, M27 (agentes.py:346, leitura única), M28 (hooks.json:19), M29 a M32 (conformidade.json:50-53): todos `morreu`, rc=0. Os 26 anteriores (M1 a M24 e afins) não mudaram de trecho de guarda, exceto o que o M27 cobre.
- As 4 fixtures novas de conformidade (mv da pasta do projeto, da sessão, forjada; rm da pasta do projeto) rodadas pelo executor de `tests.test_hooks`: 4 de 4 OK.
- Troca de `functools.cached_property` por leitura única com falha guardada (agentes.py:337-349): coberta pelo M27; o comportamento da C4 não muda.
- docs/hooks.md: cita SendMessage, lápide e liberacoes.log (linhas 11 e 70); texto, sem teste próprio. mapa do forge-testes: `hooks/.*` inclui `test_trava_agente_morto` (alteração conferida no diff).
- `--cobertura --base a1318e88`: só 2 `isenta` (as mesmas) e os 2 JSON `não coberto` (cobertos à mão pelos M28 a M32).
- Suíte inteira: não rodei (carga ~14 em 12 CPUs); a bateria é do CI do PR (check-run `bateria`), sem PR aberto neste momento.
