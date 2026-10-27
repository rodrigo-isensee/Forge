---
tipo: review
contrato: 1
pedido: prop-tempo-cpu
branch: melhoria/prop-tempo-cpu
commit: fe9dfb26221b1de4f68e8efd43899a663d1a52c0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: prop-tempo-cpu

Pedido PROP-TEMPO-CPU (revisão no PROP-TEMPO-CPU-REV, E1.1). Diff revisado: `9620160fc7ce0c0a3e411cb0bc52d1d9716e6fa4...fe9dfb26221b1de4f68e8efd43899a663d1a52c0` (3 commits: cf71384, bfdba3b, fe9dfb2), lido por inteiro; primeira rodada, sem delta.

## Achados

## Parecer
Aprovado. A entrega faz o que o pedido E1 pede, sem afrouxar limite além da decisão técnica de 16:07.

- **Medida de CPU** (`tests/apoio_volta_unica.py:47`): `MedidaDeCpu` soma `time.process_time()` (o processo, com as threads do `ThreadPoolExecutor` do lote) e `ru_utime + ru_stime` de `RUSAGE_CHILDREN`. Os filhos dos quatro testes saem todos por `subprocess.run` (`apoio_volta_unica.py:397`, `:767` e o `rodar` dos textos grandes), que espera o filho; a CPU deles e dos netos que eles esperaram entra na conta. O relógio segue medido e vai na mensagem.
- **Limites:** `test_hooks_volta_lancador.py:153` e `:372` seguem 60; `test_hooks_volta_propriedades.py:153` segue 1,0 e mantém o `limite_de_tempo(5)` de relógio como teto de travamento; `test_hooks_volta_corpus.py:114` passa a `limite_de_cpu_do_corpus()` = 60 × `trabalhadores_do_lote()`, exatamente a decisão de 16:07. Os outros tetos de relógio (timeout de 900 s e 600 s dos `subprocess.run`) ficam. Nenhuma asserção saiu; nenhuma amostragem entrou.
- **Fonte única do número de trabalhadores:** `trabalhadores_do_lote()` é usada tanto pelo lote (`apoio_volta_unica.py:418`) quanto pelo limite; não há como o limite e o paralelismo divergirem.
- **Mensagem:** a do corpus traz CPU, relógio e trabalhadores (`MedidaDeCpu.texto()` mais `trabalhadores`); as dos outros três trazem CPU e relógio.
- **`tests/test_medida_cpu.py`:** cobre os três termos da soma (filho que dorme não conta e o relógio passa, filho que gasta conta, o próprio processo conta), o formato do texto e o limite por núcleos (1, 2, 4, 8, 64 → 1, 1, 2, 4, 4 trabalhadores). Folgas razoáveis sob carga (0,8 s gastos contra ≥ 0,7; dormir 1,5 s contra CPU < 0,5).
- **Mutantes** (`tests/mutantes/prop-tempo-cpu.json`, M1 a M4): `bin/forge-mutante tests/mutantes/prop-tempo-cpu.json` no head fe9dfb2: `M1 · morreu`, `M2 · morreu`, `M3 · morreu` (`apoio_volta_unica.py:62`), `M4 · morreu` (`:44`). Cada mutante tem o seu teste e o `de` casa com a linha real.
- **Mapa FORGE_CHECK** (`bin/forge-testes:73`): uma linha, só o acréscimo de `test_medida_cpu` (decisão 17:39); `tests/test_testes_tocados.py:61` passa de 25 para 26, exata, e `test_medida_cpu` entra no `assertIn` (decisão 17:45). `python3 -m unittest tests.test_medida_cpu tests.test_testes_tocados.Mapa`: `Ran 17 tests ... OK`.
- **Teto M14:** 142 linhas de código e teste (`git diff --numstat --no-renames`, fora `changelog.d/` e `tests/mutantes/`), abaixo de 400; não toca `hooks/` nem `tests/catraca.py`.
- **Fragmento de changelog:** `changelog.d/prop-tempo-cpu.md`, `### Corrigido`; o `CHANGELOG.md` não foi editado.
- **Regras:** `R-NEUTRO` e `R-CUSTO` preservadas (nada de projeto, nada pago); `tests/config.json` intocado; PA-7 (`docs/engineering/achados-recorrentes.md`) sem achados registrados, nada a conferir.
- **Segurança e QA:** pareceres próprios, em paralelo (decisão de 2026-10-24, item 4); não refeitos aqui.

Recomendações (não devolvem; fora do bloco porque o parecer é aprovado):
- `tests/apoio_volta_unica.py:423` · os textos grandes rodam em série depois do lote, e o orçamento de 60 × trabalhadores cobre também essa parte, que no relógio dividia os 60 s; dentro da decisão de 16:07, mas, se essa sonda crescer, vale medi-la à parte · recomendado.
- `tests/apoio_volta_unica.py:53` · `RUSAGE_CHILDREN` só conta filhos já esperados; um descendente que ficasse vivo depois do teste (processo solto) não entraria na conta. Hoje nenhum caminho dos quatro testes deixa filho solto; vale uma linha no docstring dizendo o limite da medida · recomendado.
- `tests/test_hooks_volta_corpus.py:37` · `limite_de_cpu_do_corpus` e `trabalhadores_do_lote` entraram depois de `rodar`, fora da ordem alfabética da lista de importação · recomendado.
