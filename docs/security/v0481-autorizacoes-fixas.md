---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-autorizacoes-fixas
commit: 39b5b066122f8f6c1883aef2bd692b147d05d8a1
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: v0481 (E14.77, #901, AUTORIZACOES-FIXAS, volta por delta)

Delta lido: `forge-check parecer delta` de `4c88ca81..39b5b066`. No domínio entra só `bin/forge-fechar:674`. Os outros dois arquivos são pareceres (o de review e o anterior deste portão) e ficam fora do domínio. A 1ª rodada (aprovada no `4c88ca81`) fica no git e não é recopiada aqui.

- ci: 39b5b066122f8f6c1883aef2bd692b147d05d8a1 verde

CI do head (run 45751838425): as 10 partes da suíte, os dois tetos de pulados, `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `catraca` e `árvore já provada na develop` estão verdes. Há dois vermelhos, e os dois vêm da própria construção. `bateria (pareceres)` cai em R-REVIEW porque o parecer de review ficou desatualizado depois que `bin/forge-fechar` mudou (job 139682013252). O agregador `bateria` cai só por `pareceres: failure` e registra `partes: success` (job 139685070775).

Rodado aqui: `python3 -m unittest tests.test_fechar tests.test_fechar_corte tests.test_fechar_limpar_clone` (161 testes, OK) e `shellcheck bin/forge-fechar` com o 0.9.0 (rc 0). Nenhuma spec em `tests/mutantes/` tem a linha antiga como texto-alvo, então não há mutante tocado.

Gatilhos: controle do Forge (`forge-fechar`, limpeza de clones; R-CONFORMIDADE), sem mudança nos gatilhos da 1ª rodada.

## O que aperta, o que é neutro e o que afrouxa
**Aperta:** nada.

**Neutro:** `comum="$(if cd "$(git rev-parse --git-common-dir)"; then pwd -P || true; else :; fi)"` (`bin/forge-fechar:674`) tem o mesmo efeito de `cd ... && pwd -P || true`. Com o `cd` bem-sucedido, sai o caminho físico. Com o `cd` falho, sai vazio com rc 0. Com o `git rev-parse` vazio, o `cd ""` do bash não sai do diretório e as duas formas devolvem o diretório corrente. A sonda S1 confere os três casos. A variável continua servindo só para comparar com o diretório comum de cada clone em `~/.forge-contrib/wt/`, e nenhum caminho novo de remoção nasce daí.

**Afrouxa:** nada.

## Sondas
- S1 · script em arquivo com as duas formas aplicadas a um link para diretório, a um caminho inexistente e à cadeia vazia · espera: saída e rc iguais nas duas formas · obtido: iguais nos três casos (caminho físico, vazio com rc 0, diretório corrente)

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Ferramentas: `forge-check parecer delta`, `git diff`, `shellcheck` 0.9.0, os três módulos de teste e o `gh api` dos check-runs e dos logs dos dois jobs vermelhos. Sem varredura de segredos ou dependências, porque o delta não tem dependência nem credencial.
