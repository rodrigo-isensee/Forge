---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pesado-versoes
commit: 4d3f76d441f1c276b554497e69c4330556dc3433
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E64.3, PESADO-VERSOES-FORA-DA-FILA)

Diff `8ee73d15..f8210fe5` (um commit): `hooks/pesado.py` (+18/-6), `tests/test_forge_pesado.py`, `tests/test_hooks.py` (escopo do E64.2), 3 fixtures em `tests/hooks/pesado/forgetestes-*.json`, `tests/mutantes/v0478-pesado-versoes.json`, `docs/hooks.md`, `docs/hooks-fixtures.md` e o fragmento `changelog.d/v0479-pesado-versoes.md`.

## Sondas

## Parecer
Aprovado.

- Requisito: o teste dirigido do `bin/forge-testes` passa de lista de exclusão (`--completa`, `--vermelho`) a lista fechada `LEVES_DO_FORGE_TESTES` (`hooks/pesado.py:294`), com `-k` e `--` à parte. Conferi contra o `argparse` de `bin/forge-testes:1143-1159`: as seis leves são exatamente as opções que não rodam a suíte larga; `--versoes`, `--modulos`, `--prazo`, `--executar` (o `--registro` interno só age com ele), `-h` e a desconhecida pesam. Nenhuma leve começa por `--c` nem `--v`, então abreviação ambígua (`--ve`) cai em pesado, e o teste `test_nenhuma_opcao_leve_abrevia_completa_vermelho_nem_versoes` trava isso com mínimo de 6 itens (checklist 11).
- A mudança só aperta: `--modulos` e `--prazo` sozinhos passam a pesar; nas skills, agentes e regras eles só aparecem com `--vermelho`, já pesado. `-kx` colado e o que vem depois de `--` pesam por conservadorismo, como a docstring diz.
- `tests/test_hooks.py:3212`: troca de `--dirigida` (opção inexistente, agora pesada) por `--afetados`; o teste de ausência segue lendo uma forma leve real.
- Guardas do diff (classe C): três linhas de guarda (`pesado.py:299`, `:301`, `:309`), um mutante cada (M1 a M3), cada um com teste do ramo de falha por comportamento (chama `pesado.pesado`), não por leitura da fonte. Rodei `bin/forge-mutante tests/mutantes/v0478-pesado-versoes.json --processos 1`: M1, M2 e M3 morreram, rc=0.
- Teste novo: `python3 -m unittest tests.test_forge_pesado.FormasLevesDoForgeTestes tests.test_hooks.PesadoClassePelosArgumentos`: 8 testes, OK. Suíte inteira: só no CI do PR (R-REVIEW); a branch não tem PR nem run, então o verde do CI fica para o merge.
- Tamanho (H1): 18 linhas de código, um comportamento. Docs (`docs/hooks.md`) e índice de fixtures atualizados na mesma entrega; fragmento do changelog presente. Commit único em Conventional Commits.

## Revalidação no head 4d3f76d4 (E64.8)
Delta lido: `forge-check parecer delta docs/reviews/v0479-pesado-versoes.md`, intervalo `f8210fe5..4d3f76d4`; no domínio só `tests/mutantes/v0451-a1b.json` (os outros três arquivos do intervalo são pareceres). Aprovado.

- M5 passa a mirar `all(opcao_leve(a) for a in argumentos if` (`hooks/pesado.py:309`), a linha que lê os argumentos em qualquer posição; A1-separador passa à tupla `("--", "-k")` de `opcao_leve` (`pesado.py:299`), quem segura o `--` desde a E64.1. A1-prefixo, A1-igual e A1-separador ganham `test_formas_da_lista_seguem_leves` (`--list`, `--base=...`, `-- tests/a.py`), teste que já existia em f8210fe5: o delta não toca teste.
- `bin/forge-mutante tests/mutantes/v0451-a1b.json --processos 1`: M1 a M7 e os três A1 morreram, rc=0. `bin/forge-mutante tests/mutantes/v0478-pesado-versoes.json --processos 1`: M1 a M3 morreram, rc=0.
- Nota do revisor: em f8210fe5 rodei só a spec do pedido; a `v0451-a1b`, que mira o mesmo `hooks/pesado.py`, tinha três mutantes sobreviventes e passou sem ser rodada. Suíte inteira: só no CI do PR (R-REVIEW).
