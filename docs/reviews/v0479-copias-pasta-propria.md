---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-copias-pasta-propria
commit: 38182111f20ad008e7db51910ef24e80f4d988c3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E78.2, forge-copia com as cópias do projeto em pasta própria)

Diff revisado: `5e3ca873..48a6e19b` (bin/forge-copia, teste, spec de mutantes, changelog, índice e ritmo-e-corte). Código em `bin/`: cerca de 35 linhas, dentro do teto H1, um comportamento só.

## Achados
- A1 (recomendado) bin/forge-copia:241 · no projeto o modo `worktree` não é recusado: só a docstring (linha 4) diz "use clone"; o sandbox barra `.git/worktrees` e o git falharia no meio. Recusar `worktree` quando `raiz_do_projeto()` existe, com motivo claro e teste do ramo.

## Parecer
Aprovado. Detecção projeto × Forge: `raiz_do_projeto()` sobe o `--show-toplevel` real até antes de `/.forge/wt/` (vale de dentro de uma cópia) e exige `.forge/config.json` sem `.claude-plugin/`; fora de git ou no Forge, segue `~/.forge-contrib`. Os testes de `Projeto` cobrem os quatro ramos (projeto, de dentro da cópia, Forge com as duas marcas, fora de git) e a recusa da pasta do Forge a partir do projeto.

Limpeza: `limpar()` usa a mesma `raiz()` e o mesmo critério (`sujeira` antes e depois, `fim_do_item`) nas duas pastas; `test_limpar_apaga_a_copia_do_projeto` prova o apagamento em `<projeto>/.forge/wt`. O `forge-fechar --limpar` continua varrendo só `~/.forge-contrib/wt`, o que é coerente: ele é do Forge, e no projeto a limpeza é `forge-copia limpar` (texto de ritmo-e-corte.md:44).

`.gitignore` `*` criado uma vez, depois da validação do destino, e não tocado se existe; o `git status` do projeto fica limpo (teste).

Verificadores: `test_forge_copia` (64), `test_forge_fechar` (34) e `test_modelos_projeto` (20) verdes no 48a6e19b; `forge-mutante` na spec: M1 a M7 mortos; `--cobertura --base 5e3ca873`: toda guarda do diff coberta. Suíte inteira: fica no CI do PR.

## Revalidação no 38182111 (E78.7)
Delta lido com `forge-check parecer delta` (`48a6e19b..38182111`): `bin/forge-copia`, teste, as duas specs de mutantes e o changelog. O `.gitignore` é aberto com `O_CREAT|O_EXCL|O_NOFOLLOW` (link criado depois também falha) e o link versionado é recusado antes, com rc 2 pela `recusa()` em `main()`; a `raiz()` do projeto não é resolvida, e `.forge/wt` como link para `~/.forge-contrib/wt` cai na recusa "fica fora de" (S1). Os testes S1 e S2 provam o ramo de falha pelo comportamento (rc 2, nada gravado no alvo nem na cópia). A1 segue recomendado, fora deste delta.

Verificadores: `test_forge_copia` 66 OK no 38182111; `forge-testes --registros --base origin/develop` rc=0; `forge-mutante` nas duas specs: M1 a M10 mortos; `--cobertura --base 48a6e19b`: linhas 59 e 248 cobertas por M8 e M9. Suíte inteira: fica no CI do PR.
