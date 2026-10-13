# JFV-02 - Commit local na cópia vigente é descartado sem aviso

- Severidade: média (perda de commit local; recuperável pelo reflog até o `gc`)
- Status: resolvido (6432242)
- Responsável sugerido: node-backend (script de infraestrutura `scripts/jarvis-forge`)
- Ambiente: branch `melhoria/jarvis-forge-vigente`, commit b51cd3a, Linux (bash), HOME e XDG_DATA_HOME temporários; origin local de teste

## Passos para reproduzir
1. Rodar `scripts/jarvis-forge --sem-tmux` para criar a cópia vigente.
2. Na cópia vigente, criar e commitar um arquivo novo (sem push): `git -C $XDG_DATA_HOME/forge/vigente add local.txt && git commit -m local`.
3. Rodar `scripts/jarvis-forge --atualizar-vigente`.
4. Conferir `git -C .../vigente log --oneline -1`.

## Resultado esperado
Como o `--atualizar-vigente` diz "recusa se tiver mudanças locais" (cabeçalho do script e README), a atualização deve recusar com mensagem, sem mover o HEAD, ou deixar explícito o descarte do commit.

## Resultado obtido
O script exibe `cópia vigente atualizada para origin/develop`, sai com código 0 e faz `git reset --hard origin/develop`. O commit local some do HEAD. Ele só continua no reflog, sem aviso ao usuário.

## Evidência
Saída do harness (cenário T11.1): rc=0, `cópia vigente atualizada para origin/develop (a2e58b5)`, HEAD movido. `git reflog` da cópia mostra `commit: local` seguido de `reset: moving to origin/develop`. Causa: `git -C "$vigente" reset --quiet --hard origin/develop`, depois de a checagem olhar só `git status --porcelain` (arquivos), que não vê commits à frente do remoto.
Correção sugerida: recusar também quando `git rev-list origin/develop..HEAD` não estiver vazio, ou ajustar a documentação para dizer que commits locais são descartados.

## Resolução
Resolvido e verificado na revalidação do commit 6432242 (2026-10-13): cenário reproduzido com stubs e origin local, sem recorrência.
