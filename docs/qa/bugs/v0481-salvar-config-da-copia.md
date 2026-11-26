# v0481-salvar-config-da-copia - o git do salvar executa comando do .git/config da cópia
- Severidade: alta
- Responsável sugerido: desenvolvedor do hook (`hooks/salvar.py`)
- Ambiente: melhoria/v0481-d6-resto @ 9a708f86c, python3, git local

## Passos para reproduzir
1. Repositório temporário com `git config filter.x.clean "touch <marca>; cat"` e `.gitattributes` com `*.txt filter=x`.
2. Importar `hooks/salvar.py` e chamar `git_da_copia(<repo>, "add", "-A", "--", "a.txt")`.

## Resultado esperado
Nenhum comando vindo do config da cópia roda no hook, que está fora do sandbox.

## Resultado obtido
A marca é criada: `filtro do .git/config executou: True`. Também alcançam o hook `core.sshCommand`, `gpg.program`, `credential.helper` e `remote.origin.receivepack`.

## Evidência
Saída da sonda acima. `GIT_SEGURO` só neutraliza `core.hooksPath` e `core.fsmonitor`. Sugestão: neutralizar por `-c`, ou não agir com chave local fora de uma lista de permitidas; teste novo com vermelho antes do verde.
