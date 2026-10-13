# SBX-02 - `tmux ls` e `tmux has-session` falham com "Operation not permitted"
- Severidade: média (funcionalidade secundária; contorno simples: rodar `tmux ls` no terminal fora do Claude)
- Responsável sugerido: dono do Forge (`excludedCommands` está em `.claude/settings.json`, protegido); revisão pelo `tech-lead`
- Ambiente: branch `melhoria/sandbox-bash`, commit 4b9a502, Linux/WSL2, tmux 3.4, sessão tmux ativa (`TMUX=/tmp/tmux-1000/default,1566,1`)

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
