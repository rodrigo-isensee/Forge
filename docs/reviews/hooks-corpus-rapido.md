---
tipo: review
contrato: 1
pedido: hooks-corpus-rapido
branch: melhoria/hooks-corpus-rapido
commit: 2c14a56245b9dc4060903073c5e4e8227aecd6b3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: hooks-corpus-rapido

Revalidação por delta (head 2c14a56, delta `978d2d6..2c14a56`, abaixo): o A1 bloqueante do parecer anterior (35dd28f) está resolvido. Primeira leitura, escopo `363ceee..978d2d6` (um commit), pedido HOOKS-CORPUS-RAPIDO, E1 a E3; revisão do pedido HOOKS-CORPUS-RAPIDO-REV, E1.1.

## Achados
- A1 (recomendado) docs/hooks.md:95 · o texto ainda cita `tests/test_hooks.py` e a classe `CorpusHeredocVoltaUnica` para as provas (antigo A2; não devolve)
- A2 (recomendado) tests/apoio_volta_unica.py:297 · `DECIDIDOS` segue gravado e sem leitor (antigo A3; não devolve)
- A3 (recomendado) tests/test_pesos_teto.py:15 · o teto de 15 min segue copiado à mão do ci.yml (antigo A4; não devolve)

## O que foi lido
- O diff inteiro de `363ceee...978d2d6` (11 arquivos), o pedido HOOKS-CORPUS-RAPIDO e o -REV, e `docs/engineering/achados-recorrentes.md` (PA-7: sem achado registrado; nada a conferir).
- `hooks/_comum.py` (`executar`, `vigia_de_prazo`, os `lru_cache`), o `__main__` de `hooks/conformidade.py` e `hooks/parecer.py`, `rodar` e `LANCADOR` de `tests/test_hooks.py`, e `MapaDoForgeCheck` de `tests/test_testes_tocados.py`.

