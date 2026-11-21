---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-aviso-versao-parada
commit: 063a2d567e8500d6fcaa23d1ec4cae15adcb1c98
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-aviso-versao-parada

Revalidação (E69.9) do code review do AVISO-VERSAO-PARADA-NO-PROJETO no head 063a2d56. O parecer anterior (0b2b6398, head 1d47aa8e) reprovou só pelo A1 (`docs/hooks.md:16`).

## Sondas

## Parecer
Aprovado (`R-REVIEW`). O A1 está resolvido e o delta não traz defeito.

- Delta lido (`forge-check parecer delta docs/reviews/v0479-aviso-versao-parada.md`, intervalo 1d47aa8e..063a2d56): no domínio, `bin/forge_versoes.py`, `docs/hooks.md` e `tests/test_doutor.py`; `revalida: sim`.
- A1 (E69.7, 55280b3d): a linha do `doutor` em `docs/hooks.md:16` agora traz o aviso de versão parada. O texto bate com o código: 2 dias ou mais (`PARADO_AVISA_A_PARTIR_DE = 2`, `hooks/doutor.py:41`), um por dia e outro no mesmo dia só se a causa mudar (`hooks/doutor.py:260`), causa e comando, estado em `.forge/run/versao-parada` e medida em `.forge/run/versao-parada.log`.
- E69.8 (063a2d56, guarda C-2): os dois comentários que citavam o caminho do desenho em `docs/propostas/` passam a citar "o desenho aviso-versao-parada" (`bin/forge_versoes.py:168`, `tests/test_doutor.py:1167`). Só comentário e docstring, sem mudança de comportamento; `grep docs/propostas` nos dois arquivos não acha nada.
- Testes rodados aqui no head: `python3 -m unittest tests.test_reval_delta`: "Ran 10 tests / OK"; `python3 -m unittest tests.test_doutor.VersaoParada`: "Ran 23 tests / OK".
- Suíte inteira: não rerrodada (brief); a prova é o CI do PR, obrigatório para o merge.
- O resto (código, guardas, tamanho H1, segurança) segue como no parecer anterior: fora do delta, sem releitura.
