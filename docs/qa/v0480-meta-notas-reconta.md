---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas-reconta
commit: 25c6a8be55fd458c627fe3f28dd1ae6609483d9a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0480-meta-notas-reconta (E137.26, PR #822, revalidação por delta no head 25c6a8be)

Revalidação do A1 bloqueante do parecer anterior (head c947a063, E137.17), só o que mudou em `tests/test_meta.py` e `tests/mutantes/v0480-meta-notas-reconta.json` (E137.22), mais o delta E137.26 abaixo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Ordem de uso mais recente decide quem sai (hooks/meta.py:327) | test_sessao_que_volta_a_ser_usada_guarda_a_marca | teto MARCAS_GUARDADAS com sessão reutilizada | passou; cai com `pop` trocado por `get`; o mutante M5 morre |

## Cenários e resultado real
- `python3 -m unittest tests.test_meta` (da raiz): Ran 55 tests, OK.
- Mutante manual refeito por mim, `vistas.pop(str(transcrito), {})` para `vistas.get(str(transcrito), {})` em hooks/meta.py: o teste novo falha (`AssertionError: .../s0.jsonl not found in {s7 ... s14}`), Ran 55 tests, FAILED (failures=1). Arquivo restaurado, `git status` limpo.
- `bin/forge-mutante tests/mutantes/v0480-meta-notas-reconta.json --base 67810f5d`, rc 0: `base=67810f5d3246cfc4f5b0f6cb36d1975f0468f3c0 mb=67810f5d3246cfc4f5b0f6cb36d1975f0468f3c0 rev=6b1b7c1199c10a385e098dd26952848a833e404f`; M1, M2 (erro), M3, M4 e M5 (hooks/meta.py:327) morreram.
- `bin/forge-testes --vermelho c947a063 --modulos test_meta`: sai "nenhum teste prova a mudança", porque a base c947a063 já traz o mesmo código de produção; o commit do delta só acrescenta teste e mutante. O vermelho deste teste é o do mutante acima (a falha observada), não o da base.
- Suíte inteira: só no CI do PR; não rodada aqui.

## Delta E137.26 (head 25c6a8be)
`forge-check parecer delta`: intervalo 6b1b7c11..25c6a8be; no domínio só `tests/mutantes/v0478-meta-notas.json` e `tests/mutantes/v0478-meta-notas-2.json` (trechos `de` alinhados ao código atual de `hooks/meta.py`).
- `bin/forge-mutante --processos 1 --ids M1,M10 tests/mutantes/v0478-meta-notas.json tests/mutantes/v0478-meta-notas-2.json`: `rev=25c6a8be55fd`; `M1 · morreu · hooks/meta.py:286`; `M10 · morreu · hooks/meta.py:285`.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: Ran 4 tests, OK.
- `python3 -m unittest tests.test_meta`: Ran 55 tests, OK.
- Suíte inteira: só no CI do PR; não rodada aqui.
