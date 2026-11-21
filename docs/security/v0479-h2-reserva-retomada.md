---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-reserva-retomada
commit: 610ba4ce1568a305a58e9cebf7e4bb289695dd8a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478, H2-RESERVA-DA-RETOMADA-PRAZO (E87.3)

Cobre os recomendados A4 e A5 de `docs/security/v047-h2-autor-fica.md` (E2.65 do v0474) e o A6 da E2.64. Diff lido inteiro: `ad3b3b6f..610ba4ce` (10 arquivos; o código é `hooks/agentes.py`, o resto é teste, fixture, mutante e doc).

## Gatilhos
Gatilhos: hook de controle do Forge (`hooks/agentes.py`, trava de escrita por branch do R-TETO)

## Achados

## Sondas

## Detalhe dos achados
Nenhum bloqueante e nenhum recomendado. A mudança só aperta. Conferi os quatro pontos do pedido com sondas pelo hook real (o runner de fixtures `tests/test_hooks.py`, num projeto temporário), no head e na base `ad3b3b6f` (cópia por `git archive`).

1. **O Start tardio fecha o buraco depois do início** (`hooks/agentes.py:1301`). Sonda: `autores` com A na `melhoria/a`, sem reserva, `SubagentStart` de A, depois o disparo de um 2º escritor na `melhoria/a`. Na base o disparo sai com 0 e sem aviso (é o buraco do A4: valia por toda a sessão de A). No head ele é recusado (2, `R-TETO: melhoria/a ocupada por forge:software-engineer`). Depois do `SubagentStop` de A, a reserva cai e o disparo seguinte volta ao aviso H2, com 0. A fixture `autor-retomado-inicio-tardio-reserva-de-novo` cobre isso, e o mutante M1 de `tests/mutantes/v0479-h2-reserva-retomada.json` guarda o ramo.
2. **Na janela, entre RESERVA_S e o Start, o 2º escritor ainda passa.** Isso é residual e não regride (a base faz o mesmo). Sonda S1: a reserva da retomada com `desde` de 400 s atrás e um disparo de escrita na `melhoria/a` dão 0, mas com o aviso H2 `autor retomável (melhoria/a: <id de A>)`. Sonda S2: o 2º escritor da janela inicia, depois vem o Start tardio de A. Os dois ficam com registro na `melhoria/a` (o `SubagentStart` não recusa), e o 3º escritor é recusado. Sonda S6: o 2º escritor da janela termina antes do Start de A. O `guardar_autores` o põe no lugar de A como autor da branch, então A inicia sem reserva. Fechar a janela pediria uma reserva da retomada mais longa, o que reabre a decisão do A5 (reserva curta). O aviso H2 no disparo da janela já informa o Jarvis. Proporcionalidade: o conflito é entre agentes do próprio time, e o envio sem `--force` recusa a corrida no remoto. Por isso não é achado deste parecer. Vai em `Melhoria vista` do relatório como cartão possível (registrar no `erros.log` o Start tardio que encontra a branch já ocupada ou o autor trocado).
3. **O id que não está em `autores` segue como antes.** Sonda S4: o `SubagentStart` de um id fora de `autores` grava o registro sem `escrita`, como na base, e o disparo seguinte na `melhoria/a` dá 0 com o aviso H2. O teste `Autores.test_inicio_sem_autor_nao_reserva_branch` cobre o caso. O retorno antecipado do ramo novo também não toma a reserva sem id de outro disparo (sonda S7: a reserva do 2º escritor fica com o id dele, e o retomado A fica com o próprio registro).
4. **A função única de prazo não encurta nem alonga reserva de forma indevida** (`hooks/agentes.py:363`, usada em `:372` e `:994`). Comparei `prazo_do_registro` com as duas expressões antigas em 441 combinações: `id` ausente, vazio, 0, texto, lista, objeto, número; `tipo` ausente, vazio, `SendMessage`, outro, caixa trocada, lista; `expira_s` de 0 até infinito, com os vizinhos de RESERVA_S. A expiração (`dentro_do_prazo`) é idêntica nos 441 casos. A hora anunciada na recusa muda em 16 casos, todos com `tipo` igual a `SendMessage` e `expira_s` maior que RESERVA_S, e sempre para menos. Ela passa a ser a expiração real da reserva da retomada (o A5 corrigido). Nenhuma reserva muda de duração. O registro do Start tardio vale `expiracao_horas`, o mesmo que o retomado que inicia no prazo já recebe (conversão em `iniciar`). Não há prazo novo.

**Só aperta.** O único efeito novo sobre o estado é acrescentar uma reserva no `SubagentStart`, e só quando o id está em `autores`. Os ids vêm do Claude Code, e um subagente não forja o `SubagentStart`. A reserva nova cai no `SubagentStop` de A (fixture `autor-retomado-inicio-tardio-libera-no-fim`), pela expiração, ou pela liberação de pid morto, porque herda `sessao` e `pid` de `da_sessao`, como qualquer registro iniciado. Nenhuma recusa existente sumiu. Os mutantes I55, M22 e M23 só foram realinhados ao texto novo (o I55 agora aponta para um teste que mata a negação na função única).

Testes rodados aqui: `python3 -m unittest tests.test_hooks_agentes_autor` deu 13 testes, OK (os 3 novos e as fixtures `autor-*`). Suíte inteira: não rodei, conforme o brief. Ela fica com o CI do PR e com a entrega conferida da E87.1 (histórico do pedido, 17:51).

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas usadas: leitura do diff, sondas pelo runner de fixtures do próprio repositório e comparação exaustiva da função de prazo, tudo local e passivo. Não rodei varredura de segredos nem SAST, porque o diff só tem lógica de hook em Python da biblioteca padrão, sem dependência nova nem segredo.
