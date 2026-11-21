---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-retomado-conflito
commit: a98c1a537f12e4c34213c27fa18cd213c8191d05
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E92.2, H2-RETOMADO-CONFLITO)

Diff `fb3b670b..a98c1a53`: 7 linhas em `hooks/agentes.py` (`iniciar`), 2 fixtures em `tests/hooks/agentes/`, spec com 5 mutantes, docs e fragmento de changelog. Dentro do teto H1 e com um comportamento só.

## Achados
- A1 (bloqueante) hooks/agentes.py:1309 · R-TETO afrouxa: o retomado tardio roda sem reserva da branch tomada; quando a viva cai, outro disparo de escrita passa com ele ainda escrevendo (base: ele a segura, S1). Correção: manter todas as branches no registro e a linha do erros.log.
- A2 (recomendado) tests/hooks/agentes/autor-retomado-tardio-reserva-viva-vale.json:1 · falta fixture do retomado com duas branches, uma tomada e outra livre; a partição só é provada por sonda direta em `iniciar`.

## Sondas
- S1 · iniciar() com viva afedcba… e autor a0123… em melhoria/a, depois SubagentStop da viva, em fb3b670b e a98c1a53 · espera: retomado em execução segue com melhoria/a (como na base) · obtido: base ['a0123456789abcdef']; head [] (branch sem reserva)

## Parecer
Reprovado (A1, o mesmo defeito do A1 da segurança em `docs/security/v0479-h2-retomado-conflito.md`, reproduzido aqui de forma independente pela S1). O `SubagentStart` não recusa: o retomado roda de qualquer jeito, então tirar a branch do registro dele não protege a reserva viva, só deixa a branch descoberta depois que ela cai. Correção sugerida: o registro do retomado mantém `escrita` inteira (como na base), o conflito segue no `erros.log`; a fixture `autor-retomado-tardio-branch-tomada-avisa` passa a esperar a recusa depois da queda da viva, e o M4 deixa de ser morto por ela. Os mutantes M2, M3 e M5 caem com a mudança; refaça a spec só com as guardas que sobrarem.

O que está certo: a linha do erros.log (texto passado por `sem_controle` e cortado; o `aid` só chega aqui se casar com `autores`, já validado), e o próprio registro do retomado não entra em `ocupadas` (o `iniciar` sai antes se o id já está em `agentes`).

Ferramentas (citadas, não refeitas): `bin/forge-mutante` na spec: M1 a M5 morreram; `--cobertura --base fb3b670b`: as guardas do diff estão todas declaradas. `tests.test_hooks_agentes_autor`: 13 testes OK; as 129 fixtures de `tests/hooks/agentes/` passam (4 puladas por falta do namespace de pid no sandbox). Suíte completa: fica com o CI do PR.
