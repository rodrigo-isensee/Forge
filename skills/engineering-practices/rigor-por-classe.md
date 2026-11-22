# Rigor por classe e gatilhos

Detalhe da `R-REVIEW` (diretriz 25: o resumo fica na regra). A classe e os portões vêm de `forge-check classe`.

- **T:** autor, 1 review e CI.
- **T de texto ou de teste (G1.3; D2):** diff todo de `.md`, inclusive agente, skill, modelo, `CLAUDE.md` e `docs/regras/`, ou todo de testes, inclusive os de controle (`tests/test_*.py` e `tests/hooks/`), sem remoção nem link, é T: só o review. `docs/regras/` soma a segurança pelo gatilho, sem QA. Seguem C: o resto de `CONTROLES_DO_FORGE`, `stacks/*/pronto.md` e `seguranca.md`, o `.md` em `.claude/` (salvo `CLAUDE.md`), binário, cabeçalho de agente ou skill mudado, o código de controle em `tests/` (`catraca.py`, `neutralidade.py`, todo `.py` da raiz fora de `test_*.py`) e a mistura de texto ou teste com código. A isenção M13 saiu. A catraca mede o `.py` enfraquecido; a fixture de `tests/hooks/` mudada só tem o review. Reversão: 1 escape de segurança em item T de texto de controle.
- **N:** review ∥ QA e CI.
- **C:** review ∥ segurança ∥ QA e CI, mais devops com infra (`docs/devops/<pedido>.md`).

## O que bloqueia e a revalidação (`R-REVIEW`, `R-SEGURANCA`)
- Bloqueante sempre com evidência: repro, teste que falha ou `arquivo:linha`; na segurança, com o caminho de ataque.
- **Revalidação só no delta (G1.2):** a 1.ª rodada lista todos os achados. Na revalidação, o bloqueante novo fica num trecho mudado entre o `commit:` anterior e o atual (margem de 3 linhas) ou repete um bloqueante da rodada anterior (mesmo id e arquivo); o achado cita a linha mudada que causa o defeito, não onde o sintoma aparece. Fora disso, vira `recomendado` e cartão, e o `forge-check pr` e o `docs` recusam o parecer. Exceção: segurança com `explorável: S<n>` no achado e a sonda `S<n>` em `## Sondas`. Reversão: 2 escapes em 14 dias vindos de achado rebaixado.

## Gatilhos de segurança (`R-SEGURANCA`)
A ferramenta acha os óbvios pelo diff; o plano marca os outros em `gatilhos_seguranca`.
