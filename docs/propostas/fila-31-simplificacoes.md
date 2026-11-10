# FILA-31: simplificações de clean code do Forge

Medida em 2026-11-10 sobre `bin/` e `scripts/` (base `587415d8`, `forge_versoes.py` fora do escopo). Método: análise por AST
(import sem uso, constante sem uso, variável local sem uso, função de corpo idêntico em dois arquivos, função com 60 linhas ou mais)
e leitura. Ganho em linhas; risco = chance de mudar comportamento ou quebrar teste que carrega o script.

## Aplicadas nesta versão (maior ganho, menor risco, sem mudar comportamento)

| # | Onde | O quê | Ganho | Risco |
|---|------|-------|-------|-------|
| S1 | `bin/forge-sugerir:17` (`posixpath`), `bin/forge_run.py:12` (`os`) | import sem uso | 2 linhas, 2 dependências a menos | nulo |
| S2 | `bin/forge-check:7171` (`SUBTITULO_DO_REGISTRO`), `bin/forge-testes:174` (`NOME_COM_PONTO`), `bin/forge_decisor.py:23` (`CONDICOES`) | constante sem nenhuma referência em `bin/`, `scripts/`, `hooks/` e `tests/` | 3 linhas de código morto | nulo |
| S3 | `bin/forge-check:768, 842, 1578, 4784, 5914`, `bin/forge-doutor:258`, `bin/forge-mutante:543`, `scripts/promover-homolog.py:227` | nome atribuído e nunca lido passa a `_nome` (diz ao leitor que o valor é descartado) | 8 nomes enganosos | nulo |

## Fila (não aplicadas)

| # | Onde | O quê | Ganho | Risco |
|---|------|-------|-------|-------|
| F1 | `bin/forge-mutante:624-660` e `bin/forge-testes:403-440` | `ENTRADA`, `PESADA`, `outras`, `contexto` idênticos nos dois scripts; extrair para `bin/forge_pesadas.py` | cerca de 37 linhas duplicadas | médio: os testes (`test_forge_mutante.py:1059`, `test_testes_tocados.py:1401`) chamam `f.outras` e `f.contexto` no script carregado; o script precisa importar o módulo por `sys.path` próprio e a catraca protege `bin/` |
| F2 | `bin/forge-mutante:129-146` e `bin/forge-testes:457-480` | `git_da_copia`, `resolver`, `montar_copia` idênticos; só `ambiente_da_copia` difere (o do mutante guarda `PYTHONPYCACHEPREFIX`) | cerca de 24 linhas | médio: mesmo caminho de F1, e o ambiente da cópia é guarda de isolamento |
| F3 | `bin/forge-atualizar:34` e `bin/forge-voltar-versao:19` | `git(projeto, *args)` idêntico | 3 linhas | baixo, ganho pequeno |
| F4 | `scripts/promover-homolog.py:245` (`promover`, 73 linhas) | separar leitura dos checks, decisão e efeito | função mais curta e testável | médio: mexe em script de promoção sem teste por ramo |
| F5 | `scripts/suite-paralela.py:663` (`orquestrar`, 74 linhas) | extrair o laço de espera e o resumo | função mais curta | médio: orquestração concorrente |
| F6 | `bin/forge-check` (10.125 linhas num arquivo só) | continuar a extração de grupos de comandos para `bin/forge_*.py`, como `forge_decisor`, `forge_dono`, `forge_meta`, `forge_run` | arquivo de navegação difícil | alto, por grupo; fazer um grupo por PR, com o teste do grupo |
| F7 | `bin/forge_versoes.py:3`-região de imports (`datetime` sem uso) | import sem uso | 1 linha | nulo; fora desta frente, feita junto da frente que já edita o arquivo |

Critério de reversão: cada item aplicado é um commit só, revertível sem efeito nos outros.
