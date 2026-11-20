# v0479-ae2-c1-tag-com-digito-unicode - tag com dígito não ASCII vira marca
- Severidade: baixa
- Responsável sugerido: tech-lead (autor do AE2 C1)
- Ambiente: melhoria/v0479-ae2-c1-contagem @ aa8e521a, python3 -I

## Passos para reproduzir
1. Repositório com a tag `v0.47.11` e a tag `v٩.٩.٩` (dígitos arábico-índicos).
2. `contar(raiz)` com `refs/remotes/origin/develop` no commit.

## Resultado esperado
Tag fora da forma ASCII `v<n>.<n>.<n>` é ignorada (a docstring de `TAG_DE_VERSAO` diz que fora da forma não é marca); versão em curso `0.47.12`.

## Resultado obtido
`versao` = `9.9.10`. O mesmo vale para `MERGE_DE_PR` e `SQUASH_DE_PR` (`\d` aceita dígito Unicode no número do PR).

## Evidência
`bin/forge_contador.py:25-27`: `\d` sem `re.ASCII`. Reproduzido com o script do passo 1 (saída `9.9.10`). Corrigir com `[0-9]` ou `re.ASCII`.
