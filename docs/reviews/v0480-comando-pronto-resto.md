---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-comando-pronto-resto
commit: dff23f769706eb32c04432a1a1c35fc3a9f2c5f1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E139.7, PR #826, resto do COMANDO-PRONTO-NO-TEXTO)

Diff `0e59c446..dff23f76`: 9 arquivos, um commit (`docs(skills): resto do comando pronto nas skills qa-testing e esperar-estado`).

## Diretriz 25 (texto tirado das skills)
Cada trecho removido de `SKILL.md` está num arquivo novo ou vizinho, com o mesmo sentido e ponteiro:
- `skills/qa-testing/SKILL.md`, "Simulação de merge": os três passos e o aviso das refs remotas saem palavra por palavra em `skills/qa-testing/comandos.md:38-44`; a seção da `SKILL.md` aponta para `comandos.md`.
- `skills/qa-testing/SKILL.md`, vermelho e mutantes: o texto ficou e só ganhou a forma completa (`--modulos`, caminho da spec, "depois do commit"); nada saiu.
- `skills/esperar-estado/SKILL.md`, laço sem teto da regra 6: está em `skills/esperar-estado/envio-longo.md:20-25`, com "a mesma saída do laço com teto, sem `fim=teto`" e a regra 6 apontando para lá.
- `skills/qa-testing/SKILL.md:51-52`: `forge-check` e `bin/forge-testes` perderam as crases, com o texto igual; o sentido fica, ver A1.

## Asserção trocada em tests/test_comando_pronto.py
Nenhuma asserção antiga mudou. A linha trocada é o `return` de `problemas_da_citacao` (`tests/test_comando_pronto.py:75-76`): antes devolvia `erros + faltas`, agora devolve `erros + faltas + formas_que_falham(...)`. A lista só cresce, e as 11 asserções antigas de `test_ramos_de_falha` seguem iguais e verdes (o ramo novo só dispara em `testes --vermelho` sem `--modulos` e em `mutante` com palavra solta fora de `tests/mutantes/`, que nenhum caso antigo usa). Não enfraquece. As 5 asserções novas cobrem os ramos de falha e de passagem das duas formas. Em `tests/test_esperar_estado.py`, a contagem de casos passa a somar os blocos de `envio-longo.md` (cresce) e `laco_longo` continua exigindo um bloco só nas duas fontes.

## Verificado
- `python3 -I -m unittest discover -s tests -p test_comando_pronto.py`: `Ran 3 tests`, `OK`; o teste lê 9 arquivos e 34 citações.
- `python3 -I -m unittest discover -s tests -p test_esperar_estado.py`: `Ran 16 tests`, `OK`.
- `bin/forge-mutante tests/mutantes/v0480-comando-pronto-resto.json`: `rev=dff23f769706`, os 8 mutantes `morreu`.
- `"rc=$?"` em `comandos.md:18` vai entre aspas duplas, a forma que `hooks/_comum.py:1709` aceita; não contradiz o "sem `$?`" do envio em `esperar-estado`.
- Mapa do `bin/forge-testes`: `skills/esperar-estado/.*` e `skills/qa-testing/.*` passam a chamar `test_comando_pronto`, que agora lê as duas pastas.
- Suíte completa: fica com o CI do PR #826 (V2); não foi rodada aqui.

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:51 · as crases de `forge-check` (l.51) e `bin/forge-testes` (l.52) saíram para o teste novo não cobrar subcomando; o sentido fica, mas some a marca de código. Melhor citar a forma real (`forge-check classe`) ou uma exceção com motivo em SEM_OBRIGATORIAS.
- A2 (recomendado) tests/test_comando_pronto.py:117 · o mínimo segue em 5 arquivos e 20 citações, com 9 e 34 lidos agora; tirar qa-testing ou esperar-estado de PASTAS passa verde. Suba os mínimos para o número atual (checklist 11).

## Sondas

## Parecer
Aprovado. A diretriz 25 foi cumprida: o texto que saiu das duas `SKILL.md` está em `comandos.md` e `envio-longo.md` com o mesmo sentido e com ponteiro. A troca em `test_comando_pronto.py` só acrescenta problemas à lista e não tira nenhuma asserção. Os 8 mutantes morrem e os dois módulos tocados passam. A1 e A2 são recomendados e viram cartão depois do merge.
