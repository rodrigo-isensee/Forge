---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-limpar-clone
commit: 5ff5fb4cf68646f8a09fc909df5bc927b9844e1c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança por delta: v0478 (E132.16, PR #831 depois da volta E132.13)

A rodada anterior (E132.12, aprovado no commit `7ba9f0ba`, sem achados) está no git. Esta rodada leu só o delta `7ba9f0ba..5ff5fb4c` que `forge-check parecer delta` mostra no domínio: `bin/forge-fechar`, `tests/test_fechar_config.py` e `tests/test_fechar_limpar_clone.py`. Fora do domínio ficou `tests/mutantes/v0480-fechar-limpar-clone.json`.

Gatilhos: controle do Forge (`bin/forge-fechar`, que apaga clone em `~/.forge-contrib/wt`), busca só de leitura da origin.

## Só aperta ou neutro, por escrito
- **`bin/forge-fechar:607-611` (`sem` vira `sem_busca`), neutro:** só troca o nome do array local de `origem_atual`. O conjunto buscado é o mesmo: pontas e heads mesclados, só sha40, só os que faltam. O fetch continua só de leitura em `buscar_de` (`:592`). `sem_busca` não aparece em nenhum outro ponto do script, e `pontas` continua indo ao `local` de `limpar_clones`. O motivo é o SC2100 em `st=sem-pass`, que não é de segurança.
- **`tests/test_fechar_limpar_clone.py:48-65`, aperta:** o teste novo prova que um head mesclado que esta cópia não lê, com a branch já apagada da origin, é buscado. Também prova que o clone ancestral desse head sai. Ele mata o mutante que tira os mesclados da busca. Nenhuma asserção ficou mais fraca.
- **`tests/test_fechar_config.py:104`, neutro:** muda só o nome do teste. A asserção não muda.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
- **Testes dos arquivos tocados no head `5ff5fb4c`:** `tests.test_fechar_limpar_clone` e `tests.test_fechar_config` deram 12 OK em `LC_ALL=C` e 12 OK em `C.UTF-8`. `bash -n bin/forge-fechar` passou.
- **Suíte inteira:** não rodou aqui, porque o brief a pede sem suíte local. Vale o CI do PR #831 no head, obrigatório para o merge.
- **Lacunas:** `shellcheck` e `gitleaks` não estão nesta estação. O SC2100 fica com a `bateria (verificações longas)` do CI.
