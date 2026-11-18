---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: bf3ce6af7420bc86931931866ef462163b5cec3c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478-testes-prazo (E12.4)

Escopo lido: diff `4182a6b9..bf3ce6af` (7 arquivos; produção só a extração de `pids_do_proc` em `bin/forge_sempre_atual.py`, sem mudança de comportamento). Classe C pelo `forge-check pr` (sensível da catraca). Suíte: não rerrodada (o módulo `test_oraculo_sempre_atual` falha no sandbox também na base, pelo `/proc`; a prova dele é o CI do PR). Rodados os 5 testes novos: `OK`.

## Achados
- A1 (bloqueante) tests/test_hooks.py:121 · R-REVIEW: o critério só prova que o hook não gastou CPU, não que houve carga. Espera fora da CPU (sleep, I/O, trava) passa como carga: S1, 3,8 s a mais de espera, recusa aceita sem carga. Prove a disputa (ex.: ru_nivcsw dos filhos) ou exija liberar.
- A2 (recomendado) tests/test_hooks.py:1222 · a linha PRAZO-CARGA afirma "vez na CPU" sem medir isso; na S1 o tempo faltante era sono. Com o A1 resolvido, a frase passa a ser verdadeira; até lá, diga "sem trabalho de CPU do hook".

## Sondas
- S1 · fixture v0455-merge-com-git-lento-decide-no-prazo-longo com `sleep 4; sleep 3.8;` no 1.o git, por liberar_ou_provar_a_carga · espera: AssertionError (merge passou do prazo longo por espera, não por carga) · obtido: ok, PRAZO-CARGA parede=8.39s cpu=0.14s sono=4s prazo=8s

## Parecer
Reprovado, por um achado (A1), que responde à pergunta do autor: **sim, afrouxa o que o teste prova.**

Antes, o `test_prazo_do_merge` provava que o merge com o git lento de 4 s decide e libera dentro dos 8 s. Agora a recusa do vigia de 8 s passa quando `cpu + sono <= prazo - 1`. A folga de 1 s não sai de carga provada. Sai do tempo de relógio que nem a CPU dos filhos nem o `sleep` conhecido do fixture explicam, e esse tempo tanto pode ser fila de CPU (carga) como espera fora dela: um segundo comando lento, I/O, trava ou timeout de rede no caminho do merge. Um defeito desse tipo, que em produção faz o merge recusar por prazo, deixa o teste verde e imprime "vez na CPU". A S1 prova isso: 3,8 s de espera que não é CPU, 0,14 s de CPU, e o teste aceitou. Continuam pegos o defeito dos 3 s (pela mensagem) e o hook que trabalha demais (pela CPU). Os testes das duas funções novas cobrem bem cada ramo do critério, mas o critério não separa carga de espera.

Correção sugerida (a escolha é do autor): medir a disputa de verdade, por exemplo as trocas de contexto involuntárias dos filhos (`ru_nivcsw` do `getrusage(RUSAGE_CHILDREN)`, que o `sleep` não gera) com um mínimo, ou a parcela de CPU de um processo irmão de referência no mesmo intervalo. Outra saída é o dono aceitar o afrouxamento por decisão registrada no pedido, com critério de reversão.

O resto passa na leitura:
- `descende_de` e a troca de `pids_do_proc` no lançador cobrem só o `forge-sempre-atual`. O ciclo, o órfão e o pid sem leitura têm teste, e M1 a M4 dão um mutante por guarda.
- O subprocesso usa `-I` e ambiente limpo.
- O S14 do `v047-sempre-atual-12.json` acompanha a linha movida.
- A produção não muda de comportamento.
- O fragmento `changelog.d` existe. Com o A1 resolvido, o texto dele ("vez na CPU, não trabalho do hook") precisa acompanhar a correção.
