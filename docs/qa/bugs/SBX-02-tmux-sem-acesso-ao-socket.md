# SBX-02 - `tmux ls` e `tmux has-session` falham com "Operation not permitted"
- Status: limite documentado (rodada 1 de correção; o QA revalida). `excludedCommands` só vale com o comando exato e sozinho: pipe, redirecionamento, `cd` ou encadeamento devolvem a chamada ao sandbox. `tmux ls` puro funciona (README, "Sandbox do Bash").
- Severidade: média (funcionalidade secundária; contorno simples: rodar `tmux ls` no terminal fora do Claude)
- Responsável sugerido: dono do Forge (`excludedCommands` está em `.claude/settings.json`, protegido); revisão pelo `tech-lead`
- Ambiente: branch `melhoria/sandbox-bash`, commit 4b9a502, Linux/WSL2, tmux 3.4, sessão tmux ativa (`TMUX=/tmp/tmux-1000/default,1566,1`)
- Revalidação (6e0ff68, rodada 1): `tmux ls` puro, sem pipe, rodado de novo na sessão com a configuração ativa: mesmo erro (`error connecting to /tmp/tmux-1000/default (Operation not permitted)`, rc 1). A configuração ativa é a anterior à branch; a correção documentada (`excludedCommands` exato) só vale após merge e reinício. Pendência: rodar `tmux ls` sozinho depois do reinício. Se falhar com a configuração da branch, este bug reabre como média.

## Passos para reproduzir
1. Na raiz do Forge, com o sandbox ativo: `tmux ls`
2. Ou: `tmux has-session`

## Resultado esperado
Ambos rodam fora do sandbox (`excludedCommands`: `tmux ls`, `tmux has-session *`, `tmux capture-pane *`) e listam as sessões. O README diz: "Só `tmux capture-pane`, `tmux ls` e `tmux has-session` rodam fora do sandbox."

## Resultado obtido
```
error connecting to /tmp/tmux-1000/default (Operation not permitted)
rc=1
```
Igual para `tmux has-session`. O diretório `/tmp/tmux-1000` existe (`drwx------`, dono `rodrigoisensee`), e há um servidor tmux ativo (pid 1566), então o erro vem do acesso ao socket e não de ausência de servidor.

## Evidência
Saída literal acima, reproduzida com o comando isolado (sem pipe), o que descarta o problema de casamento de padrão com pipe.
