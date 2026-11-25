---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 841c14dcdc209c0cb1375caba6b11bcc0d4b155f
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-g2-1-publicar (E6.23, PR #878, G2.1: forge-check parecer publicar; classe C), volta por delta

Base 30dde218, head 841c14dc; delta lido: `git diff c78bfe22..841c14dc` (E6.21: `ultima_raiz` em `hooks/conformidade.py`, 3 fixtures `contrib-publicar-*`, mutantes M34 a M36, mínimo de 8 em `test_fixtures_do_publicar`). Parecer anterior (c78bfe22) aprovado; o review E6.18 reprovou por A1. Clone pelo `forge-copia`, no head do remoto (`HEAD` = `ls-remote` = 841c14dc). Sem CI neste head: `gh run list --commit 841c14dc` vazio e sem check-run; por isso sem a linha `ci:`. O CI do head anterior (3f42827f, só parecer) tinha `CI` e `Catraca` vermelhos, fora deste delta.

## Critério → teste → resultado (delta)
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 do review E6.18: duas `--raiz` antes do subcomando, a última no Forge, barram (S1) | fixture `contrib-publicar-duas-raiz-a-ultima-no-forge-bloqueia` em `test_fixtures_do_publicar` | primeira `--raiz` no projeto, última no Forge, formas `--raiz=` e separada | passou |
| A1: `--raiz` repetida depois do subcomando, a última no Forge, barra (S2) | fixture `contrib-publicar-raiz-depois-do-subcomando-no-forge-bloqueia` | `--raiz` antes e depois do subcomando | passou |
| Caso inverso: primeira no Forge, última no projeto libera (regra do argparse) | fixture `contrib-publicar-duas-raiz-a-ultima-no-projeto-libera` | a última vale, não a primeira | passou |
| Nada que barrava deixa de barrar | as 5 fixtures anteriores (`GH_REPO`, `--raiz` única no Forge, sessão do Forge, projeto, outro subcomando) no mesmo teste (8 fixtures, lados 0 e 2) | `--raiz` única: `ultima_raiz` igual a `parecer.opcao`; depois do `--`, não (S4) | passou nas 5 fixtures; falhou na sonda S4 |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_publicar`: 1 teste (8 fixtures), OK. `test_forge_pareceres.py`: 35 testes, OK.
- Vermelho: as 3 fixtures novas contra o `hooks/conformidade.py` de c78bfe22 (árvore do head com o hook da base, em `$TMPDIR`): `Ran 1 test, FAILED (failures=3)`, uma falha por fixture (as três acima). Com o hook do head, passam. O `forge-testes --vermelho` do módulo inteiro estourou o prazo da sessão e não deu veredito; vale o recorte acima.
- Mutantes (`bin/forge-mutante --processos 3 tests/mutantes/v0481-g2-1-publicar-6.json`, `rev=841c14dcdc20`): `M31 · morreu · conformidade.py:2575`, `M32`, `M33` (`:2578`), `M34 · morreu · :1387`, `M35 · morreu · :1389`, `M36 · morreu · :1388` (última em vez da primeira). M1 a M30 seguem como no parecer anterior.
- `--cobertura --base 30dde2189bb6`: as linhas novas 1387, 1388 e 1389 saem `coberta` (M34, M36, M35); 2575/2578 seguem cobertas; só `hooks/conformidade.json` e `tests/pesos-d4.json` saem "não coberto" (dados). Nenhuma linha de guarda mudada sem mutante.
- Nada que barra deixa de barrar (exceto depois do `--`, S4 abaixo): com uma só `--raiz`, `ultima_raiz` devolve o mesmo valor que `parecer.opcao` (`--raiz X` e `--raiz=X`); sem `--raiz`, `None` e o hook usa a pasta. Abreviação não abre contorno: o parser de topo tem `--raiz` e `--raiz-pedidos`, então prefixo menor é ambíguo e o argparse recusa. `--raiz` sem valor no fim é ignorada pelo hook e recusada pelo argparse.
- A1 do review E6.18: fechado, provado pelas fixtures de S1 e S2 (vermelho na base, verde no head).

## O corte deixa o publicar seguro para entrar agora?
Ainda não. A trava lê a última `--raiz`, mas também a que vem depois do `--` (sonda S4), onde o argparse a toma como o arquivo: regressão contra c78bfe22.

## Sonda S4 (o "nada que barra deixa de barrar" do brief, depois do `--`)
`ultima_raiz("--raiz /f parecer publicar -- --raiz=./x.md".split())` devolve `./x.md`; em c78bfe22 `parecer.opcao` devolvia `/f` (a primeira) e barrava. Com `--raiz <clone do Forge> parecer publicar -- --raiz=x/.forge/pareceres/v1/review.md` o hook libera em 841c14dc (código 0) e barrava antes (código 2); o forge-check usa a raiz do Forge. Confirma o A1 do review E6.22 e da segurança E6.24. A afirmação acima de que uma só `--raiz` não muda vale só sem o `--`.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1386 · `ultima_raiz` não para no `--`: `--raiz <forge> parecer publicar -- --raiz=x` passa (S4), barrava em c78bfe22. Pare o laço no `--`, com fixture (lado 2) e mutante.
- A2 (recomendado) bin/forge_pareceres.py:1 · Cartão: M1.4, M4.1, M4.2, M9.2, M9.3, M10.1, M10.2 e M18.1 cortadas do G2.1; sem elas o G2.2 (leitura) não pode entrar. Registrar como pré-requisito escrito do G2.2.
- A3 (recomendado) hooks/conformidade.py:3962 · M9.2 fica sem o hook `autoria` em `.forge/pareceres/`: o `publicar` recusa sempre. Abrir cartão com prioridade antes do G2.2.

## Parecer
Reprovado no head 841c14dc por A1 (bloqueante, regressão do `--`). O A1 do review E6.18 (S1, S2) está fechado: 3 fixtures vermelhas na base e verdes no head, M34 a M36 mortos. A cobertura de mutante não pegou o `--` porque nenhum mutante nem fixture o exercita (falha do plano de QA: a sonda de regressão cabia na primeira leitura). Sem CI do head para citar.
