---
tipo: qa
contrato: 1
pedido: suite-paralela-d4
branch: melhoria/suite-paralela-d4
commit: 1bdd3e8522da941d89a8620a980196401e751126
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: SUITE-PARALELA-D4 (suíte em processos no pre-push e no CI)

Código testado: `1bdd3e8` (o HEAD `6db3bd7` só soma pareceres em `docs/`). Worktree `~/.forge-contrib/wt/suite-paralela-d4`; sondas em cópia `git archive` do `1bdd3e8` em `$TMPDIR/sonda`, com remoto bare local e `XDG_RUNTIME_DIR` próprio (a trava real de outros agentes não foi tocada). Sem rede. Sem correção de código.

## Achados

## Obrigação → teste → resultado
| Obrigação (decisões do dono e escopo do pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: mesmos testes divididos em processos, N medido | `scripts/suite-paralela.py` real na worktree | N = min(4, nproc) | passou: 1347 testes, 4 processos, 192,2 s |
| Guarda de completude: módulo que some reprova | cópia mínima, `modulos()` sem `test_c` | soma e multiconjunto de IDs | passou: `FAILED (guarda=2)`, rc 1, "1 teste(s) ausente(s)" |
| Uma suíte por vez, fila por ordem (SUITE-FILA-JUSTA) | 3 pushes (b1, b2, b3) com 1,5 s de intervalo | ordem de chegada; exclusão | passou: fins a 5,5 s um do outro, b1, b2, b3 em ordem; b2 e b3 avisam a espera |
| Push sem refs não roda a suíte (PREPUSH-JA-NO-REMOTO) | `git push origin b1` já igual | zero refs | passou: "nada a enviar", rc 0, sem suíte |
| Push que só apaga roda a suíte | `git push origin --delete b3` | uma ref com sha zerado | passou: suíte rodou (3 testes, OK) e a ref foi apagada |
| Parar só o próprio grupo (PREPUSH-PKILL-ALHEIO) | TERM no hook que espera; TERM no hook que roda, com processo isca de nome igual vivo | hook em espera; filho; grupos | passou: o que espera morre sem tocar a suíte em curso; o que roda diz "suíte interrompida", reprova o push, os 3 processos somem e a isca segue viva; senha da fila apagada |
| Falha fechada no push de código | push da cópia completa com `x.md` fora do clone (pré-existente) | rc diferente de 0 reprova o envio | passou: reprovou o push, ref não criada |
| Sem afrouxar: suíte inteira e plugin | `unittest discover -s tests -q`; `scripts/validar-plugin.sh` | n/a | passou: 1347 testes OK em 373,2 s (série); `Validation passed` |

## Execuções reais
- Série, na raiz da worktree: `Ran 1347 tests in 373.191s`, `OK`.
- Paralela (`scripts/suite-paralela.py`, uma vez, pela mesma trava e fila): 4 processos (418, 143, 363 e 423 testes; 185,6, 192,0, 191,6 e 182,6 s), tempo de parede 192,3 s, `OK`, árvore limpa depois. Máquina com outros agentes (load 2 a 3), por isso acima dos 112 s do parecer de devops; ainda -49% sobre a série medida agora.
- Push da cópia completa: pela suíte em processos, 1347 testes, 4 processos, 116 s a 146 s conforme a carga, `OK (skipped=1)`; a primeira tentativa foi reprovada por `tests/test_pedido_fora.py:68`, que lê um `x.md` fora do clone (cartão já aberto no pedido, depende do ambiente, não do diff); a cópia foi movida de pasta e passou. O hook também esperou a trava de outro agente por 11 min sem furar a fila.
- Vermelho antes do verde: os testes novos (`tests/test_suite_paralela.py`, `tests/test_pre_push_trava.py`) são da E1.1; as sondas acima reproduzem cada comportamento no hook e no script reais e a guarda foi vista falhando.

## Riscos (não bloqueiam)
- Tempo da suíte depende da carga da máquina; com agentes rodando, a ordem de 190 s, não de 110 s.
- Módulo que sumisse da árvore depois do `discover` só foi simulado por troca da lista (`modulos()`), não por corrida real.
