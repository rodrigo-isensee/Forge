---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-retomado-conflito
commit: a98c1a537f12e4c34213c27fa18cd213c8191d05
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E92.3, H2-RETOMADO-CONFLITO)

Escopo: `hooks/agentes.py` (ramo do retomado tardio no `iniciar`), duas fixtures novas, mutantes M1 a M5, `docs/hooks.md`, `docs/hooks-fixtures.md`, fragmento do changelog. Base `fb3b670b`, head `a98c1a53`. A janela A5 (entre os 300 s da reserva curta e o `SubagentStart`) fica fora por decisão e não é contada.

## Gatilhos
Gatilhos: hook de controle do R-TETO (reserva de escrita por branch), registro no erros.log.

## Achados
- A1 (bloqueante) hooks/agentes.py:1309 · Não só aperta: o retomado fica sem reserva da branch tomada pela vida inteira dele; quando a reserva viva cai, um disparo novo de escrita na branch passa (rc 0) com o retomado ainda rodando, e o aviso manda retomar o outro. Na base, rc 2 (S1, S2).

## Sondas
- S1 · fixture ...branch-tomada-avisa com esperado codigo 2, stderr "R-TETO: melhoria/a ocupada por forge:software-engineer" (viva B, SubagentStart do retomado A, SubagentStop de B, Agent em melhoria/a) · espera: rc 2, como na base fb3b670b (passou) · obtido: no head, rc 0 com aviso
- S2 · a mesma sequência de S1, esperado aviso contendo a0123456789abcdef · espera: o aviso aponta o retomado que segue rodando · obtido: "autor retomável (melhoria/a: afedcba9876543210): retome-o por SendMessage", o agente que já parou

## Detalhe dos achados
**A1.** Evidência: `hooks/agentes.py:1304-1310` grava o retomado só com `livres`; a fixture `tests/hooks/agentes/autor-retomado-tardio-branch-tomada-avisa.json:60` fixa como esperado o `codigo: 0` do disparo seguinte, e o mutante M4 (`livres = escrita`) morre justamente por essa fixture, isto é, o teste trava o afrouxamento.

Caminho: o Jarvis retoma o autor A por `SendMessage`; o `SubagentStart` de A chega depois dos 300 s, quando B já reserva a branch (A5, fora). Até aqui, base e head têm dois escritores (A e B), e o head ainda registra o conflito no erros.log, o que é ganho. Mas B termina antes de A: na base, o registro de A segue e o terceiro disparo de escrita na branch é recusado (rc 2, "ocupada por forge:software-engineer"); no head, A não tem registro na branch, o terceiro disparo passa (rc 0) e o aviso do H2 diz para retomar B (que parou), escondendo que A está ativo. Resultado: dois escritores na mesma branch por até `expiracao_horas`, fora da janela A5, que a base recusava. O erros.log tem a linha do conflito, mas o vigia só a mostra no Stop, depois do disparo. Severidade: média (controle de coordenação do R-TETO; quem dispara é o próprio Jarvis, sem atacante externo; efeito: push concorrente e trabalho sobrescrito na branch). O pedido exige "só aperta"; este caminho afrouxa frente à base, por isso bloqueia.

Correção mínima (P, dono: tech-lead, autor da E92.1): manter no registro do retomado todas as branches de `escrita` (como na base; o registro dele não apaga nem altera o da reserva viva, que segue valendo e recusando) e manter a linha `H2-RETOMADO-CONFLITO` no erros.log quando houver `tomadas`. Trocar a fixture `...branch-tomada-avisa` para esperar rc 2 ("ocupada por forge:software-engineer") depois do `SubagentStop` da viva, e ajustar o M4 (que passa a ser o próprio código) para um mutante que tire as `tomadas` do registro e morra nessa fixture. Se o time preferir manter o desenho "a reserva viva vale e o retomado fica sem ela", isso afrouxa e é DECISÃO DO DONO (R-DECISAO), não do time.

O que está bem (sem achado):
- Branch livre: com `escrita` [a, b] e só `a` tomada, o retomado segue com `b` (rc 2 no disparo em `b`; a linha do erros.log cita só `a`). A base não registrava o conflito. Sonda verde no head.
- Reserva vencida (fora de `vigentes`) e reserva de parecer (sem `escrita`) não tomam a branch: o retomado a mantém (rc 2 no head e na base).
- O próprio registro do retomado não conta como "outra": o `iniciar` sai antes se o id já está em `agentes` (`hooks/agentes.py:1296-1300`).
- Linha forjada no erros.log: as branches passam por `sem_controle` e corte de 80 caracteres; o id do agente vem de `autores`, que só guarda id na forma (`guardar_autores`); `registrar_erro` junta os espaços e corta em 300. Sem caminho.
- O aviso não esconde o conflito no momento do `SubagentStart` (a linha vai ao erros.log, a fixture `...reserva-viva-vale` prova); ele só engana depois que a viva cai, que é o caminho do A1.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Janela A5 fora por decisão registrada no pedido. Suíte inteira não rodada (CI do PR); rodadas só as 5 sondas pelo harness de fixtures de `tests/test_hooks.py`, no head e numa cópia da base por `git archive`, com TMPDIR próprio em `/root/.forge-contrib/wt/sondas-E923-cYvg`. Ferramentas externas de varredura não se aplicam a esta mudança.
