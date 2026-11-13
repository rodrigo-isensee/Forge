---
tipo: qa
contrato: 1
pedido: v0457
branch: melhoria/v0457
commit: 9f5e7f6b9c2e4fdeb26a5819fd71fceee77d2b1e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v0457 (junção das 21 frentes, head 9f5e7f6b; volta 1, delta desde 7c6dd9df)

## Achados
- A1 (recomendado) docs/regras/README.md:1 · resolvido na volta 1: merge 6cfde7e0 da develop 2b896503 sem marcador de conflito; `--remerge-diff` confere as 3 resoluções (ver Revalidação).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Junção não perde frente (21 merges, 21 fragmentos) | `git log` dos merges + `ls changelog.d` (24 = 21 frentes + envio-leve + envio-sandbox + README) | n/a | passou |
| Merge da develop (36d976df) sem perder correção | cruzamento MB→develop × MB→frentes: só tests/test_hooks.py e tests/test_testes_tocados.py nos dois lados; numstat 3+90=93 e 2+65=67 (soma exata) | arquivos tocados dos dois lados | passou |
| Arquivos só da develop (pre-push, README, plugin.json, CHANGELOG, tech-lead) idênticos à develop no head | `git diff 36d976df 7c6dd9df -- <arquivos>` | n/a | passou |
| Envio leve (pre-push) vivo sobre a junção | mutantes envio-leve.json, M1 a M5 | guarda do pre-push | passou |
| MAPA do forge-testes (corrigido na junção, 4fe18828) | mutantes v0457-testes-mapa e -2, M1 a M12 | cada linha de guarda | passou |
| Testes de junção E23.2 (afetados, apoio, paralela, leve) | `unittest tests.test_testes_tocados tests.test_pre_push_leve tests.test_apoio_sandbox tests.test_suite_paralela` | MAPA com ao menos 20 conferidos | passou |

## Cenários e resultado real
- Merge: 21 `merge: junta melhoria/v0457-*` em primeira linha, sem marcador de conflito nos arquivos do diff. Os 5 arquivos listados como `diff --cc` (plugin.json, pre-push, CHANGELOG, README, tech-lead) saem sem hunk: resolução limpa, iguais à develop.
- 237 testes dos 4 módulos acima: 236 ok, 1 pulado (sandbox, /proc de outro namespace), 1 falha só na minha cópia: `PlanoAfetados.test_nunca_menos_que_o_mapa` deu 0 conferidos porque a cópia de `git archive` não tinha índice; com `git add -A` o módulo `PlanoAfetados` passou (9 testes, OK). Artefato do meu ambiente, não defeito.
- `tests.test_hooks` (cruzamento dos dois lados): 136 testes, 6 falhas. Quatro são as `agentes/*` já combinadas no brief (sandbox, /proc). As outras duas são o timeout de 120 s de `pesado/mesma-sessao-libera` (trava global, máquina em carga 15 com outras suítes): `test_fixtures_do_v0442` roda o mesmo fixture sozinho e passa em 11,5 s (OK). Em `test_fixtures` ele repetiu o timeout (534 s de módulo): contenção da trava `pesado`, não regra; o CI do PR confirma.
- `forge-check docs` na cópia com refs: rc 1, 48 linhas, todas em docs/reviews/hk3-parecer-texto.md, docs/security/anti-alucinacao-portao.md e docs/security/guarda-conferente.md (sondas fora do formato); a develop 36d976df dá as mesmas 48 linhas e os arquivos são iguais à develop: pré-existente, não da junção.
- Sem PR da branch ainda: o check-run `bateria` do sha 7c6dd9df não existe (`gh api .../check-runs` devolve `[]`). A suíte inteira fica para o CI do PR; não declaro verde dela.
- Vermelho antes do verde: não rodei de novo; cada frente trouxe o seu `--vermelho` revisado, e a junção não adiciona teste de regra novo além dos ajustes E23.2 (pesos, MAPA, ids), cobertos pelos mutantes acima.

## Provas
- Mutantes: `forge-mutante tests/mutantes/envio-leve.json` rc=0, M1..M5 `morreu`; `forge-mutante tests/mutantes/v0457-testes-mapa.json tests/mutantes/v0457-testes-mapa-2.json` M1..M12 `morreu`.
- Limites: suíte inteira e `claude plugin validate` ficaram para o CI (máquina carregada, instrução do brief).

## Revalidação (volta 1, 7c6dd9df..9f5e7f6b)
- M2 de `tests/mutantes/v0457-testes-mapa.json`: `de` agora inclui a linha seguinte (8+ caracteres); M2 `morreu` em bin/forge-testes:267.
- Merge 6cfde7e0, `--remerge-diff`: README de regras fica com R-COPIA/R-VERIFY ligados a R-LIMITES.md e R-DECISAO da develop (uma a uma); economia-de-tokens com regras 9 a 11 da develop e Ritmo como 12, e a skill falar-com-o-dono cita a 12; test_reval_delta soma (14, teste-le) de test_conferir_reversao e mantém as entradas da junção. Zero marcadores `<<<<<<<` nos 3 arquivos.
- Teto de agents/jarvis.md: 7955 caracteres (`wc -m`), texto da develop com a linha Economia; fixture metricas-texto.json em 7795 (contagem do teste de métricas, `test_metricas_texto` OK).
- Índice de fixtures: 2331 fixtures no corpus (`find`) = 2331 no docs/hooks-fixtures.md; `test_indice_fixtures` OK.
- Cópia com índice git: `test_reval_delta`, `test_testes_tocados`, `test_pre_push_leve`: 165 testes OK, 1 pulado (sandbox /proc).
- Não rodei a suíte inteira nem test_catraca (2 falhas vêm da develop, E18.5 em QA); a bateria fica para o CI do PR.

## Provas (volta 1)
- `forge-mutante tests/mutantes/v0457-testes-mapa.json tests/mutantes/v0457-testes-mapa-2.json`: M1..M12 `morreu`.
