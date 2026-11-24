---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-copia-nome-unico
commit: f6f1eaf1a22d1b046e953b62135e76d9419284eb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · E111.2, revalidado em E111.6, E111.10 e E111.15 · CLONE-NOME-UNICO (forge-copia)

## Revalidação E111.15 (head f6f1eaf1, volta de CI E111.13)
Delta lido: `forge-check parecer delta` de 04e560fa..f6f1eaf1, sem o que veio da develop (d2288045); no domínio só `bin/forge-testes` (+1).
- A linha nova do `MAPA` (`bin/forge-testes:210`) leva `bin/forge-copia` a `test_forge_copia`, `test_forge_copia_nome` e `test_forge`; trata a falha do run 45252018444 (`MapaCobreOQueOsTestesLeem`: o módulo novo lê o script e a convenção só achava `test_forge_copia`). Os três módulos existem; é dado de mapa, sem guarda nova.
- `bin/forge-testes --listar bin/forge-copia`: dirigido (test_forge, test_forge_copia, test_forge_copia_nome, test_indice_forge, test_oraculo_sempre_atual, test_oraculo_v047).
- `python3 -m unittest tests.test_testes_tocados` (ambiente limpo): 196 testes, OK (skipped=1). Suíte completa: CI do PR.

## Revalidação E111.10 (head 04e560fa)
Delta lido: `forge-check parecer delta` de 2f16f017..04e560fa; no domínio só `tests/pesos-d4.json`, o arquivo do conflito no merge da develop (f17183d1). Desde 2f16f017, fora do merge, só pareceres (6a1a8ce8, a2bf1b46, 3d7866ba).
- Resolução (`git show --remerge-diff 04e560fa`): lado da develop inteiro mais a linha `"test_forge_copia_nome": 4.0`. `git diff f17183d1 04e560fa -- tests/pesos-d4.json` dá só essa linha; o JSON carrega, 289 chaves, em ordem.
- Patch da branch inalterado: `git diff 900bfdfe 3d7866ba` e `git diff f17183d1 04e560fa` (sem as linhas `index`) diferem só no contexto do trecho de `tests/pesos-d4.json`; `bin/forge-copia`, testes e mutantes iguais.
- Suíte completa: CI do PR sobre a develop atual.

## Revalidação E111.6 (head 2f16f017)
Delta lido: `forge-check parecer delta` de 95011540..2f16f017 (desde 0def05cd só há pareceres); no domínio: `bin/forge-copia` (+2), changelog, mutantes e teste.
- A1 da segurança tratado: `ocupado` devolve verdadeiro para link simbólico (`bin/forge-copia:79`), e a sugestão pula para `-2`. No destino informado nada muda: `ocupado(real)` recebe o `realpath`, que nunca é link.
- `test_link_com_o_nome_sugerido_nao_e_oferecido` exercita o ramo de falha (link para pasta vazia fora da pasta de cópias: saída 2, sugere `b-qa-2`, nada criado no alvo).
- `bin/forge-mutante --processos 1 --ids M6 tests/mutantes/v0480-copia-nome-unico.json`: `M6 · morreu · bin/forge-copia:79`.
- `python3 -m unittest tests.test_forge_copia_nome`: 9 testes, OK. Suíte completa: CI do PR #806.

## Primeira rodada (head 95011540)

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
