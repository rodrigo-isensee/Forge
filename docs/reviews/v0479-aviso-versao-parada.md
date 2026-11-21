---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-aviso-versao-parada
commit: 1d47aa8ec5d32e91308dd65d5793279634024106
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-aviso-versao-parada

Code review do AVISO-VERSAO-PARADA-NO-PROJETO (v0478 E69.5) no head 1d47aa8e, base develop bead3e53. Diff: `hooks/doutor.py`, `bin/forge_versoes.py`, `README.md`, fragmento `changelog.d/`, 4 specs de mutante novas e a `v047-sempre-atual-4.json` alinhada, `tests/test_doutor.py` (classe `VersaoParada`).

## Achados
- A1 (bloqueante) docs/hooks.md:16 · a linha do `doutor` não cita o aviso de versão parada (2 dias, um por dia, causa e comando, `versao-parada` e `versao-parada.log` em `.forge/run/`); o T3 do desenho (docs/propostas/aviso-versao-parada.md:141) põe `docs/hooks.md` na entrega. Pendente: o item do T3 sem commit.

## Sondas

## Parecer
Reprovado, só pelo A1 (requisito do desenho e definição de pronto: documentação afetada na mesma entrega; `R-REVIEW`). O código está correto; a volta é só documentação, sem nova rodada de código.

- Escopo: faz a opção A do desenho (seções 4 a 7): texto por causa (`sessao-antiga`, `adiada`, `falhou`, `sem-atalho`) com o comando que a pessoa roda, sem "Nada a fazer"; `PARADO_AVISA_A_PARTIR_DE = 2`; um aviso por dia e outro no mesmo dia só se a causa mudar (`hooks/doutor.py`, comparação de `avisada_em` e `causa`); sem rede vale o `ultima` do cache com a data; medida em `.forge/run/versao-parada.log`, fechada quando a carregada alcança a vista. Sem rede nova nem token (`R-CUSTO`).
- Leitura defensiva: `versao_instalada` cobre JSON fora da forma (TypeError, KeyError, ValueError) e filtra escopo `user` ou o `projectPath` do projeto; `causa_da_parada` lê `registro.log` e `estado.json` com `_ler_limitado`, aceita etapa só `[a-z0-9-]{1,32}` (o que vem do registro não vai cru ao texto) e cai em `sem-atalho` com pasta ausente, link ou de outro dono, reaproveitando `pasta_do_sempre_atual` (extraída de `avisos_do_sempre_atual`, sem mudar comportamento; a spec `v047-sempre-atual-4.json` A4 e A5 acompanha o `return None`). O formato do registro bate com o gravador (`bin/forge_sempre_atual.py:281`, último campo `falhou:<etapa>:<resumo>`).
- Isolamento da falha: `principal` envolve o aviso novo em `except OSError` com `registrar_erro`, e a falha não come o aviso de versão nova nem o do relógio.
- Tamanho (H1): 135 linhas de código, abaixo de 150 (histórico do pedido, E69.3); um comportamento.
- Guardas: 31 mutantes em 4 specs de até 8 (`v0478-aviso-versao-parada*.json`), um por linha de guarda, cada um com teste do ramo de falha por subprocesso do hook (`VersaoParada.stop`), não por leitura da fonte; o autor relata 31 mortos (E69.3).
- Teste novo rodado aqui no head: `python3 -m unittest tests.test_doutor.VersaoParada`: "Ran 23 tests in 10.773s / OK".
- Suíte: não rerrodada (brief: sem suíte local); a prova é o CI do PR, obrigatório para integrar.
- Segurança: parecer aprovado em aaf8d31b (E69.4), citado sem refazer.
