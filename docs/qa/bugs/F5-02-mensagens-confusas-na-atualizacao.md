# F5-02 - mensagens confusas para quem não programa (texto do doutor no meio, "Pronto" seguido de "Algo não saiu", Ctrl-C)
- Severidade: baixa
- Responsável sugerido: forge:tech-lead (`bin/forge-atualizar`, `bin/forge-voltar-versao`)
- Ambiente: melhoria/primeiro-uso-f5 @ e532702

## Passos para reproduzir
1. `forge atualizar` com resposta `s`, caminho feliz: depois de "Plugin: ... fixado na versão 9.9.0." sai um bloco "Forge doutor: 1 coisa para ver - O projeto está na versão 0.12.0 ... atualize o projeto com `forge-upgrade --simular` ... depois `forge-upgrade`", no meio da própria atualização, seguido de "Pronto: ... o doutor não achou nada novo".
2. Com um doutor que acha problema novo: aparece "Pronto na branch forge/upgrade-9.9.0. Revise o diff..." e logo depois "Algo não saiu como esperado" e "Voltar para a versão 0.12.0?".
3. Mande SIGINT durante o `marketplace add` (a fixture `sigint-no-add`); depois rode `forge voltar-versao`.

## Resultado esperado
Um texto só por etapa, sem pedir à pessoa um comando que o próprio `forge atualizar` está rodando; sem "Pronto" antes de "Algo não saiu"; depois do Ctrl-C, a mensagem fala da realidade (nada foi atualizado).

## Resultado obtido
1 e 2 como descritos (mistura de avisos; jargão "doutor", "branch", "pull request", "marca", "ponto de retorno" sem explicação). 3: a marketplace volta ao original, mas ficam o ponto e a marca; `voltar-versao` diz "Vou voltar o Forge da versão 9.9.0 para a 0.12.0" (a 9.9.0 nunca foi instalada) e fixa o plugin na tag 0.12.0, que antes estava sem fixação. Nada se perde. É o recomendado já registrado na terceira review (ponto e marca que ficam no Ctrl-C).

## Evidência
Saídas completas obtidas na exploração (ver `docs/qa/primeiro-uso-f5.md`).
