---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-fila-suite-espera
commit: 1e04c56fe51c0165e112a1fcd5aab23ea52cc666
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
data: 2026-11-14
---
# QA: v047-fila-suite-espera

Pedido de controle (`.githooks/pre-push`), sem especificação de UX nem contrato de API; as obrigações são as da linha E1.131 do pedido v047 (FILA-SUITE-ESPERA): posição na fila, aviso de trava velha (sem liberar nem pular a fila), registro dos envios barrados. Diff conferido: `origin/develop..1e04c56f` (6 arquivos: hook, `docs/hooks.md`, fragmento de changelog, teste e 2 specs de mutantes). O remoto avançou para `0eeaa303` com só pareceres de review e segurança; trazido por merge, sem rebase.

## Achados
- A1 (recomendado) .githooks/pre-push:408 · `FORGE_FILA_INTERVALO=0` passa na validação e imprime a linha da fila a cada ciclo de 0,2 s (reproduzido: 12 linhas em 3 s). Sem efeito na suíte; rejeitar 0 ou impor mínimo (R-TETO, ruído do hook).
- A2 (recomendado) tests/test_pre_push_fila.py:142 · Na base, `test_barrado_registra_uma_linha_por_envio` cai por erro (`read_text` de arquivo ausente), não por asserção: o vermelho sai "sem veredito" (rc=2). Assertar a existência do registro antes de ler. F9 e F12 já o matam (R-QA).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Posição e quem está na frente ao entrar | test_posicao_e_quem_esta_na_frente_ao_entrar | pid sem hora (`?`), 1 linha por intervalo | passou; vermelho na base (asserção) |
| Fila que é link não é listada | test_fila_que_e_link_nao_e_listada | link simbólico | passou; vermelho na base (asserção) |
| Atualiza a cada intervalo; intervalo inválido recusado | test_atualiza_a_cada_intervalo_e_intervalo_invalido_e_recusado | `1m` (não inteiro) | passou; vermelho na base (asserção) |
| Dona morta avisa uma vez e não libera | test_dona_morta_avisa_uma_vez_e_nao_libera | trava segue presa | passou; vermelho na base (asserção) |
| Dona viva, outro namespace, pid não numérico: sem aviso | test_dona_viva_ou_de_outro_namespace_nao_avisa | `x1`, `-99999`, ns `1` | passou; passa na base (guarda negativa, coberta por F6, F7, F13) |
| Trava sem troca de dona há mais de 35 min avisa | test_trava_sem_troca_de_dona_ha_mais_de_35_min_avisa | 36 min | passou; vermelho na base (asserção) |
| Barrado registra uma linha por envio (push e suite) | test_barrado_registra_uma_linha_por_envio | espera estoura em até 20 s | passou; base: erro (A2); F9 e F12 matam |
| Registro que é link não é seguido | test_registro_que_e_link_nao_e_seguido | link simbólico | passou; passa na base (guarda negativa, coberta por F10) |

## Cenários e resultado real
- Suíte do módulo no head: `python3 -m unittest tests.test_pre_push_fila`: 8 testes, OK (28,6 s).
- Suíte inteira: check-run `bateria` do sha 1e04c56f: success (run 43597037335; também `suíte` 3.12 e 3.14 partes 1 a 3, success). O check `catraca` falha neste sha e em 0eeaa303 (pede o rótulo do dono, já sabido no pedido); não é do domínio do QA.
- Vermelho antes do verde (módulo restrito, a suíte inteira passa pelo CI; a execução inteira local não terminou em tempo útil):
```
vermelho: base=e60183d0a41d head=1e04c56fe51c módulos=test_pre_push_fila (restrito por --modulos)
revertidos à base: .githooks/pre-push, changelog.d/v047-fila-suite-espera.md, docs/hooks.md
contagem: não prova (passa na base)=2; prova (asserção)=5; sem veredito=1
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.   rc=2
```
  Cinco provam por asserção; os dois que passam na base são guardas negativas, provadas por mutantes; o sem veredito é A2.
- Cobertura: `forge-mutante --cobertura --base e60183d0...` sai `não coberto: .githooks/pre-push` (shell: declarado, não provado), rc=0. Conferi a lista contra as linhas de guarda do diff: 14 mutantes cobrem validação do intervalo, cadência, contagem da posição, fila link, aviso único, namespace, pid numérico, 35 min, modo do registro, link do registro, laço da trava, limite da espera, kill -0 e "No such process". Sem guarda mudada sem mutante, salvo a chamada `registrar_barrado` em `barrar` (matada de fato por F9/F10, que dependem do arquivo).
- Mutantes (`forge-mutante --processos 4` das duas specs, rev 1e04c56fe51c): F1 a F14 todos `morreu`, rc=0, nenhum sobrevivente.
- Exploração: `FORGE_FILA_INTERVALO=0` com espera de 3 s imprime 12 linhas de fila (A1). Intervalo inválido, fila link e registro link: recusados ou ignorados como esperado; nenhum caminho libera a trava ou pula a fila.

## Bugs
- Baixo (cartão, sem aceite do usuário, R-QA): A1, ruído de `FORGE_FILA_INTERVALO=0`. Responsável: quem mantém o `pre-push` (tech-lead).
