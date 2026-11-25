### Corrigido
- `forge-fechar --limpar`: o clone de parecer (`-qa`, `-rev`) limpo e já mesclado sai. A tag local (a `arquivo/*` que a origin apagou) não conta mais como trabalho fora da origem, e o commit do clone que é ancestral do head do PR MERGED vale como mesclado mesmo com a ref remota da branch apagada; stash, branch local e commit depois do head mesclado seguem pendentes (v0481 E14.1).
