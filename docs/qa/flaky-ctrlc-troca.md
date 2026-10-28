---
tipo: qa
contrato: 1
pedido: flaky-ctrlc-troca
branch: melhoria/flaky-ctrlc-troca
commit: a6adac96786de046c4eb5db80b7eff038de159a3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: flaky-ctrlc-troca

Base 41ba6111694b, head a6adac96786d (diff: `tests/test_atualizar.py`, `tests/mutantes/flaky-ctrlc-troca.json`, fragmento de changelog; nenhum código de produção). Plano antecipado não se aplica (correção de teste, sem especificação nova).

## Achados

## Critério → teste → resultado
| Critério (pedido) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: Ctrl-C na troca não depende do SIGINT herdado | `CtrlCNaTroca.test_ctrl_c_na_troca_nao_deixa_ponto_nem_marca_...` (com SIGINT ignorado no pai) | SIGINT ignorado herdado (pre-push com `&`) | passou |
| E1: o teste não depende do ambiente | `CtrlCNaTroca.test_o_ctrl_c_na_troca_vale_mesmo_com_a_suite_rodando_com_o_sigint_ignorado` | idem; falha se o `preexec_fn` sair | passou |
| E1: nenhuma asserção removida ou afrouxada | diff do teste (só soma `preexec_fn`, `import signal` e 1 teste) | n/a | conferido |
| PQ-1: estável sob carga | classe `CtrlCNaTroca` x20, SIGINT ignorado, 6 laços de CPU por `timeout 150` | carga alta | 20/20 |

## Cenários e resultado real
- `python3 -m unittest tests.test_atualizar.CtrlCNaTroca`: 8 testes OK. Idem com o SIGINT ignorado no processo pai: 8 OK.
- `python3 -m unittest tests.test_atualizar` (arquivo inteiro): 79 testes OK (46,9 s).
- Repetição da classe 20 vezes, com SIGINT ignorado e carga por timeout (loadavg 6,96 em 12 núcleos): ok=20 bad=0.
- `bin/forge-mutante tests/mutantes/flaky-ctrlc-troca.json` (rc=0): `F1 · morreu · bin/forge_versoes.py:270`. Lista conferida contra o diff: o diff não muda linha de guarda em `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`; o F1 é a guarda que o teste protege, sem lacuna.
- Vermelho antes do verde: `forge-testes --vermelho 41ba6111… --modulos test_atualizar` saiu 1, "nenhum teste prova a mudança", e não pode provar: a correção está em `tests/`, que a ferramenta mantém no HEAD (`mantidos no HEAD: tests/test_atualizar.py`), então base e HEAD rodam o mesmo teste. Prova equivalente feita à mão numa cópia em `$TMPDIR` (HEAD com `tests/test_atualizar.py` da base), SIGINT ignorado no pai: o teste do Ctrl-C FALHOU (`AssertionError: 'Nada foi atualizado' not found ... Não deu para trocar o plugin`, rc=1), o defeito do pre-push reproduzido; sem o SIGINT ignorado, o mesmo teste passa na base (rc=0), o que confirma a causa (SIGINT herdado ignorado, não o relógio). Com o HEAD, passa nos dois modos.
- PA-7: `docs/engineering/achados-recorrentes.md` sem achados registrados; nada a conferir.

## Observações (não bloqueiam)
- `preexec_fn` não é seguro com threads; o `rodar` roda sem threads na suíte, e a alternativa (`restore_signals`) não cobre SIGINT ignorado. Sem ação.
