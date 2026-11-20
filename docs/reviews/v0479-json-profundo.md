---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-json-profundo
commit: fbab4dede7912d7650c8787b4edbbaed2e73e1fb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478, E44.3 (JSON-PROFUNDO-PY314)

Diff `004ce869..fbf2c6f7`: teto comum de aninhamento (64 níveis de `[` e `{`) antes do `json.loads` no `ler_estado` de `hooks/agentes.py`, nos leitores da catraca (`json_raso` em `tests/catraca.py`) e no `ci_vermelha` de `bin/forge-placar`; fonte em `hooks/_json_raso.py`, cópias na catraca (que não carrega código de fora, I7) e no `forge-placar` (cópia já na develop, só o leitor novo no diff).

## Achados
- A1 (recomendado) hooks/_json_raso.py:9 · A docstring (e tests/test_json_raso.py:3, tests/catraca.py:96) diz que o teste prova as três cópias iguais "caractere a caractere"; ele prova respostas iguais em 14 casos. Ajustar o texto ou comparar o corpo das funções (inspect.getsource) no teste.
- A2 (recomendado) bin/forge-placar:199 · A recusa do `--ci` fundo tem duas mensagens no mesmo script (`JSON de --ci X aninhado...` aqui e `--ci X não é uma lista de runs legível (aninhado...)` em :715) para a mesma entrada; unificar num só texto.

## Sondas

## Parecer
Aprovado. O item faz o que a E44.1 e a E44.2 pedem (`R-REVIEW`): o teto entra antes do `json.loads`, sem recursão, com mensagem fixa, e falha fechada nos três leitores (estado ilegível recusa com R-TETO, catraca trata como JSON ilegível pelo `ValueError` que os chamadores já capturam, placar sai com 2 sem traceback). Os `json.loads` que sobram em `tests/catraca.py:506,508` leem chaves que a própria catraca serializou, como o comentário em `tests/catraca.py:97` registra. Bytes do estado são decodificados com a detecção do `json`; o erro de decodificação cai no `except Exception` de `ler_estado` e vira ilegível.

Tamanho (H1): cerca de 95 linhas de código fora testes e docs, um comportamento; dentro do teto. Commits em Conventional Commits, em português, um por mudança.

Ferramentas, sem refazer: `bin/forge-mutante` nas três specs, 1 processo, no head: M1 a M20 morreram (M4 por erro do teste declarado); `--cobertura --base 004ce869` sem guarda descoberta; `--conferir` com os trechos no lugar. Testes novos rodados da raiz (`tests.test_json_raso`, `test_estado_ilegivel...test_json_aninhado_fundo_e_ilegivel`, `test_catraca...test_json_aninhado_acima_do_teto_e_ilegivel`, `evals.test_placar...test_ci_aninhado_acima_do_teto_sai_com_2_sem_traceback`): 5 OK no python 3.12.3. Suíte completa: no CI do PR, ainda não aberto (brief sem PR); o merge espera o CI verde.

Os dois recomendados não devolvem e viram cartão depois do merge (META85).

## Revalidação
Delta lido (`forge-check parecer delta`, intervalo `fbf2c6f7..fbab4ded`, sem o que veio da develop `ef7739a` pelo merge do `forge-fechar`): no domínio só `docs/indice-forge.md`, uma linha nova na tabela de `hooks/` para `_json_raso.py`, com o texto da primeira linha da docstring do módulo. `tests.test_indice_forge` rodado da raiz no head: 19 OK. Sem achado novo; o parecer segue aprovado no head `fbab4ded`.
