---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/flaky-prepush-grupo
commit: 905edbbb3bb529646fcfa4dbdac0f724ec0f23f5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: flaky-prepush-grupo

## Gatilhos
Teste de controle do pre-push do modelo de projeto (R-SEGURANCA, guarda que barra o envio e encerra o grupo da etapa). Muda só `tests/test_prepush_so_docs.py` e o fragmento de changelog; o hook do modelo não muda.

## Achados
- A1 (bloqueante) tests/test_prepush_so_docs.py:315 · a espera do vigia é vazia: o `sleep` irmão do wrapper (`lanca`) é filho do PID do hook e passa no filtro; o SIGTERM sai logo após o arquivo `etapa`, sem cobrir a janela do `alvo`

## Sondas

## Detalhe dos achados
A1. Evidência: `tests/test_prepush_so_docs.py:315` (filtro de `vigia`) e `:323` (uso); `lanca` roda `sleep 60 & echo $! > irmao; exec .githooks/pre-push`. O `exec` mantém o PID, então o `sleep 60` irmão tem ppid igual a `p.pid`, nome `sleep` e PID diferente da etapa: `vigia` devolve verdadeiro assim que o irmão existe, antes mesmo de o hook chegar ao laço. Como `le("etapa")` só volta depois de o hook já ter lançado a etapa, a nova espera não acrescenta nada e o sleep de 1 s foi removido sem substituto. O SIGTERM passa a chegar na janela entre o lançamento da etapa e a atribuição de `alvo="-$etapa"` (`templates/projeto/.githooks/pre-push:147-150`), onde `encerrar_etapa` sinaliza só o líder e deixa o filho da etapa no grupo: `test_term_no_hook_encerra_o_grupo_e_poupa_o_irmao` pode falhar com mais frequência, não menos. Leitura estática: neste sandbox o `/proc` é de outro namespace de PID, então não pude executar os 4 testes de `GrupoDaEtapa` nem provar com sonda; o raciocínio vem da semântica de `fork`/`exec` e de `lanca`. O CI, que roda os testes, decide.
Caminho de ataque: não há (teste, não produção); o risco é a prova do controle ficar frágil ou vazia, e o CI do PR voltar a oscilar.
Severidade: média (controle de segurança com prova não confiável). Correção mínima: ler o PID do irmão (`self.le("irmao")[0]`) e excluí-lo no filtro (`pid not in (etapa, irmao)`), ou exigir como filho do hook um `sleep` posterior à atribuição de `alvo`; manter o prazo de 30 s e as asserções. Esforço: P. Dono: tech-lead (autor da E26.4).

Não afrouxa as asserções: `assertEqual(rc, 1)`, a mensagem de interrupção, o irmão vivo e o grupo encerrado seguem iguais; o hook do modelo não foi tocado. O problema é só o portão novo não segurar o que promete. Conferido contra `docs/engineering/achados-recorrentes.md`: nenhum item se aplica (sem ambiente herdado, sem `-I` em caminho de decisão, sem lista negativa).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só leitura do diff e a sonda do `/proc`, que não pôde rodar neste sandbox; os testes não foram executados (pulados aqui, só o CI os roda).
