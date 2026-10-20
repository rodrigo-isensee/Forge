---
tipo: qa
contrato: 1
pedido: teto-adaptativo
branch: melhoria/teto-adaptativo
commit: 54852d4e5bde991de5a2691dc4fa979d9ce01d4e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# Parecer de QA: teto de agentes adaptativo (R-TETO)

Escopo: E1 (R-TETO), E2 (hook `agentes`, `forge-check kanban`, R-WIP) e E3 (testes e fragmento) do pedido `teto-adaptativo`, sobre o código 54852d4 (review e segurança aprovados; HEAD 8dad4de só acrescenta os pareceres). Sem UI: E2E de navegador e acessibilidade não se aplicam. O pedido não numera critérios (`CA-n`); as obrigações são E1, E2, E3 e as decisões do dono nele registradas.

## Método
- Suíte completa e validação do plugin na raiz da worktree, sem outra suíte rodando (checado com `pgrep -af "python3 -m unittest discover" | grep -v pgrep`, vazio).
- Simulação independente: o hook real `hooks/agentes.py` recebe `PreToolUse` (Agent) num projeto git descartável em `$TMPDIR`, com `FORGE_NPROC` e `FORGE_PROC` (pasta com `loadavg` e `meminfo` falsos); nada em `~/.claude`. O `forge-check kanban` roda com as mesmas variáveis sobre um KANBAN.md montado do modelo `templates/projeto/KANBAN.md`.
- Vermelho antes do verde: `hooks/agentes.py` e `bin/forge-check` de `origin/develop` numa cópia descartável com os testes da branch; `python3 -m unittest tests.test_hooks.Hooks.test_fixtures`.
- Mutação manual (sem ferramenta gratuita na stack do Forge) só em `hooks/agentes.py`, o arquivo alterado pelo diff.

## Resultado da execução
| Verificação | Resultado |
|---|---|
| `python3 -m unittest discover -s tests -q` | Ran 871 tests in 181.8s, OK |
| `scripts/validar-plugin.sh` | marketplace e plugin: Validation passed |
| Simulação do hook (23 casos) | 23 de 23 como esperado |
| Simulação do `forge-check kanban` (12 casos) | 12 de 12 como esperado |
| Hook pesado | `hooks/pesado.py` fora do diff; 17 fixtures de `tests/hooks/pesado` verdes na suíte |

## Obrigação → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1/E2: 16 núcleos, load 3, 6 GB livres liberam mais de 5 agentes | simulação: 5 ativos libera, 15 ativos libera, 16 ativos bloqueia ("teto 16"); fixture `nproc-16-libera` | teto = nproc (máximo) | aprovado |
| E1: load >= 0,8 x núcleos bloqueia | 16 núcleos: load 12,7 libera, 12,8 e 13 bloqueiam; 8 núcleos: 6,3 libera, 6,5 bloqueia; fixtures `load-acima-de-80-bloqueia`, `load-no-limite-de-80-bloqueia` | limite exato 0,8 x nproc | aprovado |
| E1: memória <= max(1 GB, 15% do total) bloqueia | total 16 GB (piso 2,4): 2,5 libera, 2,4 e 2,0 bloqueiam; total 4 GB (piso 1 GB): 1,1 libera, 1,0 e 0,9 bloqueiam; fixtures `memoria-*`, `piso-minimo-de-1gb-*` | limite exato do piso, os dois ramos do max | aprovado |
| E1: sem /proc o teto é min(3, núcleos) | 16 núcleos: 2 ativos libera, 3 bloqueia; 2 núcleos: 1 libera, 2 bloqueiam; 1 núcleo: 1 ativo bloqueia; fixtures `sem-proc-*` | /proc ausente; 1 e 2 núcleos | aprovado |
| E2: `teto_maximo` limita | 16 núcleos com `teto_maximo` 4: 3 libera, 4 bloqueia (mensagem "limitado por teto_maximo 4"); `teto-maximo-limita` | máximo configurado | aprovado |
| E2: `teto_agentes` fixo sobrepõe | `teto_agentes` 2: 2 ativos bloqueia; `teto-fixo-acima-do-adaptativo` | teto fixo | aprovado |
| E2: FORGE_NPROC/FORGE_PROC ficam registrados (R1 da segurança) | `erros.log` do projeto traz os dois avisos | escape de teste visível | aprovado |
| Decisão do dono (worktrees e colunas do WIP seguem o teto): `kanban` aceita mais instâncias com teto alto | teto 16: 8 e 16 instâncias com `worktree:` distinto aceitas; Pronto com 25 aceito | máximo do teto | aprovado |
| Idem: barra acima do teto | teto 16: 17 instâncias barradas ("limite 16"); 8 instâncias sem `worktree:` distinto barradas; Pronto com 26 barrado ("limite 25"); sem /proc (teto 3): 4 instâncias e Pronto 6 barrados, 3 e 5 aceitos; `teto_maximo` 4: 5 barradas, 4 aceitas | logo acima do limite; sem /proc igual ao modelo de hoje | aprovado |
| Tarefas pesadas continuam uma por vez | `hooks/pesado.py` sem alteração no diff; fixtures `outra-ativa-bloqueia`, `outro-agente-da-sessao-bloqueia` verdes | n/a | aprovado |
| E3: testes por hardware e fragmento de changelog | `tests/hooks/agentes/` (nproc 3, 4, 8, 16), `test_hooks` (limites), `changelog.d/teto-adaptativo.md` | 1, 8 e 16 núcleos | aprovado |

## Vermelho antes do verde
Com o `hooks/agentes.py` e o `bin/forge-check` de `origin/develop`, `python3 -m unittest tests.test_hooks.Hooks.test_fixtures` falha em 13 fixtures da branch, entre elas `nproc-16-libera` ("15 agentes ativos, teto 4"), `nproc-8-libera` ("7 agentes ativos, teto 5"), `nproc-3-bloqueia` e `nproc-4-bloqueia` (saída 0, esperado 2), `load-acima-de-80-bloqueia` e `memoria-abaixo-do-piso-bloqueia` (mensagem sem os núcleos e o limite novo). Os testes novos não passam sem a implementação.

## Mutação em hooks/agentes.py
| Mutante | Resultado |
|---|---|
| `CARGA_MAX` 0,8 para 0,9 | morto (8 fixtures falham) |
| `carga >= ...` para `carga > ...` | morto (1) |
| `memoria <= max(...)` para `memoria < max(...)` | morto (1) |
| `PISO_FRACAO` 0,15 para 0,10 | morto (1) |
| `teto_adaptativo` devolve `nproc + 1` | morto (5) |
| sem /proc ignora `min(padrao, nproc)` | morto por `tests.test_hooks` (2 falhas); sobrevive só nas fixtures, e o teste de unidade cobre |

Nenhum mutante sobrevivente.

## Riscos residuais (informativos, sem bloqueio)
- A trava de carga olha o load de 1 minuto: uma rajada de disparos antes de o load subir passa (R3 da segurança; cartão TETO-RAJADA, outro pedido).
- A docstring de `hooks/agentes.py` diz que `teto_maximo` limita só o adaptativo, mas o código o aplica também ao fixo (A5 do review; vai no TETO-RAJADA).
- As mensagens de carga alta valem também para memória baixa ("carga alta ... GB disponíveis"); texto, não comportamento.
- O WSL não expõe temperatura; a proteção é o limite de 80% de carga, como na decisão técnica do pedido.

## Achados
