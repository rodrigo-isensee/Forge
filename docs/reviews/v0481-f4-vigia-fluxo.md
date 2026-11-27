---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: dd25e4a821e0e284215c2916f78147edbd285e7e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E34.11, F4 do estudo de atrito, PR #931), volta 2

Revalidação por delta (H3) no `dd25e4a8`. Delta lido: `forge-check parecer delta docs/reviews/v0481-f4-vigia-fluxo.md`, intervalo `04b508f6..dd25e4a8`, 4 arquivos no domínio (`bin/forge_estado.py`, `tests/mutantes/v0481-f4-vigia-fluxo-7.json`, `tests/mutantes/v0481-s1-status.json`, `tests/test_hook_vigia_f4.py`).

Achados da volta 1 (`04b508f6`):
- A7 resolvido: o `de` de M7 e M8 de `tests/mutantes/v0481-s1-status.json` leva a linha do `return` seguinte e casa uma vez só em `bin/forge_estado.py` (63 e 66); a suíte 4/5 do head está verde.
- A8 resolvido: `gravar_prs_abertos` (`bin/forge_estado.py:120`) apanha o `OSError` da gravação e do `chmod` e tira o temporário pelo mesmo nome do `gravar_json` (`hooks/_comum.py:2574`, `<nome>.<pid>.tmp`); o `unlink` que falha também não sobe. O `status` segue com rc 0 e o `proximo` não muda nada.
- A5 segue como cartão depois do merge.

## Verificações
- ci: dd25e4a821e0e284215c2916f78147edbd285e7e verde
- CI lido em `gh pr checks 931`: suíte 1/5 a 5/5, passos, python 3.14, verificações longas, instalação, árvore já provada, teto de pulados e `catraca` verdes; `bateria` e `bateria (pareceres)` esperam os pareceres.
- Testes afetados, à mão: `python3 -m unittest tests.test_hook_vigia_f4 tests.test_forge_status_estado`, 70 testes OK.
- Mutantes: `bin/forge-mutante` em `v0481-f4-vigia-fluxo-7.json` (M49 a M52) e `v0481-s1-status.json` (M5 a M8), todos mortos; `--cobertura --base 04b508f6`, rc 0.
- Leitura dos testes novos de `GravacaoDaLista`: o caminho da lista vem do `lista_de_prs` remendado no `setUp`, então o `renovar_prs_abertos` do teste do `proximo` chega de fato à gravação; o teste do disco cheio confere a lista anterior intacta e a pasta só com ela.

## Parecer
Aprovado. Os dois bloqueantes da volta 1 estão resolvidos com teste do ramo de falha e mutante morto por guarda nova, e o CI do head está verde fora os portões que esperam os pareceres.
