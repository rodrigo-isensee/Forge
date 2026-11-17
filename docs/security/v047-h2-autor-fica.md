---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 6d73898a54d405cae438ed76d745fd32bc2436f4
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474, H2-AUTOR-FICA-ATE-O-MERGE (E2.29)

Primeira rodada sobre `e2880b42..6d73898a` (3 commits): `hooks/agentes.py` (registro `autores` no `SubagentStop` e aviso R-TETO no disparo), a chave `aviso` do executor de fixtures em `tests/test_hooks.py`, os 12 fixtures `autor-*`, `tests/test_hooks_agentes_autor.py` e as specs de mutante. Lidos por inteiro no delta.

## Gatilhos
Gatilhos: guarda em hook de controle (`R-TETO`, uma delegação de escrita por branch), leitura de estado que um agente pode corromper (`.forge/run/agentes.json`).

## Achados
- A1 (bloqueante) hooks/agentes.py:467 · autores_retomaveis faz set de l.get("id") e a.get("id") sem checar tipo; id não texto (lista, objeto) no estado legível lança TypeError depois do append (956) e antes do gravar_json (1050): o disparo sai 0 sem reserva e o 2º escritor da branch passa (S1, S2)
- A2 (recomendado) tests/test_hooks.py:820 · o ramo `aviso` só confere o trecho com assertIn: stderr extra (um traceback) ou outra chave no JSON do stdout passariam; conferir cada linha do stderr com prefixo `R-` e as chaves do stdout iguais a ["systemMessage"]

## Sondas
- S1 · fixture agentes: estado {"agentes":[],"lapides":[{"id":["x"],"desde":"{agora-60}"}]}, disparo de escrita em melhoria/a · espera: código 0 e o disparo gravado em agentes.json (como na base e2880b42) · obtido: código 0, agentes.json sem o disparo; TypeError unhashable type: 'list'
- S2 · mesmo estado de S1, passo 1 disparo "P1" e entrada disparo "P2", os dois em melhoria/a · espera: código 2 R-TETO (branch ocupada, como na base) · obtido: código 0, o segundo escritor passa

## Detalhe dos achados
**A1.** Evidência: `hooks/agentes.py:467` (`fora = {l.get("id") for l in lapides} | {a.get("id") for a in agentes}`), chamado em `hooks/agentes.py:958`, depois de `agentes.append` (956) e antes do `gravar_json` de `hooks/agentes.py:1050`. `lapides_vigentes` e `vigentes` não validam o tipo do `id` (só `desde`), e `ler_estado` aceita o arquivo (é JSON, raiz objeto, listas). A exceção sobe a `executar` (`hooks/_comum.py:2840`), que no `agentes` (sem `critico`) libera com 0. Caminho de ataque: um agente (ou a sessão) que grava `.forge/run/agentes.json` com uma lápide ou registro de `id` não texto faz todo disparo seguinte passar sem reserva: o teto e a regra de uma delegação de escrita por branch deixam de contar (S2). É o mesmo modelo de ameaça que o HOOK-ESTADO-ILEGIVEL-LIBERA fechou: estado corrompido nunca libera. Na base `e2880b42` as sondas S1 e S2 dão o esperado (gravado; código 2); no head, não. O aviso, que só informa, passa a poder liberar o que antes recusava. Severidade: média (exige escrita no estado, mas anula o controle por inteiro e sem rastro além do erros.log). Correção mínima: o aviso nunca impede o registro; uma das duas, de preferência as duas: (a) em `autores_retomaveis`, só ids texto no conjunto (`isinstance(x, str)` nos dois lados); (b) calcular o aviso dentro de `try/except Exception` que registra no erros.log e devolve `None`, ou emiti-lo depois do `gravar_json`. Teste: fixtures `autor-*` com lápide de `id` lista e registro de `id` objeto, esperando o disparo gravado e o segundo escritor recusado. Esforço: P. Dono: o autor da branch (developer do H2).

Conferido sem achado: (1) `autores` não entra em decisão nenhuma: só `autores_retomaveis` → `aviso_de_autor` → `avisar` (linhas 1033, 1043, 1048, 1050); nenhum ramo de recusa ou liberação o lê, então forjar `autores` não burla o R-TETO (no máximo produz ou cala o aviso); `autores` lixo (não lista, item não objeto, id fora da forma, `desde` não número, `escrita` não lista) vale vazio ou é filtrado (`autores_vigentes`, `textos`), sonda local com cinco formas de lixo deu o disparo gravado. (2) As recusas de `lancar` (teto, branch ocupada, R-BRIEF) seguem antes do `append`; o estado ilegível segue recusando (`ler_estado` intacto, `autores` fora da validação de propósito). (3) O texto do aviso usa a branch da própria `escrita` do disparo, passada por `sem_controle` e cortada em `CORTE_DO_NOME`, e o id casa `ID_DE_AGENTE`: sem quebra de linha forjada no `systemMessage`. (4) `guardar_autores` corta em `LAPIDES_MAX` e só roda no `SubagentStop`, onde a exceção deixaria o registro ativo (lado seguro). (5) O executor: a chave `aviso` exige `hook == agentes` e código 0; os demais hooks e os fixtures do `agentes` sem a chave seguem com stdout e stderr vazios (`tests/test_hooks.py:824-829`).

**A2.** Endurecimento do teste, sem caminho de ataque: hoje um fixture de aviso que também despejasse traceback no stderr passaria. Severidade: baixa. Esforço: P. Dono: `qa-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; não há execução de CI para a branch (`gh run list` vazio, sem PR), então o portão do PR segue exigindo o CI verde. Rodei `tests/test_hooks_agentes_autor.py` no head (6 testes, OK) e as sondas S1 e S2 pelo executor de fixtures do próprio `tests/test_hooks.py`, no head e numa cópia local na base `e2880b42`. `gitleaks` ausente do PATH (lacuna; o delta não traz credencial nem configuração). Workflows fora do delta.
