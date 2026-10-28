---
tipo: revisao-seguranca
contrato: 1
pedido: lote-ti
branch: melhoria/lote-ti
commit: 98991ed1ae89eb2e94612acaad29201582aec83e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: lote-ti

Escopo: `ed7fbd8...98991ed`, só testes (`tests/apoio_volta_unica.py`, `tests/test_hooks.py`, `tests/test_hooks_volta_corpus.py`, `tests/test_hooks_volta_lancador.py`) e um fragmento de changelog. Nenhum arquivo de `hooks/` muda.

## Gatilhos
Controles do Forge (testes que provam o `conformidade`, falha fechada e vigia de prazo). Sem segredo, dependência, workflow ou infra tocados.

## Achados

## Detalhe dos achados
Verificações pedidas:
- HOOKS-FALHA-FECHADA-SANDBOX: nenhuma asserção dos três testes de falha fechada foi removida ou afrouxada; o commit só acrescenta `test_apoio_pathlib_312_faz_o_caminho_longo_demais_levantar` (`tests/test_hooks.py:1314`), que prova a pré-condição (ENAMETOOLONG levantado com o apoio no PYTHONPATH). Falha fechada segue provada (`esperado 2`). Os testes do item rodaram verdes aqui.
- FLAKY-G1-CARGA (T9b, 60 s): `tests/apoio_volta_unica.py:495-509` mantém `subprocess.run(timeout=...)`, e o estouro vira `AssertionError` com a causa ("falha do arnês, não do gerador"); não há retry nem `skip`. Texto que não termina continua reprovando, só em 60 s em vez de 10 s. O teste novo `test_t9b_bash_que_passa_do_prazo_e_falha_do_arnes` (corpus:410) prova o travamento detectado. Não esconde travamento.
- PR-VERDE-D3-TEMPO (CPU em vez de relógio): o vigia de produção (3 s de relógio, e o timeout de 10 s do Claude Code, que libera) segue coberto por testes de relógio em `tests/test_hooks_volta_propriedades.py:136,170-186`, não alterados. O que muda é só o teto K e a propriedade: limites 15 ms (máximo) e 10 ms (média), ~2,2x e 2x o p95 medido (6,9 e 4,9 ms); propriedade 120 s de CPU (decisão do dono de 19:13), medida por `MedidaDeCpu` que soma filhos. Custo que exploda em CPU continua reprovando. `test_guarda_mede_cpu_e_nao_relogio` trava a troca.
- PROP-AMOSTRA: a semente é impressa na falha (`add_note`) e repetível por `FORGE_PROP_SEMENTE`; sem semente, amostra antiga; a cobertura por execução não diminui, só desloca. O gerador não ganha entrada externa além de uma variável de ambiente de teste.

Recomendações (não bloqueantes, em prosa):
- `tests/apoio_volta_unica.py:748`: `process_time` do driver da `Guarda` não conta filho (`git ls-files` em `conformidade.py:1153`) nem espera. No teto K (corpo `ls`, sem git) não importa; uma regressão que passe a bloquear em subprocesso só seria vista pelos testes de relógio do vigia. Severidade informativa; dono: `qa-engineer`, se quiser somar `RUSAGE_CHILDREN` ali.
- O limite da propriedade (120 s) vale 2,8x o p95 medido no sandbox, acima dos 2x da regra D3; está declarado no docstring e a medida no runner do CI fica para o QA. Informativa.
- PA-7 (`docs/engineering/achados-recorrentes.md`) conferido: sem item aplicável a testes; lista sem ocorrências.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e execução local só dos testes do item; `gitleaks`/`osv-scanner` não se aplicam (sem segredo nem dependência no diff).
