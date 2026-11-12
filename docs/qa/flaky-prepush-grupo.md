---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/flaky-prepush-grupo
commit: 905edbbb3bb529646fcfa4dbdac0f724ec0f23f5
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: flaky-prepush-grupo (E26.7)

## Achados
- A1 (bloqueante) tests/test_prepush_so_docs.py:313 · vigia() casa o `sleep 60` irmão de lanca(): ele é filho do mesmo PID (o bash -c faz exec do hook), nasce antes do arquivo `etapa` e não é a etapa, então devolve True de imediato e a espera não prova que o hook chegou ao laço; exclua o PID de `irmao`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Obrigação: o SIGTERM só sai com o hook já no laço de vigia (substitui o sleep fixo de 1 s) | GrupoDaEtapa.interrompe (usado por test_term_no_hook..., test_grupo_nao_criado...) | corrida entre alvo=-etapa (pre-push:126-127) e o TERM | não passou: a condição é satisfeita antes do laço (A1) |
| Asserções iguais | diff c340c322..905edbbb | n/a | passou (só a espera mudou) |

## Cenários e resultado real
- Leitura do diff (git show): em lanca() o bash -c faz `sleep 60 & echo $! > irmao; exec .githooks/pre-push`, logo o irmão tem ppid == p.pid == `hook`. vigia() aceita qualquer `sleep` com ppid == hook e pid != etapa; o irmão cumpre as duas condições desde antes da etapa existir. O ganho sobre o sleep(1) fica só no `ate(...)` retornar na primeira volta (~0 s), ou seja, a espera some em vez de crescer: a janela passa a ser menor que a de antes (0,2 s do le(); o 1 s sai) e a instabilidade tende a piorar.
- Causa provável do stderr vazio: TERM chegando entre `alvo=$!` e a troca para `-$etapa` (pre-push:125-127, dois `ps` em subshell), ou com o hook ainda fora do laço, sob carga. A intenção da mudança (esperar o laço) pega essa causa; a implementação não.
- Sandbox: GrupoDaEtapa roda 4 testes e pula todos (/proc de outro namespace); não consegui executar a vigia nem reproduzir. O achado A1 vem de leitura, com a premissa de exec preservar o PID, que é semântica do bash. Não houve vermelho/verde possível aqui.
- O que o CI precisa mostrar para dar a instabilidade por resolvida: (1) os 4 testes de GrupoDaEtapa executados, sem `skipped`, no check-run `bateria` do sha final; (2) vigia ligada ao laço (teste mostrando que a espera aguarda de fato, por exemplo ao menos um `sleep` filho do hook que não seja etapa nem irmão); (3) repetição sob carga: o job do PR e re-runs em série, sem repetir o stderr vazio (uma execução verde não prova nada, a falha original era intermitente).
- Sem plano antecipado, mutação nem forge-mutante: não toca bin/, hooks/ nem .githooks/; só teste.
