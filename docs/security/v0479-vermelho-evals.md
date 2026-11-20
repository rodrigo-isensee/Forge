---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-vermelho-evals
commit: 8b5d4a5f52add0af2856af46e95e748cb069f301
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0478 E48.1 (VERMELHO-TESTS-EVALS)

Escopo: diff `004ce869..8b5d4a5f` (6 commits): `bin/forge-testes`, `tests/test_testes_tocados.py`, `tests/mutantes/vermelho-tests-evals.json`, fragmento em `changelog.d/`. Leitura estática, sem suíte local (brief E48.3: máquina carregada); o CI do PR é o portão da bateria e não havia check-run no head na hora deste parecer.

## Gatilhos
Gatilhos: arquivo sensível da catraca (`bin/forge-testes`, a prova de vermelho que sustenta o teste antes da correção), validação de entrada de linha de comando que vira nome de módulo importado.

## Achados

## Sondas

## Detalhe dos achados
Sem achado bloqueante nem recomendado. O que foi conferido:

- **Falha fechada do `--vermelho` mantida** (`bin/forge-testes:90`). `TESTE_DO_DIFF` passa a manter no HEAD `tests/<pacote>/.../test_*.py`; o resto de `tests/` segue produção e volta à base. Sonda local só da expressão: `tests/catraca.py`, `tests/neutralidade.py`, `tests/evals/__init__.py` e `tests/evals/apoio.py` não casam (voltam à base); `tests/evals/test_x.py` e `tests/a/b/test_x.py` casam. Os segmentos são `[a-z0-9_]+`, sem `.`, então `..` não entra (`tests/evals/../../bin/test_x.py` não casa). Um autor não consegue manter código de apoio da catraca no HEAD só por pô-lo num subpacote: precisa do prefixo `test_`, que já valia na raiz.
- **Nome de módulo da linha de comando** (`bin/forge-testes:92`, `:941`, `:405`). `NOME_DE_MODULO` só aceita `[a-z0-9_]` separados por `.`, termina em `test_<nome>` e recusa o prefixo `tests.` repetido (lookahead); `../test_x`, `evals/test_x`, `a..test_x` são recusados. Depois disso o nome precisa estar em `todos`, a lista tirada dos arquivos reais de `tests/` (`:785`, `:788`); só então chega ao `loadTestsFromName(f"tests.{modulo}")` (`:648`) e ao nome do registro em `trabalho/` (`:821`), que não ganha `/`. Não há importação arbitrária nem escrita fora da pasta temporária.
- **Custo de expressão** (entrada livre de linha de comando): as duas expressões não têm ambiguidade (o separador não está na classe); 50 mil segmentos casam em 9 ms no total. Sem caminho de negação de serviço.
- **Caminho na árvore da base** (`bin/forge-testes:402`, `:715`): `arquivo_do_modulo` só recebe nome já validado; `git ls-tree`/`git show` leem o objeto da âncora, sem execução.
- **Mutantes**: 11 mutantes com executor `unittest` e duas isenções com motivo (`tests/mutantes/vermelho-tests-evals.json`); são dados, não código executado pela ferramenta fora do executor já existente.
- Observação de estilo, fora da segurança, ao `tech-lead`: o docstring de `nome_do_modulo` (`bin/forge-testes:406`) diz que confere se cada pasta é pacote, mas o código não olha `__init__.py`; um `test_*.py` em pasta que não é pacote entraria em `todos` e falharia por importação nas duas cópias (resultado `falha no HEAD`, rc 1: falha fechada, não aprovação falsa).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: leitura do diff, sonda local da expressão (biblioteca padrão), consulta pública de check-runs do head (vazia). Faltaram no PATH: o varredor de segredos e o SAST da lista da skill (lacuna registrada; o diff não tem segredo nem dependência nova).
