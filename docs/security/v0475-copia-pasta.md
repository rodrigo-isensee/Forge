---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: 7a3df21d0869b4c97b852a9fc0924cba1b66e2c2
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0475-copia-pasta (E3.169, revalidação por delta)

Delta lido: `forge-check parecer delta docs/security/v0475-copia-pasta.md`, intervalo `a108ef53..7a3df21d`, sem o que veio da base. No domínio: só `skills/trabalho-em-paralelo/SKILL.md:12,16-17` (a frase de anotar devolvida; a regra do lote por arquivo encurtada com remissão a `ritmo-e-corte.md:16`, onde o texto inteiro está; linha nova "CI pago" remetendo a `ritmo-e-corte.md:18`). Fora do domínio: `tests/mutantes/v0475-copia-pasta.json`, `tests/test_forge_copia.py` (mutantes M11-M14). Já lido nas rodadas anteriores (no git, parecer em `a108ef53`): `bin/forge-copia` e `docs/propostas/copia-pasta-settings.patch`, sem mudança neste delta.

## Gatilhos
Gatilhos: configuração do sandbox do modelo de projeto (`allowWrite`, ADR 0009), ferramenta que cria cópia git a partir de entrada do agente (`R-SEGURANCA`).

## Achados
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · Aberto, sem mudança: o `allowWrite` na pasta inteira ainda dá à sessão de projeto escrita em `~/.forge-contrib/wt/*` e nos clones de outros projetos; a skill só orienta. Estreitar no `forge-init` por projeto.

## Sondas

## Detalhe dos achados
- **A1:** fechado em `a108ef53` (rodada anterior), sem regressão no delta.
- **A2, baixa:** mesma análise da rodada anterior; o delta não toca o patch nem o `bin/forge-copia`. Dono: `devops-engineer`.

Conferido, sem achado: o delta da skill é só texto de processo; nenhuma frase de controle de segurança saiu (a regra do lote continua inteira em `ritmo-e-corte.md:16`). Sem segredo, dependência, workflow nem rede no delta.

Provas: `python3 -I tests/catraca.py --base origin/develop` rc=0; `python3 -m unittest tests.test_forge_copia` 14 testes OK; `tests.test_metricas_texto tests.test_ambiente_git` (com o anterior) 36 testes OK. Suíte: CI do head `7a3df21d` na fila (`gh run list`), Catraca verde; a suíte inteira é o portão do merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`: não rodados (o delta não toca segredo, dependência nem workflow). Lacuna mantida: o patch é proposta; os projetos já criados só recebem o `allowWrite` pela migração (ADR 0005).
