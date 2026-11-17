---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: f26b0721cc27c5460c37e910544587bf742126ef
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474, H2-AUTOR-FICA-ATE-O-MERGE (E2.65, volta por delta)

Delta lido (`forge-check parecer delta`, `482ee7c7..f26b0721`), no domínio: `hooks/agentes.py` (`vigentes` com o prazo curto para o registro `SendMessage`, `iniciar` que converte a reserva da retomada, docstring de `reservar_retomada`), `tests/test_hooks.py` (aviso exige stdout; medida com `rpartition` e cauda conferida) e os fixtures `autor-retomada-reserva-curta-expira` e `autor-retomado-inicio-vira-reserva-do-agente`. Fora do domínio: `docs/hooks-fixtures.md` e as specs de mutante (M19/A4). Já lido (no git, `482ee7c7` e antes): o resto do H2.

## Gatilhos
Gatilhos: guarda em hook de controle (`R-TETO`, uma delegação de escrita por branch), leitura de estado que um agente pode corromper (`.forge/run/agentes.json`).

## Achados
- A3 (recomendado) tests/test_hooks.py:838 · corrigido: rpartition e a cauda exigida em "/.forge/run/agentes.json"
- A4 (recomendado) hooks/agentes.py:987 · SubagentStart do retomado depois de RESERVA_S (300 s) acha a reserva da retomada já vencida: o autor volta a escrever sem reserva e um segundo escritor passa na branch dele (sonda S8); reservar de novo as branches de `autores` do id no iniciar
- A5 (recomendado) hooks/agentes.py:745 · a recusa por reserva de retomada (tipo SendMessage, com id) anuncia a expiração por expiracao_horas, mas ela vale RESERVA_S: a hora dita sai até 2 h depois da real (sonda S11: 18:00 para ~16:03)

## Sondas
- S8 · estado com retomada de A há 400 s, SubagentStart de A, disparo Explore com brief em melhoria/a · espera: R-TETO (A escreve a branch) · obtido: código 0, disparo gravado
- S11 · retomada de B há 100 s em melhoria/a, SendMessage para A (autor de melhoria/a) · espera: recusa com a expiração às agora+200 s · obtido: recusa "expiração às 18:00" com agora 16:02

## Detalhe dos achados
**Prazo curto da retomada: abre janela para um segundo escritor?** Não no caminho normal. A documentação oficial do Claude Code (hooks, seção SubagentStart, consultada hoje) diz que o `SubagentStart` dispara também quando o Claude retoma um subagente, e `hooks/hooks.json` registra o `agentes` no `SubagentStart` sem matcher: o retomado converte a reserva em registro do agente (tipo dele, `desde` novo, prazo de `expiracao_horas`, branches mantidas) antes de escrever. Entre o `PreToolUse` e o `SubagentStart` a reserva curta segura a branch (S1, S6). Sem `SubagentStart` (negado ou falho), ninguém escreve, então soltar em 300 s é o certo (S2, S3). A janela que sobra é o `SubagentStart` que chega depois de 300 s (permissão pendente com a pessoa, fila): a reserva já caiu e o `iniciar` registra o id sem branches (ou casa uma reserva pendente sem id, comportamento da base para qualquer agente). Mesma troca já aceita para o `Agent` (reserva sem `SubagentStart` vale `RESERVA_S` desde a base); sem atacante (o risco é o próprio Jarvis disparar o segundo escritor), severidade baixa (A4). Correção mínima: no `iniciar`, sem registro do `aid` e com o `aid` em `autores_vigentes`, anexar o registro com as branches de escrita dele que nenhuma reserva vigente ocupa. Esforço P. Dono: `software-engineer`.

**`iniciar` (`hooks/agentes.py:985-990`).** Conferido sem achado: casa só registro com o mesmo `agent_id` e tipo `SendMessage`, não toca reserva pendente sem id de outro disparo (S7), não muda sessão nem pid. Um `agent_type` vazio ou qualquer valor diferente de `SendMessage` leva o prazo longo, o lado que segura a branch. Forjar o estado segue sem capacidade nova (quem grava o arquivo já apaga as reservas).

**A5.** `recusar_branch_ocupada` usa `expira_s` para todo registro com id, e a reserva de retomada tem id e prazo curto. Só a mensagem erra (a recusa em si está certa); a pessoa espera à toa. Correção mínima: usar `min(RESERVA_S, expira_s)` também quando `tipo == RETOMADA`, a mesma condição de `vigentes`. Esforço P. Dono: `software-engineer`.

**Sondas refeitas no head** (12, pelo executor de fixtures de `tests/test_hooks.py`, com o `erros.log` conferido), todas como esperado em `f26b0721`: retomada negada ou sem `SubagentStart` (S1 reserva com 290 s recusa o disparo; S2 com 310 s libera; S3 `SendMessage` + `SubagentStop` sem início solta a branch; S4 `SendMessage` de novo depois do prazo reserva outra vez); retomada com `SubagentStart` (S5 registro convertido com 400 s ainda recusa; S6 `SendMessage`, `SubagentStart`, disparo: recusa "ocupada por forge:software-engineer"; S7 o início não rouba a reserva pendente); S8 (A4); retomada com branch ocupada (S9 por reserva pendente, S10 por agente ativo com 1000 s, S11 por outra retomada: recusa; S12 por retomada vencida: reserva). Na cópia de `482ee7c7`, S2, S6, S7, S8 e S12 falham, o que prova que distinguem a mudança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI; a consulta de execuções da branch não trouxe nenhuma (sem PR), então o portão do PR segue exigindo o CI verde. Rodei `tests/test_hooks_agentes_autor.py` no head (10 testes, OK, 22 fixtures `autor-*`) e as 12 sondas no head e na base. `gitleaks` ausente do PATH (lacuna; o delta não traz credencial nem configuração). Workflows fora do delta.
