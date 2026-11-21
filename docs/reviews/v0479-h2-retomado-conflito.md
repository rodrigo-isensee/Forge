---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-retomado-conflito
commit: 83d3b07d479ddc5ade6c4fdffc331aea7602e845
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E92.7, H2-RETOMADO-CONFLITO, revalidação)

Revalidação (H3, `R-REVIEW`) pelo `forge-check parecer delta`, intervalo `a98c1a53..83d3b07d`, domínio código e testes: `hooks/agentes.py`, 3 fixtures de `tests/hooks/agentes/` (1 nova), spec de mutantes, `docs/hooks.md`, `docs/hooks-fixtures.md` e o fragmento de changelog. Fora do delta nada foi relido.

## Delta lido
- A1 (anterior, o mesmo da segurança) corrigido: `hooks/agentes.py:1309` grava `escrita` inteira no registro do retomado, como na base; a linha do `erros.log` fica (`:1306-1308`, texto por `sem_controle` e cortado). Contra a base, a única mudança de comportamento é o aviso: o `R-TETO` não afrouxa.
- `autor-retomado-tardio-branch-tomada-avisa` espera agora rc 2 depois da queda da reserva viva: é a prova da S1 anterior (o retomado segura a branch).
- A2 (anterior) atendido: `autor-retomado-tardio-branch-mista` prova as duas metades, o `erros.log` cita só a tomada e a livre segue reservada pelo retomado (recusa com `melhoria/b`).
- Spec: M4 refeito sobre o registro (tira as tomadas) e M5 trocado (todas viram tomadas); os dois caem pelas fixtures acima. A guarda apagada (`livres = ...`) sai junto com o defeito.
- `docs/hooks.md` e o changelog descrevem o comportamento novo; `docs/hooks-fixtures.md` regerado (130 fixtures em `agentes`).

## Parecer
Aprovado no head 83d3b07d.

Ferramentas (citadas, não refeitas pelo review): `bin/forge-mutante` na spec, 1 processo: M1 a M5 morreram; `--cobertura --base a98c1a53`: só a spec editada e a guarda apagada da correção, sem guarda nova sem mutante. `tests.test_hooks_agentes_autor`: 13 testes OK; as 130 fixtures de `tests/hooks/agentes/` passam (4 puladas por falta do namespace de pid no sandbox). Suíte completa: fica com o CI do PR.
