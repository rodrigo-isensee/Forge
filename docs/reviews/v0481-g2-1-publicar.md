---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 841c14dcdc209c0cb1375caba6b11bcc0d4b155f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E6.22, #878, G2.1: forge-check parecer publicar; classe C), 2ª volta por delta

Revalidação por delta da rodada que reprovou em c78bfe22 (E6.18; texto no git). Delta lido: `forge-check parecer delta` deste arquivo (7 arquivos no domínio: `hooks/conformidade.py`, 3 fixtures `contrib-publicar-*`, a spec `-6`, `tests/test_hooks.py` e o fragmento do changelog) e `git diff c78bfe22..841c14dc`.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1386 · `ultima_raiz` lê `--raiz=` também depois do `--`, onde o argparse já o toma como o arquivo: `--raiz <forge> parecer publicar -- --raiz=./.forge/pareceres/v1/review.md` passa no hook (S4), barrava no c78bfe22 e o forge-check usa a raiz do Forge (S5). Pare no `--`, com fixture e mutante.
- A2 (recomendado) hooks/conformidade.py:113 · Forma opaca (`python3 $(command -v forge-check)`) do A2 do E6.18, sem mudança neste delta: segue como cartão depois do merge.

## Sondas
- S4 · sessão de projeto, `forge-check --raiz ~/.forge-contrib/proj parecer publicar -- --raiz=./.forge/pareceres/v1/review.md` · espera: código 2, R-CONTRIB (como no c78bfe22, que barra) · obtido: código 0, sem saída
- S5 · o mesmo comando com `--raiz <tmp>/forge` e o arquivo em `<tmp>/forge/--raiz=./...` · espera: o arquivo lido sob a raiz do Forge · obtido: lido lá (passa caminho, `pedido:` e `tipo:`; recusa só no contrato, autoria e `commit:`), rc 1

## Achados anteriores
- A1 (bloqueante): corrigido para as formas S1 e S2. `ultima_raiz` dá a última `--raiz`, antes ou depois do subcomando, com e sem `=`; as fixtures `contrib-publicar-duas-raiz-a-ultima-no-forge-bloqueia` (S1) e `contrib-publicar-raiz-depois-do-subcomando-no-forge-bloqueia` (S2) barram, e o inverso (`-a-ultima-no-projeto-libera`) libera, como o argparse. Abreviação de `--raiz` não abre contorno: todo prefixo de `--raiz` também é prefixo de `--raiz-pedidos`, e o argparse recusa por ambiguidade. A forma com `--` (A1 acima) é a lacuna nova.
- A2 (recomendado): segue como cartão (A2 acima).

## Leitura do delta
- **O que deixou de barrar:** com uma `--raiz` só, a leitura é a mesma do `parecer.opcao`. Com duas, a primeira no Forge e a última no projeto, o c78bfe22 barrava e o 841c14dc libera: é o certo, porque o forge-check usa a do projeto (fixture do inverso). Fora disso, só a forma com `--` (A1), sonda rodada nos dois SHAs pela máquina de fixtures (`Fixture`, `executar_fixture`) sobre o `git archive` de cada um.
- **Testes:** `test_fixtures_do_publicar` sobe o mínimo para 8 e mantém os dois lados (item 11 do checklist).
- **Mutantes:** M34 a M36, um por linha de guarda de `ultima_raiz`; a troca do M36 (`raiz or`) é a que reproduz a leitura antiga da primeira.
- **Tamanho (H1):** 11 linhas de código no delta.
- **Commit:** Conventional Commits em português, com o pedido e a etapa.

## Verificações
- Rodados aqui no 841c14dc: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_publicar` (OK); `bin/forge-mutante --processos 1 --ids M34,M35,M36` na spec `-6` (os 3 morreram); `bin/forge-mutante --cobertura --base c78bfe22` (linhas 1387 e 1389 cobertas por M34 e M35; nenhuma sem mutante).
- CI: nenhum check registrado no 841c14dc (`gh pr checks 878` e `check-runs` do commit vazios; o PR está em rascunho). Sem linha `ci:`. A suíte inteira não foi rerrodada aqui.

## Parecer
Reprovado por A1: o critério desta volta é que nada que barra hoje deixe de barrar, e a forma com `--` barrava no c78bfe22 e passa no 841c14dc. A correção cabe em uma linha (`ultima_raiz` para no `--`), com uma fixture da S4 e um mutante dessa guarda. O resto do delta fecha o A1 do E6.18.
