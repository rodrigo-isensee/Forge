---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/invariante-gatilho
commit: 5fffee68faa49810653da9dceb8c5c8dd69aaf44
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: invariante-gatilho (pedido versao-033, frente 0.34)

Revalidação por delta da leitura do lote textos-034 (parecer 77a422eebe94e998f2d8881b215d46bf8d8a3f21, branch rev-textos-034), que dividiu o lote em um PR por cartão (A1 de lá). Delta lido: `git diff` dos arquivos de texto entre o commit do cartão no lote e o head desta branch, o teste novo e o fragmento do changelog. Já lido no 77a422e: o restante do texto, que é igual.

## Delta
- `templates/projeto/docs/pedidos/_modelo.md:37`: atende o A4 do 77a422e, porque a referência a `tests/config.json` agora vem marcada como do Forge. A frase em `agents/jarvis.md` ficou como resto do cartão; o cartão fecha em parte e o resto vai ao quadro.
- `tests/test_invariante_gatilho.py` confere a nova redação; `changelog.d/invariante-gatilho.md` traz só a linha deste cartão.

## Comandos (head 5fffee6)
- `python3 -I -m unittest discover -s tests -p test_invariante_gatilho.py`: OK.
- `python3 -I tests/neutralidade.py`: rc=0.
- M14: 21 linhas de teste, um cartão; abaixo de 150.

Gatilho: nenhum.

## Achados
- A1 (recomendado) templates/projeto/docs/pedidos/_modelo.md:37 · "já nasce com esta etapa, no Forge, inclusive quando..." pode ser lido como se a etapa inteira valesse só no Forge; escrever "inclusive, no Forge, quando prevê invariante novo..." deixa o alcance claro.

## Parecer
Aprovado. O A4 do lote foi atendido; o A1 é só redação e não devolve.
