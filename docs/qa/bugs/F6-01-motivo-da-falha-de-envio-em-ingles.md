# F6-01 - motivo da falha de envio aparece em inglês
- Severidade: baixa
- Responsável sugerido: forge:shell-dev (ou o agente de desenvolvimento da stack do script)
- Ambiente: melhoria/primeiro-uso-f6 @ e0d6d1c, `bin/forge-sugerir`

## Passos para reproduzir
1. Projeto temporário, HOME temporário, `gh` falso que escreve `error connecting to api.github.com` no stderr e sai com 1.
2. Num terminal (pty), fora do Claude: `forge sugerir "problema observado: x"` e responder `s`.

## Resultado esperado
Mensagem inteira em português claro, para quem não programa.
## Resultado obtido
`Não consegui enviar (error connecting to api.github.com). Guardei em ...; quando houver rede: forge sugerir --fila`. O trecho entre parênteses é a primeira linha crua do `gh`, em inglês. O texto fica na fila e o código de saída é 1, como previsto.
## Evidência
Saída do passo 3 da seção "Exploratórios" de `docs/qa/primeiro-uso-f6.md`.
