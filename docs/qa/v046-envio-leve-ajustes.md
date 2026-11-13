---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/envio-leve-ajustes
commit: 1beb0d5aee9f14ae6db5a1fd1b4053ddd581caaf
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 (E19.1, envio leve ajustes), revalidação no head 1beb0d5a

Revalida o parecer aprovado em c3e271e5 (sem arquivo). Delta c3e271e5..73d0017a: `README.md` (1 linha) e `tests/test_pre_push_leve.py` (+2/-1). Nenhuma linha de `.githooks/pre-push` mudou.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 do review: o teste de segredo cai quando a barreira da base some | `test_segredo_no_delta_ainda_barra_sem_imprimir_o_valor` (a branch neutraliza `scripts/verificar-contribuicao.sh`, só `segredo_no_delta` barra) | segredo no delta, sem imprimir o valor | passou no head (8 testes OK); com o mutante em `.githooks/pre-push:212` (`segredo_no_delta \|\| exit 1` → `true`) o teste falha: FAIL, 8 testes, failures=1 |
| A2 do review: README diz que o `so_parecer` só vale com opt-in | leitura do diff (README.md:68) | n/a | passou: "Só com o opt-in há uma exceção curta (o envio leve sai antes dela)", coerente com o hook |
| Critérios anteriores (envio comum sem teste, protegidas, não fast-forward, opt-ins) | `tests.test_pre_push_leve` | os mesmos | mantidos: hook intocado |

## Cenários e resultado real
- Cópia limpa do head (`git archive`), `python3 -m unittest tests.test_pre_push_leve`: Ran 8 tests, OK.
- Mutante: mesma cópia, linha 212 trocada; saída: `FAIL: test_segredo_no_delta_ainda_barra_sem_imprimir_o_valor`, `FAILED (failures=1)`.
- Vermelho antes do verde: o teste mudado é prova de mutante, não regra nova; o mutante o derruba.
- `test_hooks.test_fixtures` falha também na base, por ambiente (não do delta). Suíte inteira: check-run `bateria` do PR no mesmo sha, não rodada aqui (I5).

## Revalidação por delta no head 1beb0d5a (E19.5)
Delta 55ea12e5..1beb0d5a: uma linha, `bin/forge-testes:139`, acrescenta `test_pre_push_leve` ao MAPA de `scripts/verificar-contribuicao.sh` (A4 do review, achado pelo CI do PR #503, run 43225790681). O merge da develop (55ea12e5) foi só texto. Aprovação do 73d0017a mantida; nenhum achado novo.
- `python3 -m unittest tests.test_pre_push_leve`: Ran 8 tests, OK.
- `python3 -m unittest tests.test_testes_tocados`: Ran 149 tests, OK (skipped=1, skip já existente, não adicionado por este delta).
- Suíte inteira: check-run `bateria` do PR no mesmo sha (I5).
