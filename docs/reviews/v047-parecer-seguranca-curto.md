---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-parecer-seguranca-curto
commit: c2138efd8de14c9412bc8f6e6bced8187a8b5283
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047-parecer-seguranca-curto (E2.377, revalidação por delta; entrega E2.364)

Revalidação por delta no head c2138efd. A rodada anterior (head 02fe845d, E2.278) fica no git e não é recopiada.

## Delta lido
`forge-check parecer delta docs/reviews/v047-parecer-seguranca-curto.md`, intervalo `02fe845d..c2138efd`, sem o que veio da develop (merge c2138efd): no domínio só `agents/security-engineer.md` (commit f60b080a, enxugado para o teto; 7148 → 6803 bytes).

## Achados
- A1 (recomendado) skills/cyber-security/SKILL.md:18 · estado: aberto, cartão para a skill `cyber-security` (numerar as mitigações M<n>.<m>); o delta não o toca.
- A2 (recomendado) bin/forge-check:3039 · estado: aberto, cartão para depois da integração do bin/forge-check; o delta não o toca.

## Sondas

## Parecer
Aprovado. O delta só reescreve texto, sem guarda nova (sem mutante declarado). Saem duas frases e o que elas diziam continua coberto: "nunca leva código de produção" (item 6) já decorre de "commit próprio que só toca esse arquivo"; "as varreduras rodam no CI do projeto" e "análise avançada paga fica fora" seguem em `skills/cyber-security/SKILL.md:34`. Os invariantes de `tests/config.json` para o agente seguem presentes, as regras continuam citadas pelo ID (`R-SEGURANCA`, `R-CUSTO`, `R-CONFORMIDADE`, `R-DECISAO`, `R-REVIEW`) e nada afrouxa (`R-CONTRIB`).

Testes rodados na raiz do clone, no head c2138efd:
- `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.RegrasComId tests.test_forge.Orcamento`: 8 testes, OK.
- `python3 -m unittest tests.test_orcamento_instrucao tests.test_achado_teto_doc tests.test_modelos_citados tests.test_reval_delta`: 25 testes, OK.

Suíte: a suíte inteira roda no CI do PR, que ainda não existe (o brief pede sem PR); o merge espera o CI verde. Nenhuma classe repetida em `docs/engineering/achados-recorrentes.md`: sem linha AR nova.
