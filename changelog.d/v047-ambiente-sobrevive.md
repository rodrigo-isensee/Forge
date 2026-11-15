### Corrigido
- Container recriado volta pronto sozinho (E2.54): o postStartCommand do devcontainer do Forge e do modelo de projeto refaz gh, login pelo GH_TOKEN do ambiente, o link ~/.forge-contrib e o core.hooksPath lendo o script da origin/main (não o do work tree); preparar-estacao.sh ganha --verificar, que imprime o comando exato do que falta para o Jarvis abrir com ele
