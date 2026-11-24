---
tipo: revisao-devops
contrato: 1
pedido: v0478
branch: melhoria/v0480-ci-anotacao
commit: 3487d89164ca7a88c317a071707d168196fa08f3
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-23
---
# Review de devops: v0480-ci-anotacao

## Achados
- A1 (recomendado) scripts/suite-partes.py:310 · por_duas_partes ainda lê os.environ direto em numero_de_processos; hoje só usa variáveis que o discover não toca. Passar o `environ` copiado fecharia a mesma classe de erro.

## Detalhes
Aprovado. PR #821, head 3487d891, base 0e59c446. Nada em `.github/` (0 arquivos); o item mexe em `scripts/suite-partes.py`, que o CI roda por parte.

Efeito no CI: o `discover` da divisão importa `tests/test_catraca.py`, que faz `os.environ.pop("GITHUB_ACTIONS")` no import (linha 30). Como `main` guardava a referência a `os.environ`, `por_parte` via `GITHUB_ACTIONS` vazio e calava a anotação `::error title=forge-suite parte K/N` e a `::notice title=forge-tempos`. A correção copia o ambiente (`dict(os.environ)`) antes do discover, e `emitir_falha` (linha 232) e `anotar` (linha 407) leem a cópia. O `filho_env` de `por_duas_partes` (linha 267) também sai da cópia. Não muda código de saída, divisão de partes nem número de processos. Sem passo novo, sem cache, sem artefato, sem ação de terceiros.

Prova do teste: o novo `test_modulo_que_tira_github_actions_no_import_nao_cala_as_anotacoes` reproduz o import que tira a variável (4 partes verdes com notice, 1 vermelha com error); o mutante M1 em `tests/mutantes/v0480-ci-anotacao.json` desfaz a linha e é pego por esse teste. Rodei `python3 -m unittest tests.test_suite_partes`: 50 testes, OK (só o arquivo tocado, sem suíte). O mutante em si não foi rodado por mim.

Ferramentas: `actionlint` e `shellcheck` não se aplicam (sem workflow nem shell tocado) e não foram rodados; o CI do PR traz a bateria completa.

## Custo e rollback
Custo zero (`R-CUSTO`): nenhum minuto novo de CI, nenhum serviço, cache ou artefato; só volta a emitir duas linhas de anotação por parte. Rollback: reverter o commit 3487d891 (uma linha em `scripts/suite-partes.py`), sem migração.
