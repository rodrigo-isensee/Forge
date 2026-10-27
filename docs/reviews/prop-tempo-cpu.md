---
tipo: review
contrato: 1
pedido: prop-tempo-cpu
branch: melhoria/prop-tempo-cpu
commit: 650dbf9398a2a151368cd231d0e691a53857ccc0
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: prop-tempo-cpu

Pedido PROP-TEMPO-CPU (revisão no PROP-TEMPO-CPU-REV, E1.1). Rodada 2, revalidação por delta sobre o parecer `d39708e84d62e2182cbe37897ec581cc527c9ff4` (head anterior `fe9dfb2`).

## Delta lido
`bin/forge-check delta --parecer docs/reviews/prop-tempo-cpu.md` (intervalo `fe9dfb2..650dbf9`): o único commit de código é `650dbf9` (os outros três, `d39708e`, `cd213ff`, `2a55d58`, são pareceres). Lido por inteiro: `tests/apoio_volta_unica.py:38` e `:43-44`, `tests/mutantes/prop-tempo-cpu.json:37`, `:39-40` e `:42`, `tests/test_hooks_volta_corpus.py:115`, `tests/test_hooks_volta_lancador.py:153` e `:372`, `tests/test_hooks_volta_propriedades.py:153`, `tests/test_medida_cpu.py:43` e `:46`. Já lido (rodada 1, sem mudança): o resto do diff `9620160...fe9dfb2`, inclusive `bin/forge-testes:73` e `tests/test_testes_tocados.py:61`. Também relido, por ser texto que descreve os números que mudaram: `changelog.d/prop-tempo-cpu.md` e os docstrings dos três testes.

## Achados
- A1 (bloqueante) changelog.d/prop-tempo-cpu.md:2 · classe requisito (definição de pronto, documentação afetada): diz "com os mesmos limites", mas a decisão do dono de 19:13 sobe os três e "afrouxa a trava"; dizer os limites novos e o motivo.
- A2 (bloqueante) tests/test_hooks_volta_propriedades.py:141 · classe requisito (definição de pronto: comentários de contrato atualizados): o docstring do `test_t_reconhecedor_da_reavaliacao_e_linear` diz "rodam em menos de 1 s de CPU", e a asserção da linha 153 passou a 2,0. Trocar para 2 s.
- A3 (bloqueante) tests/test_hooks_volta_lancador.py:140 · classe requisito (idem A2): o docstring diz "O tempo (60 s de CPU)", e a asserção da linha 153 passou a 120. Trocar para 120 s.
- A4 (bloqueante) tests/test_hooks_volta_lancador.py:355 · classe requisito (idem A2): o docstring diz "o tempo (60 s de CPU)", e a asserção da linha 372 passou a 120. Trocar para 120 s.

## Parecer
Reprovado, só pelo texto que descreve os números (A1 a A4); o código do delta está certo e a volta é de quatro linhas de texto.

- **Números, conforme a decisão do dono de 19:13:** `limite_de_cpu_do_corpus()` = `90 * trabalhadores_do_lote()` (`tests/apoio_volta_unica.py:44`), com a mensagem do corpus em 90 (`test_hooks_volta_corpus.py:115`); as duas propriedades do lançador em 120 (`test_hooks_volta_lancador.py:153` e `:372`); o T em 2,0 (`test_hooks_volta_propriedades.py:153`), com o `limite_de_tempo(5)` de relógio da linha 149 igual.
- **Nada além dos números mudou no código:** `650dbf9` tem 13 adições e 13 remoções, todas troca de número, o nome do teste e as mensagens; nenhuma asserção saiu, nenhum teto de relógio (5 s do T, 900/600 s dos `subprocess.run`, 3,0 s do teste dos textos grandes) mexeu, e a fonte única de trabalhadores segue a mesma.
- **Teste renomeado:** `test_limite_do_corpus_e_60_s_por_trabalhador` virou `test_limite_do_corpus_e_90_s_por_trabalhador` (`tests/test_medida_cpu.py:43`), com o esperado `90 * trabalhadores` para 1, 2, 4, 8 e 64 núcleos; o nome antigo só sobra nos pareceres de QA e segurança da rodada anterior (registro histórico, não código). `python3 -m unittest tests.test_medida_cpu`: `Ran 5 tests ... OK`.
- **M4 da spec** (`tests/mutantes/prop-tempo-cpu.json:37-42`): `de` casa com a linha real (`    return 90 * trabalhadores_do_lote()`), `para` é `return 90` fixo, e aponta o teste renomeado. `bin/forge-mutante tests/mutantes/prop-tempo-cpu.json` no head 650dbf9: `M1 · morreu`, `M2 · morreu`, `M3 · morreu` (`apoio_volta_unica.py:62`), `M4 · morreu` (`:44`).
- **Teto M14:** 142 linhas de código e teste no PR inteiro (`git diff --numstat --no-renames 9620160...650dbf9`, fora pareceres, `changelog.d/` e `tests/mutantes/`), igual à rodada 1; não toca `hooks/` nem `tests/catraca.py`.
- **Regras:** `R-NEUTRO` e `R-CUSTO` preservadas; `tests/config.json` intocado; PA-7 (`docs/engineering/achados-recorrentes.md`) sem achados registrados, nada a conferir.
- **Segurança e QA:** pareceres próprios, em paralelo (decisão de 2026-10-24, item 4); não refeitos aqui.

Recomendações da rodada 1 (seguem como recomendação, não devolvem): `tests/apoio_volta_unica.py:423` (os textos grandes em série cabem no mesmo orçamento do corpus, agora 90 × trabalhadores); `tests/apoio_volta_unica.py:53` (`RUSAGE_CHILDREN` só conta filhos esperados; uma linha no docstring); `tests/test_hooks_volta_corpus.py:37` (ordem da lista de importação).
