# F6-02 - `--guardar` fora da primeira posição diz "opção desconhecida"
- Severidade: baixa
- Responsável sugerido: forge:shell-dev (ou o agente de desenvolvimento da stack do script)
- Ambiente: melhoria/primeiro-uso-f6 @ e0d6d1c, `bin/forge-sugerir`

## Passos para reproduzir
1. `CLAUDECODE=1 forge-sugerir "texto" --guardar`

## Resultado esperado
Nada é enviado (ok) e a mensagem explica que `--guardar` precisa vir primeiro.
## Resultado obtido
Sai com 2, sem enviar e sem chamar o `gh` (comportamento seguro), mas diz `opção desconhecida: --guardar`, que confunde: a opção existe.
## Evidência
Passo 4e dos exploratórios em `docs/qa/primeiro-uso-f6.md`.
