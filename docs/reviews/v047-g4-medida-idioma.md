---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-g4-medida-idioma
commit: bdbb45cd5235d601649e3bbdd889bb8b4aaae4cb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047 · SIEG-G4, medida do idioma da mensagem ao dono (E2.698)

Escopo (E2.683): `hooks/meta.py` grava `idioma`, `idioma_do_dono` e `outro_idioma` na linha de `.forge/run/mensagens.jsonl`; só mede, nunca bloqueia. Base 5b1aacd5, head 675cf7a1, três commits (feat e dois test), mais o fragmento `changelog.d/v047-g4-medida-idioma.md`.

## Leitura
- Faz o pedido e só ele: a medida roda no `finally` de `principal`, sob o `except` que leva a falha ao `erros.log`; a decisão do Stop não muda (S6). O texto ao dono fica fora, como a E2.683 diz.
- Neutralidade (`R-NEUTRO`): o idioma do dono vem do `.forge/config.json` do projeto; ausente, português (decisão do pedido); código sem lista vira `None` e não acusa.
- `outro_idioma` só com idioma e dono conhecidos; mensagem curta, mista (empate) ou só em código e citação fica sem idioma.
- Tamanho (M14): 107 linhas de código e teste (`hooks/meta.py` 39+4, `tests/test_meta.py` 61+3), um comportamento; dentro da orientação.
- Testes de comportamento pela linha gravada, sem ler a fonte; o falso do hook é mínimo e não afrouxa regra de `git`/`gh` (item 12 n/a).

## Ferramentas
- `python3 -m unittest tests.test_meta` (ambiente limpo, `env -i`): `Ran 20 tests ... OK`.
- `bin/forge-mutante --base 5b1aacd5 tests/mutantes/v047-g4-medida-idioma.json`: M1 a M8 `morreu` (meta.py:198, 200, 208, 209, 210, 212, 231).
- `bin/forge-mutante --cobertura --base 5b1aacd5`: as 6 linhas de guarda do diff `coberta`.
- Suíte inteira: fica no CI do PR (`R-REVIEW`); não rerrodada aqui.

## Revalidação
Delta lido (`forge-check parecer delta`, 675cf7a1..bdbb45cd): só `tests/mutantes/v047-jargao-medida-4.json`, o `de` do M27 passou a `medir_mensagem(hook, raiz)` (hooks/meta.py:246, existe no código). `bin/forge-mutante --base 5b1aacd5 tests/mutantes/v047-jargao-medida-4.json`: M25, M26, M27, M28 `morreu`. Sem código nem teste mudados; A1 segue recomendado.

## Achados
- A1 (recomendado) hooks/meta.py:189 · "que" e "no" estão só na lista pt e são frequentes em espanhol: "Pienso que no es lo que querías, pero no hay prisa." mede `pt` (sondado). Falso negativo para dono pt; só medida. Tirar "que"/"no" do pt ou pesar por lista, se a medida mostrar ruído.

## Sondas
