---
tipo: qa
contrato: 1
pedido: ta-1
branch: melhoria/ta-1-fixtures-paralelo
commit: 1820ae46198ae9e8f50bd994c03af033b53e5428
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - TA-1, fixtures de hook em paralelo

Sem UX nem API. Código testado: 1820ae4 (`tests/test_hooks.py` e `changelog.d/ta-1-fixtures-paralelo.md`) sobre a base 1fd122f. O HEAD (5839185) só acrescenta o parecer de review (`parecer: aprovado`, R-REVIEW antes de R-QA). Máquina: WSL2, 16 CPUs, 7,9 GB; carga compartilhada com outras sessões do time (registrada abaixo). Ferramenta de mutação: a stack da fábrica não tem; no lugar, mutantes manuais (itens E-a e E-g).

## Obrigação -> teste -> resultado
| ID | Obrigação (pedido E1) | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 685 testes, OK (131,8 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| E-a | Falha de fixture aparece em `subTest` com o nome do caso (paralelo e série) | cópia em `$TMPDIR` de `git archive HEAD`; `codigo` 0 -> 2 em `vigia/bloqueio-de-outra-sessao-nao-conta` e em `pesado/citar-a-ferramenta-libera`; `python3 -m unittest tests.test_hooks.Hooks.test_fixtures` | exceção da thread relançada na principal | vermelho: `FAIL: test_fixtures (...) (fixture='vigia/bloqueio-de-outra-sessao-nao-conta')` e `(fixture='pesado/citar-a-ferramenta-libera')`; `failures=1` cada; original volta ao verde |
| E-b | Mesmo número de fixtures antes e depois | contador de `addSubTest` num `TestResult` (script em `$TMPDIR`), `test_fixtures` na base 1fd122f e em 1820ae4 | nenhum removido/pulado | base: 882 ok, 882 nomes únicos; branch: 882 ok, 882 únicos; `ls tests/hooks/*/*.json` = 882 |
| E-c | Ganho medido | `python3 -m unittest tests.test_hooks -v 2>&1 \| tail -3`, 3 vezes cada, alternando (cópias limpas das duas revisões) | n/a | ver tabela abaixo |
| E-d | `os.cpu_count()` baixo reduz o paralelismo sem erro | `os.cpu_count` substituído por 1, 2 e 8 (script em `$TMPDIR`; imprime o `max_workers` recebido) | `max(1, ...)` | cpu=1: max_workers 1, OK (127 s); cpu=2: max_workers 1 (2//2), OK (83 s); cpu=8: max_workers 4, OK (38 s) |
| E-g | A conferência de contagem pega fixture que deixa de rodar | mutante: `em_paralelo = [...][1:]` na cópia | contagem | vermelho: `AssertionError: 881 != 882 : todo fixture é verificado` |

Medições de E-c (tempo de `tests.test_hooks`, 14 testes, todos OK; carga de 1 min lida antes de cada execução):

| Execução | base (série) | carga | branch (paralelo) | carga |
|---|---|---|---|---|
| 1 | 127,8 s | 2,3 | 27,1 s | 5,3 |
| 2 | 144,0 s | 4,9 | 86,1 s | 4,6 |
| 3 | 85,2 s | 7,8 | 42,2 s | 3,3 |

O ganho existe em todas as execuções, mas o ruído de carga é grande (a execução 2 da branch, 86 s, pegou outras suítes rodando). Com máquina livre: base 77,1 s (contagem E-b) contra 27,8 e 27,7 s na branch (execuções isoladas de `test_fixtures`). O fragmento do changelog diz 84-114 s antes e 32-39 s depois (duas de três execuções, com a ressalva dos 74 s); é coerente com o medido aqui.

## Achados
- Nenhum bug. Sobre a recomendação 1 do review (conferência "tautológica"): ela pega fixture perdido depois da partição serial/paralelo (E-g, 881 != 882); o que ela não vê é perda na origem (`self.fixtures`), que já era guardada por `minimo(..., 460, ...)` no `setUp`, igual a antes. Não é defeito; contar contra o glob dos arquivos seria um reforço opcional. A recomendação 2 (uma linha em branco a mais, `tests/test_hooks.py` perto da linha 299) é formatação, a cargo do autor.
- Residual conhecido: com `os.cpu_count()` de 1 a 3 o teste roda com 1 trabalhador (sem ganho, sem erro); o teto de 4 respeita R-TETO.

## Resultado da execução
2026-10-16, WSL2, Python 3 da máquina, sem rede externa. Suíte inteira 685/685 OK; validação do plugin OK; E-a a E-g como acima. `forge-check pr ta-1 --ref HEAD --base origin/develop` antes deste parecer: único achado "docs/qa: sem parecer para o pedido `ta-1` (R-QA)", que este arquivo resolve; rodado de novo depois do commit (ver relatório).
