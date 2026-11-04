---
tipo: revisao-devops
contrato: 1
pedido: versao-033
branch: melhoria/prepush-so-docs
commit: bce7ad1dc874ff83d553e9c8b01592851273e583
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: prepush-so-docs (E18, pedido versao-033)

## Parecer
Aprovado. Diff 928e61b...0ba1a87: `templates/projeto/.githooks/pre-push` (a função `so_docs`, linhas 36-58, e o desvio nas linhas 62-67), `bin/forge-testes` (mapa), o teste `tests/test_prepush_so_docs.py` e o fragmento de changelog. Limite do modelo de ameaças conferido: o `pre-push.local` só é pulado quando todas as refs enviadas passam, por `git diff --name-only -z --no-renames <remoto> <local>` (C-1). Roda tudo em: branch nova, apagar ref, tag, falha do git, `mktemp` falho, diff vazio, `.github/*`, qualquer nome fora de `docs/*` ou `*.md` minúsculo (C-2, C-3, C-4). Fecha em falha: todo caminho de dúvida retorna 1. Sem variável, opção ou arquivo que pule (T-1), critério não alargado (T-2).

Efeito no fluxo dos projetos: o CI do modelo não muda (T-4); o pulo vale só no pre-push local e imprime uma linha. As checagens `R-VERIFY` e da `main` (linhas 5-30) rodam antes e sempre, e o laço só acrescenta a coleta das refs (T-3). O stdin do `pre-push.local` é o mesmo de antes (já consumido pelo laço). Compatibilidade: projetos existentes recebem a mudança pelo `forge atualizar` sem migração; sem `pre-push.local` nada muda. Bash 3.2 em diante cobre o que o hook usa (arrays, `read -d ''`, `local`; o array vazio é protegido pela guarda da linha 41), e o git usado é o padrão (`diff --name-only -z --no-renames`). A `.githooks/pre-push` do Forge não está no diff. Risco aceito pela decisão: código em `docs/**` pula o lint local, o CI pega.

Provas: `python3 -m unittest tests.test_prepush_so_docs tests.test_ambiente_git tests.test_testes_tocados` · 130 testes, OK. Ferramentas: `shellcheck` ausente do PATH (lacuna registrada; o teste do item o roda quando existe e o CI o roda); `actionlint` não se aplica (sem workflow). PA-7: sem ocorrência (sem `.github/`, permissão, SHA de ação, cache nem entrada não confiável em `run:`).

## Achados

## Rodada 2
Delta 3dd4483..bce7ad1, só `templates/projeto/.githooks/pre-push` (+4 -3), a correção do SC2094 do shellcheck do CI. A recusa dentro do laço vira a variável `recusa` com `break`; o `rm -f "$lista"` e o `return 1` ficam depois do `done`, então o arquivo da lista não é mais apagado enquanto o laço o lê, e não há diretiva `disable`. `recusa` entra no `local` e é zerada a cada ref.

Comportamento igual ao da rodada 1: `.github/*` e nome fora de `docs/*` ou `*.md` recusam (`recusa=1`); diff vazio recusa (`achou=0`); os demais retornos 1 (sem refs, `mktemp`, hash zerado, tag, falha do git) não mudaram; só libera quando toda ref passa. Sintaxe `bash -n` ok. O `break` e o `[ ] || [ ]` são POSIX e valem no Bash 3.2 em diante; nenhum git novo. Efeito no fluxo dos projetos igual ao da rodada 1: CI do projeto com a bateria completa, pulo só no pre-push local, `forge atualizar` sem migração, `.githooks/pre-push` do Forge fora do diff. Passo shellcheck do CI do PR #436 em success em bce7ad1 (run 41780938757), o que resolve a lacuna de ferramenta local; `shellcheck` segue ausente do PATH aqui. Sem regressão nova.

Provas: `python3 -m unittest tests.test_prepush_so_docs tests.test_ambiente_git tests.test_testes_tocados` · 130 testes, OK. PA-7 conferido: sem ocorrência.

## Custo e rollback
Custo zero (`R-CUSTO`): só script local, sem minutos de CI. Rollback: reverter o commit do hook; os projetos voltam a rodar o `pre-push.local` sempre.
