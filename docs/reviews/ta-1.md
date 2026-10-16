---
tipo: review
contrato: 1
pedido: ta-1
branch: melhoria/ta-1-fixtures-paralelo
commit: 1820ae46198ae9e8f50bd994c03af033b53e5428
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-16
---
# Review independente: TA-1, fixtures de hook em paralelo

Escopo: `1fd122f48ae8...1820ae46198a` (`tests/test_hooks.py` e `changelog.d/ta-1-fixtures-paralelo.md`); o autor não é este revisor.

Veredito: **APROVADO**, com 2 recomendações que não bloqueiam.

## Conferido
- Nenhum fixture removido, pulado ou marcado: `grep skip|expectedFailure` em `tests/test_hooks.py` não acha nada; `setUp` mantém `minimo(..., 460, ...)`. O corpo das asserções foi movido sem alteração para `executar_fixture`.
- Contagem: 882 fixtures em `tests/hooks/*/*.json` (= `git ls-files tests/hooks`), nomes `hook/stem` únicos (882); 18 em série e 864 em paralelo, o que bate com o fragmento.
- Série: `depende_de_pid_ou_trava` pega o hook `pesado` (18) e qualquer `{pid_` no fixture; só `pesado` usa `{pid_*}` (14 arquivos, todos já dentro do `pesado`). O laço serial roda depois do paralelo.
- Isolamento: `_pasta_temporaria()` é chamada na thread principal (o `addCleanup` não corre entre threads) e cada fixture recebe a sua. `rodar`/`git` usam `ambiente_limpo()` (sem config global, sem `FORGE_*`); o estado dos hooks fica em `.forge/run` dentro da pasta do fixture; `hook.trava()` é por projeto. `{pid_vivo}` é o `os.getpid()` e `{pid_outro}` o `outro` aberto no começo: leitura compartilhada, sem escrita. Não achei estado mutável compartilhado entre threads.
- Falhas: a exceção sai do futuro (`futuro.exception()`) e é relançada dentro de `subTest(fixture=f"{hook}/{stem}")` na thread principal, o mesmo nome de caso de antes, na ordem dos fixtures.
- R-TETO: `max_workers = max(1, min(4, (os.cpu_count() or 2) // 2))`, no máximo 4 processos de hook ao mesmo tempo; dentro do teto.
- Clean code: função extraída com nome claro, comentário só do porquê. Sem regra "ferramenta" aplicável (sem comando configurado a citar neste diff).
- Rodei só `python3 -m unittest tests.test_hooks -q`: 14 testes, OK, 25,3 s (máquina livre; a medição do autor, 32-39 s, é compatível). A suíte inteira fica com o QA.

## Achados
1. `tests/test_hooks.py:239` · a conferência `len(verificados) == len(self.fixtures)` é tautológica (`em_serie` + `em_paralelo` sempre somam `self.fixtures`, e `verificados` é preenchido dentro do `subTest` antes da execução): não pega um fixture que deixe de rodar. Sugestão: comparar com uma contagem independente (`len(list(FIXTURES.glob("*/*.json")))`) ou contar só os fixtures que terminaram sem exceção. Severidade: recomendado.
2. `tests/test_hooks.py:299-300` · duas linhas em branco dentro da classe, entre `executar_fixture` e `test_cada_hook_tem_caso_que_passa_e_que_bloqueia`; sobrou uma. Severidade: recomendado (formatação).

## Não revisado
Suíte inteira e `validar-plugin.sh` (QA, R-REVIEW antes de R-QA). A medição do PR (3 execuções antes e depois) é do autor; a terceira execução depois (74 s, máquina ocupada) está registrada no fragmento com a ressalva.
