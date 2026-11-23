---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-copia-nome-unico
commit: 950115403000c469798f92046bce95713ddfb5b3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · E111.2 · CLONE-NOME-UNICO (forge-copia)

Delta lido: 900bfdfe..95011540 (primeira rodada; 6 arquivos, 36 linhas de código em `bin/forge-copia`, dentro do teto H1, um comportamento).

## O que conferi
- Requisito: destino ocupado continua recusado (saída 2, nada criado nem reusado); a recusa agora diz a branch da cópia git que está lá e sugere `<branch-sem-prefixo>-<papel>` livre na mesma pasta, com `-2`, `-3`... Faz o pedido, sem mais.
- `tomado` só lê a branch se o destino tem `.git` próprio (não confunde com o repositório em volta) e roda o git com `core.fsmonitor=` vazio e `--no-optional-locks`: leitura sem execução de configuração alheia.
- `--papel` validado por `[a-z0-9][a-z0-9-]*` antes de qualquer criação; o nome sugerido fica em `dirname(real)`, que já passou pela guarda da pasta liberada, então não sai dela.
- `limpar` sai antes de `destino_dentro`; não muda.
- Guardas do diff com um mutante por linha: `tests/mutantes/v0480-copia-nome-unico.json` M1..M5 e o M5 de `v0475-copia-pasta.json` atualizado para a linha nova.
- Testes de comportamento do ramo de falha, subprocesso com ambiente limpo e `python -I` (AR-4).

## Ferramentas (citadas, não refeitas)
- `bin/forge-mutante --processos 1 tests/mutantes/v0480-copia-nome-unico.json`: M1..M5 morreram (linhas 79, 86, 95, 97, 265).
- `bin/forge-mutante --ids M5 tests/mutantes/v0475-copia-pasta.json`: M5 morreu (linha 112).
- `bin/forge-mutante --cobertura --base 900bfdfe`: saída 0; toda guarda do diff coberta (o `tests/pesos-d4.json` é dado, sem guarda).
- `python3 -m unittest tests.test_forge_copia_nome tests.test_forge_copia`: 74 testes, OK.
- Suíte completa: fica no CI do PR sobre a develop atual (a base andou).

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/ritmo-e-corte.md:43 · o passo da cópia extra ainda diz `wt/<item>` sem `--papel`; citar o nome único `<item>-<papel>` e a opção evitaria a recusa na primeira tentativa (CLONE-NOME-UNICO).
