# JFV-01 - Diretório existente sem .git é apagado pelo jarvis-forge

- Severidade: crítica (perda de dados; gatilho raro)
- Responsável sugerido: node-backend (script de infraestrutura `scripts/jarvis-forge`)
- Ambiente: branch `melhoria/jarvis-forge-vigente`, commit b51cd3a, Linux (bash), execução com HOME e XDG_DATA_HOME temporários e origin local de teste; claude e tmux substituídos por stubs

## Passos para reproduzir
1. Criar um diretório com conteúdo do usuário no caminho da cópia vigente, sem `.git`: `mkdir -p $XDG_DATA_HOME/forge/vigente && echo importante > $XDG_DATA_HOME/forge/vigente/nao-apagar.txt`.
2. Rodar `XDG_DATA_HOME=... scripts/jarvis-forge --sem-tmux`.
3. Conferir se o arquivo ainda existe.
4. Repetir o passo 1 e rodar `scripts/jarvis-forge --atualizar-vigente`.

## Resultado esperado
O script recusa (saída diferente de zero, mensagem clara) e não apaga nada que não criou. O diretório e `nao-apagar.txt` continuam existindo.

## Resultado obtido
Nos dois casos o script sai com código 1 (`fatal: destination path ... already exists and is not an empty directory`) e, em seguida, `criar_vigente` executa `rm -rf "$vigente"`. O diretório e o arquivo do usuário são removidos. Mensagem final: `jarvis-forge: não consegui criar a cópia vigente.`

## Evidência
Saída do harness (cenários T10.1 e T10.2): `dir existe: NAO` e `arquivo existe: NAO` depois de cada execução. Trecho causador em `scripts/jarvis-forge`, função `criar_vigente`: `if ! git clone ...; then rm -rf "$vigente"; ...`. A remoção é incondicional, mesmo quando o diretório já existia antes da chamada.
Correção sugerida (para quem corrige, não aplicada aqui): tratar como erro qualquer caminho existente sem `.git` antes do clone, ou clonar em diretório temporário e mover só se der certo; remover só o que o próprio script criou.
