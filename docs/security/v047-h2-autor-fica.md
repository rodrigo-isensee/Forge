---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 482ee7c773597cad435a49acbee8fb535b802493
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474, H2-AUTOR-FICA-ATE-O-MERGE (E2.60, volta por delta)

Delta lido (`forge-check parecer delta`, `6d73898a..482ee7c7`), no domínio: `hooks/agentes.py` (`AUTORES_MAX`, `guardar_autores`, `autores_retomaveis`, `reservar_retomada` nova, `lancar` devolvendo o aviso pendente, aviso emitido depois do `gravar_json` em `atualizar_estado`), `tests/test_hooks.py` (ramo `aviso` e medida da linha do stderr), `tests/test_hooks_agentes_autor.py` e os 8 fixtures `autor-*` novos. Fora do domínio: o fragmento de changelog, `docs/hooks-fixtures.md` e as specs de mutante. Já lido na rodada anterior (no git, `6d73898a`): o resto do H2 e o executor de fixtures.

## Gatilhos
Gatilhos: guarda em hook de controle (`R-TETO`, uma delegação de escrita por branch), leitura de estado que um agente pode corromper (`.forge/run/agentes.json`).

## Achados
- A3 (recomendado) tests/test_hooks.py:837 · a medida corta no primeiro "; registro em ": texto de recusa que o contenha antes da cauda real é medido curto, e a cauda não é conferida; usar rpartition e exigir que a cauda termine em "/.forge/run/agentes.json"

## Sondas

## Detalhe dos achados
**Achados anteriores.** A1 (bloqueante): corrigido. `hooks/agentes.py:472` só põe id texto no conjunto, e o aviso sai depois do `gravar_json` (`hooks/agentes.py:1074-1077`): mesmo que o aviso falhasse, a reserva já está gravada. Minhas S1 e S2 viraram `autor-lapide-id-lista-reserva` e `autor-lapide-id-lista-segundo-recusa`; o registro de id objeto, `autor-registro-id-objeto-reserva`. A2 (recomendado): atendido, `tests/test_hooks.py:820-827` exige o stdout só com `systemMessage` e cada linha do stderr no formato de aviso.

**Retomada que reserva (`reservar_retomada`, `hooks/agentes.py:499-511`).** Conferido sem achado: (1) roda depois de `recusar_retomada` (C8, falha fechada intacta); (2) `to` fora da forma (número, booleano, nulo, lista, objeto, texto vazio, id em maiúsculas) não casa autor nenhum, já que `autores_vigentes` só guarda id texto com `ID_DE_AGENTE`: libera sem reservar e sem erro interno, igual à base; (3) alvo ativo: nada reserva e nada recusa; (4) branch do autor ocupada (reserva pendente ou retomada de outro autor): recusa R-TETO; (5) o registro da retomada leva `desde=agora` e a sessão, então a notificação terminal antiga do autor (anterior ao `desde`) não o libera como morto (`hooks/agentes.py:401`); o `SubagentStop` do alvo solta a reserva e o devolve a `autores`. Forjar `autores` no estado agora decide uma reserva, mas só produz recusa (lado seguro) ou a ausência dela, que quem grava o estado já obtém apagando `agentes`: nenhuma capacidade nova. Limite de desenho, sem caminho provado: a reserva olha só `to`; uma retomada endereçada por outra forma que o Claude Code aceite não reservaria (como na base).

**`guardar_autores` e `AUTORES_MAX`.** O autor anterior perde só as branches tomadas; a lista tem teto próprio de 64 e só roda no `SubagentStop`. Sem achado.

**Limite de 200 caracteres (A3).** Não afrouxa o controle: o teto vive em `_comum.mensagem` (`hooks/_comum.py:2506-2510`), que corta o texto em `LIMITE_MENSAGEM` e só depois anexa a cauda; o teste passa a medir exatamente a parte que a função limita, e a cauda (o caminho do estado, sem caracteres de controle, que o usuário precisa abrir) só é usada em `hooks/agentes.py:751`. O afrouxamento fica no teste: (a) `partition` corta no primeiro "; registro em ", então um texto de recusa que o trouxesse (branch ou tipo vindos da entrada) seria medido curto; (b) nada confere que o que vem depois é a cauda do caminho, então uma regressão que pusesse texto livre na cauda passaria. Severidade: baixa (só cobertura de teste, sem caminho de ataque). Correção mínima: `rpartition` e `assertTrue(cauda.endswith("/.forge/run/agentes.json"))` quando houver cauda. Esforço: P. Dono: `qa-engineer`.

**Sondas refeitas no head** (38, pelo executor de fixtures de `tests/test_hooks.py`, que confere também o `erros.log` vazio), todas como esperado: id de todo tipo (1, 1.5, true, null, lista, objeto, lista aninhada, "") em `agentes` e `lapides`, com `autores` lixo: disparo gravado com o aviso (8) e o segundo escritor recusado (8); retomada com o mesmo estado lixo (sem lápide de id lista): reserva (8); lápide de id lista e retomada: recusa C8 com o erro no `erros.log` (falha fechada, como na base); retomada com branch ocupada por reserva pendente: recusa; duas retomadas de autores da mesma branch: a segunda recusa; retomada de agente ativo: nada reserva; `to` fora da forma (9): libera sem reservar; retomada, `SubagentStop` do alvo e novo disparo: passa com o aviso. Na cópia de `6d73898a`, 26 delas falham (A1 e a retomada sem reserva), o que prova que distinguem a correção.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; não consegui consultar execução de CI da branch (sem PR; a consulta não respondeu), então o portão do PR segue exigindo o CI verde. Rodei `tests/test_hooks_agentes_autor.py` no head (10 testes, OK, inclui os 20 fixtures `autor-*`) e as 38 sondas no head e na base. `gitleaks` ausente do PATH (lacuna; o delta não traz credencial nem configuração). Workflows fora do delta.
