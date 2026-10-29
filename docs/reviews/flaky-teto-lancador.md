---
tipo: review
contrato: 1
pedido: flaky-teto-lancador
branch: melhoria/flaky-teto-lancador
commit: b4bd24c39821e74ec66c4064a09c1f2499140aeb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: flaky-teto-lancador

Pedido FLAKY-TETO-LANCADOR (E1 a E3), revisado no pedido FLAKY-TETO-LANCADOR-REV, E1.1. Base `develop` b3791ed, head b4bd24c, primeira rodada (sem delta).

## Achados

## Parecer
Aprovado. Sem achado bloqueante nem recomendado.

- **Limite medido no runner (E1, regra de 2026-10-27 20:13):** o log do run 40756009076 (workflow_dispatch, head 62e071a, branch `melhoria/flaky-teto-lancador`) traz `TETO-LANCADOR p95-max=12.21 p95-media=10.38 python=3.12.15` e `TETO-LANCADOR p95-max=5.35 p95-media=4.04 python=3.14.9` (lido com `gh run view 40756009076 --log-failed`, cache do gh em `$TMPDIR`). Os limites são 2x o maior p95 das duas versões, arredondado para cima na primeira casa: 24,42 para 24,5 ms (máximo) e 20,76 para 20,8 ms (média), a mesma regra nos dois. A sonda usou a mesma entrada (`linha(k)`), as mesmas 20 decisões e 10 execuções; o p95 de 10 valores com a fórmula dela é o maior valor, o que deixa a medida do lado conservador. A docstring cita data, run e os p95.
- **Asserções em CPU:** as duas asserções seguem sobre os segundos que `decidir_na_guarda` devolve, que são `process_time` (o teste vizinho `test_guarda_mede_cpu_e_nao_relogio` prova isso); nenhuma passa a relógio, nenhuma sai. As asserções de decisão (libera em K, recusa em K+1 com o motivo do teto) ficam intactas. O controle continua: um custo duas vezes acima do pior p95 do runner reprova.
- **Revert do teste temporário:** `git diff b3791ed d2970bd` sai vazio; o teste `test_medida_temporaria_do_teto` não está em b4bd24c. O commit temporário fica no histórico, rotulado e revertido, o que conta como chegou a medida (E2, sem workflow novo; o `workflow_dispatch` já existia em `.github/workflows/ci.yml`, repositório público, `R-CUSTO`).
- **Escopo:** só `tests/test_hooks_volta_lancador.py` (docstring e duas linhas) e o fragmento `changelog.d/flaky-teto-lancador.md` (E3). Nada em `hooks/`, nos outros testes de tempo nem em `tests/config.json`.
- **Teto M14:** 9 linhas de código e teste (`git diff --numstat --no-renames`: 5+4 em `tests/test_hooks_volta_lancador.py`), dentro de 400.
- **Ferramentas:** `python3 -m unittest tests.test_hooks_volta_lancador` no head revisado: 22 testes, OK. O pre-push do autor registrou 2182 testes OK (histórico do pedido); a suíte completa fica no CI do PR.
- **Commits:** Conventional Commits em português, um por passo (medida, revert, correção).
- **Achados recorrentes (PA-7):** o arquivo está sem linhas; nenhuma classe se repetiu, nenhuma linha AR gravada.
- **Segurança e QA:** pareceres próprios, em paralelo (`docs/security/`, `docs/qa/`); não refeitos aqui.
