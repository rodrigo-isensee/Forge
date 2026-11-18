---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: 0b4b146a252b183e4a83e1065587daed889e8e40
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0475-copia-pasta (E3.221, revalidação por delta)

Delta lido: `forge-check parecer delta docs/security/v0475-copia-pasta.md`, intervalo `7884b151..0b4b146a`. No domínio: só `skills/trabalho-em-paralelo/SKILL.md:10-11` (linha 10 volta ao texto da `develop`, com "não andam em paralelo (serializam)"; linha 11 deixa só `forge-copia clone` como cópia citada). Já lido nas rodadas anteriores (no git, pareceres em `7a3df21d` e `7884b151`): `bin/forge-copia`, `docs/propostas/copia-pasta-settings.patch`, sem mudança neste delta.

## Gatilhos
Gatilhos: configuração do sandbox do modelo de projeto (`allowWrite`, ADR 0009), ferramenta que cria cópia git a partir de entrada do agente (`R-SEGURANCA`).

## Achados
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · Aberto, sem mudança: o `allowWrite` na pasta inteira ainda dá à sessão de projeto escrita em `~/.forge-contrib/wt/*` e nos clones de outros projetos; a skill só orienta. Estreitar no `forge-init` por projeto.

## Revalidação
- **A3 fechado em `0b4b146a`:** `skills/trabalho-em-paralelo/SKILL.md:10` igual à `origin/develop` (`git diff origin/develop` não toca a linha); `tests.test_sobreposicao_quadro` e `tests.test_jarvis_nucleo` passam (local e CI).
- **A1:** fechado em `a108ef53`, sem regressão.
- **A2, baixa:** mesma análise das rodadas anteriores; o delta não toca o patch nem o `bin/forge-copia`. Dono: `devops-engineer`.

Conferido, sem achado de segurança: o delta é só texto de processo; tirar "ou `worktree`" da linha 11 não remove controle (a regra de cópia segue no `bin/forge-copia`). Sem segredo, dependência, workflow nem rede no delta.

Provas: `python3 -I tests/catraca.py --base origin/develop` rc=0; `python3 -m unittest tests.test_sobreposicao_quadro tests.test_jarvis_nucleo tests.test_metricas_texto` 106 OK. CI `44235478693` do head: suíte 10/10 partes verdes (py3.12 e py3.14), teto de pulados verde; `bateria (pareceres)` vermelha por parecer desatualizado (esperado, resolve-se com os pareceres no head). Catraca `44235634436` verde.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`: não rodados (o delta não toca segredo, dependência nem workflow).
