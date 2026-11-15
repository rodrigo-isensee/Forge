---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-catraca-hook-por-script
commit: 9811ca977485b35c7c85f6882097a96c8e834141
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (CATRACA-HOOK-POR-SCRIPT, E2.53; review E2.61)

Intervalo `origin/develop..9811ca97` (base cb45a962), um commit, 4 arquivos; código e teste: 55 linhas (`tests/catraca.py` 18+10, `tests/test_catraca.py` 27+0), dentro do teto M14. Revisor: instância que não fez a entrega.

## Achados
- A1 (recomendado) tests/catraca.py:276 · A chave é um conjunto (evento, matcher, script): dois hooks com o mesmo script e argumentos diferentes no mesmo grupo viram uma chave, e remover um passa calado (sonda: x.sh --modo a/b, tirar o b dá diferença vazia). Sem gatilho no hooks.json do Forge; em projeto, pode contar as chaves (Counter).
- A2 (recomendado) tests/catraca.py:263 · Caminho do script entre aspas no command (`python3 "${CLAUDE_PLUGIN_ROOT}/hooks/x.py"`) não casa o sufixo e cai na linha inteira: trocar o interpretador volta a acusar hook removido. Sem gatilho no Forge; tirar aspas do termo antes do teste do sufixo.

## Sondas

## Parecer
**Aprovado.** Atende à ordem do dono (pedido v047, 2026-11-15 07:18): a catraca compara cada hook por evento e script, e o matcher entra na chave, o que é correto (mudar o matcher muda a cobertura; `test_matcher_mudado_barra`). O falso positivo do PR 565 (só `-s -E`) deixa de acusar (`test_mudar_interpretador_opcoes_ou_argumentos_passa`), a troca de script segue barrando (`test_script_trocado_barra`) e o hook sem script compara a linha inteira (`test_hook_sem_script_compara_a_linha_inteira`). A mensagem de `regra_hooks` cita o script, com o ID `R-CONFORMIDADE`.

Leitura: função pequena e nomeada, docstring com o motivo (PR 565), sem código morto; o comentário antigo sobre `-s -E` saiu junto com o filtro que ele explicava. JSON inválido segue devolvendo conjunto vazio (inalterado). Conferido contra o `hooks/hooks.json` atual: os 18 hooks têm script `.py` nos argumentos e nenhum repete script no mesmo evento e matcher, então A1 e A2 não disparam aqui.

Guardas: uma linha de guarda mudada (`tests/catraca.py:265`), um mutante declarado (CH-M1), com teste de comportamento do ramo de falha.

Verificadores citados, sem refazer a suíte (roda no CI do PR; o item ainda não tem PR):
- `bin/forge-mutante tests/mutantes/v047-catraca-hook-por-script.json`: `CH-M1 · morreu · tests/catraca.py:265` (rev 9811ca977485).
- `python3 -m unittest tests.test_catraca.Hooks`: `Ran 6 tests ... OK`.

Commits: um commit Conventional Commits em português, com o ID do cartão e a etapa; fragmento em `changelog.d/` (seção Corrigido).
