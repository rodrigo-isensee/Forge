# AA1-04 - aviso de leitura e erro de caminho imprimem o caminho (usuário e projeto)
- Severidade: baixa (a saída de dados é anonimizada; o caminho vai ao stderr/terminal local)
- Responsável sugerido: dev do `forge-check`
- Ambiente: melhoria/anti-alucinacao-medicao-fix @ dab099a

## Passos para reproduzir
1. `bin/forge-check transcricao lastro ~/.claude/projects/<pasta-do-projeto>` e ler o stderr.
2. `bin/forge-check transcricao lastro` numa pasta sem sessões (stdout).
## Resultado esperado
Coerência com a frase impressa: "a saída traz só números, nunca texto, nome ou caminho".
## Resultado obtido
Passo 1: `vai ler 282 arquivo(s) .jsonl em /home/<usuario>/.claude/projects/-home-<usuario>-Forge; ...`. Passo 2: `caminho inexistente: /home/<usuario>/.claude/projects/-home-...` no stdout, que é o canal que um relatório colaria. As linhas de sessão e total (stdout) não vazam nada.
## Evidência
Grep `<usuário>|<projeto>|/home` no stdout de `lastro` e `decisoes` sobre a pasta real: 0 ocorrências; no stderr, a linha de anúncio traz o caminho.