## Movimento de código e teto M14
- `git diff --numstat --no-renames 363ceee...978d2d6`: 4210 linhas de código e teste (bin/ 10; tests/*.py 4200), acima das 400.
- Conferência do movimento (script local que compara, linha não vazia por linha, o que saiu de `tests/test_hooks.py` com o que entrou em `tests/apoio_volta_unica.py` e nos 3 módulos): de 1852 linhas removidas, 1840 estão nos arquivos novos; as 12 restantes são o cabeçalho e a docstring da classe antiga e a função `decidir` de `decisoes_dos_hooks`, trocada pelo lote. O resto do que entrou (cerca de 206 linhas) são imports, cabeçalhos de módulo e de classe, o driver do lote, `decidir_em_lote` e o teste de equivalência; mais `tests/test_pesos_teto.py` (41) e o mapa (10). Lógica nova bem abaixo de 400.
- Testes: os 41 `test_*` da classe antiga estão nos 3 módulos, sem repetição e sem `test_*` na base `BaseVoltaUnica` (que não é `TestCase`, então nada roda três vezes); o único novo é `test_decisao_em_lote_igual_ao_subprocesso_do_hook`. As specs de `tests/mutantes/` só trocam o nome do teste para o módulo novo.
- O PR não toca `hooks/` nem caminho de `PROTEGIDOS`: a exceção vale. Aceito o teto com a linha `teto: excedido, 4210 linhas, código movido de tests/test_hooks.py` no corpo do PR (o PR ainda não existe; conferir na abertura).

## Parecer
**Reprovado**, por um achado.

A1 (bloqueante) · `bin/forge-testes:67` (tupla `FORGE_CHECK`) · O brief pede que cada módulo novo caia no plano certo, e o comentário da linha 72 diz que os módulos saídos de `test_hooks` "rodam onde `test_hooks` roda". Não rodam quando muda `bin/forge-check`: `python3 bin/forge-testes --listar bin/forge-check` lista `test_hooks` e não lista `test_hooks_volta_corpus`, `_lancador` nem `_propriedades`. Esses módulos rodam o forge-check: o `DRIVER_DOS_HOOKS` chama `_comum.forge_check()` (carrega `bin/forge-check`) e os hooks chamam `forge_check().git(...)` (`hooks/_comum.py:222`, `hooks/conformidade.py:1155`). Antes, os mesmos testes eram de `test_hooks`, então a mudança tira deles a cobertura do pre-push dirigido para `bin/forge-check`. A conferência `MapaDoForgeCheck` não pega o caso porque o fecho transitivo só segue `import test_*` (`tests/test_testes_tocados.py:518`), e os módulos novos chegam a `test_hooks` por `apoio_volta_unica`. Sugestão: pôr `VOLTA_UNICA` em `FORGE_CHECK` e fazer a `MapaDoForgeCheck` seguir também os `apoio_*` de `tests/`, senão ela acusa a sobra. Severidade: bloqueia.

Recomendações (não devolvem): A2 é texto que ficou para trás (definição de pronto: documentação afetada); A3 é estado sem leitor; A4 e A5 são cópias que podem divergir. Como a entrega já volta por A1, vale fechar A2 e A3 na mesma volta.

Conferido e sem achado:
- `decisoes_dos_hooks` em lote: o filho chama `_comum.executar` com os mesmos argumentos do `__main__` de cada hook, no ambiente de `rodar` (sem `FORGE_GUARDA_ABERTA` nem `FORGE_CARGA_LIVRE`, `FORGE_NPROC=8`, `FORGE_PROC` por hook), com `chdir` para a raiz do hook a cada texto e os prazos largos de teste. O vigia de prazo roda na thread principal do filho, e os `lru_cache` dos hooks só dependem do texto (`conta_do_gh` dá o mesmo valor por processo). A equivalência compara, numa amostra fixa de pelo menos 200 textos (corpus, G1 e alfabeto) e com 0 e 2 presentes, o lote com o subprocesso real.
- Texto acima de 50 KB: sai do lote e vai por `rodar(..., como_o_claude_code=True)`, como antes (o critério era `len(texto) > 50_000` dentro de `decidir`, só com o marcador). Agora roda em série e não no pool, o que só muda o tempo.
- Prazo do lote: `timeout=900` por fatia, contra 120 s por texto antes. Com o volume medido não é risco, mas, se vencer, aparece como erro e não como falha.
- `tests/test_pesos_teto.py`: cumpre a E3 (falha acima de 225 s, com teste do próprio corte e um mínimo de 50 módulos). `tests/pesos-d4.json`: todo módulo de `tests/` tem peso e não sobra peso sem módulo; o maior é `test_forge` (115.1).
- Mapa: os 3 módulos entram em todas as outras regras em que `test_hooks` entra (`hooks/doutor.py`, `hooks/.*`, `stacks/.*`, `.claude-plugin/.*`). `tests/apoio_volta_unica.py`, `tests/pesos-d4.json` e os módulos de teste do diff caem na suíte completa (falha fechada).
- R-NEUTRO, R-CUSTO (nada pago, nada de rede) e as regras invioláveis estão preservados. O fragmento `changelog.d/hooks-corpus-rapido.md` existe. O commit segue Conventional Commits em português.

Ferramenta: testes do item no HEAD revisado, nesta máquina. `python3 -m unittest tests.test_hooks_volta_corpus tests.test_hooks_volta_lancador tests.test_hooks_volta_propriedades tests.test_pesos_teto tests.test_testes_tocados` deu `Ran 124 tests in 198.596s`, `OK`. Os 3 módulos da volta ficam em cerca de 185 s em série, acima dos 131 s do autor; o PQ-1 do pedido (≤ 150 s) é do QA medir. Suíte completa: fica no pre-push e no CI (M8).

## Revalidação por delta (978d2d6..2c14a56)
Delta lido: `bin/forge-testes` (5 linhas), `tests/test_testes_tocados.py`, `tests/test_hooks_volta_corpus.py` (+29) e `tests/mutantes/hooks-corpus-rapido.json`; o resto do delta são pareceres de outros portões (já lidos como tal). Já lido, sem mudança: o movimento de código, `apoio_volta_unica.py`, `test_pesos_teto.py`, `pesos-d4.json`.

- A1 anterior (bloqueante, `bin/forge-testes:67`): resolvido. `FORGE_CHECK` agora termina em `+ VOLTA_UNICA` (linha 74) e traz `test_doutor_relogio`, que copia o script pelo apoio `apoio_versao_defasada`. `python3 bin/forge-testes --listar bin/forge-check` lista `test_hooks_volta_corpus`, `_lancador`, `_propriedades` e `test_doutor_relogio`.
- `MapaDoForgeCheck` agora segue os `tests/apoio_*.py` importados (`IMPORTA_APOIO`), de modo que a conferência acusaria a sobra que antes escapava; `test_forge_check_roda_os_modulos_dele` passou de 21 para 25 módulos e nomeia os quatro novos.
- `test_modulos_da_volta_unica_rodam_onde_o_test_hooks_roda`: cobre cinco caminhos (`hooks/doutor.py`, `hooks/conformidade.py`, `stacks/`, `.claude-plugin/`, `bin/forge-check`) com `subTest`, em modo dirigido.
- `test_driver_do_lote_chama_o_executar_como_o_main_de_cada_hook`: lê por `ast` os argumentos do `_comum.executar` do driver e de cada `__main__` e exige igualdade (inclui `CRITICO`, não `None`) e o `chdir` por hook; fecha o A2/A5 de equivalência da segurança sem a cópia à mão. Passa em 0,17 s.
- Spec `tests/mutantes/hooks-corpus-rapido.json`: `python3 bin/forge-mutante tests/mutantes/hooks-corpus-rapido.json` deu M1 a M6 `morreu` (bin/forge-testes:97, 101, 106, 107, 74 e tests/apoio_volta_unica.py:343). M1 a M5 cobrem as cinco regras; M6 o driver.
- Teto M14: `git diff --numstat --no-renames origin/develop...HEAD`, contando `bin/`, `hooks/`, `scripts/` e `tests/*.py`: 4265 linhas (código movido); nenhum arquivo de `hooks/` nem de `PROTEGIDOS` no diff, então a exceção vale. Exigir no corpo do PR `teto: excedido, 4265 linhas, código movido de tests/test_hooks.py` (o número subiu de 4210). PA-7 (`achados-recorrentes.md`): sem item registrado.
- Ferramenta: `python3 -m unittest tests.test_testes_tocados tests.test_pesos_teto tests.test_doutor_relogio`: `Ran 103 tests in 16.438s`, `OK`. Suíte completa: pre-push e CI (M8).

**Aprovado.** Sem bloqueante. R-NEUTRO e R-CUSTO preservados.
