---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-copia-pasta
commit: 7884b151194706a0e9fcf2a1f216fe37525bac06
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0475-copia-pasta (E3.198, revalidação por delta)

Delta lido: `forge-check parecer delta docs/security/v0475-copia-pasta.md`, intervalo `7a3df21d..7884b151`. No domínio: só `skills/trabalho-em-paralelo/SKILL.md:10` ("serializam" trocado por "não andam em paralelo"). Já lido nas rodadas anteriores (no git, parecer em `7a3df21d`): `bin/forge-copia`, `docs/propostas/copia-pasta-settings.patch`, sem mudança neste delta.

## Gatilhos
Gatilhos: configuração do sandbox do modelo de projeto (`allowWrite`, ADR 0009), ferramenta que cria cópia git a partir de entrada do agente (`R-SEGURANCA`).

## Achados
- A3 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:10 · A troca tirou "serializam", exigido por tests/test_sobreposicao_quadro.py:377; a suíte falha no CI (parte 3/5, py3.12 e py3.14) e local. Use o texto da develop: "não andam em paralelo (serializam)", que satisfaz os dois testes.
- A2 (recomendado) docs/propostas/copia-pasta-settings.patch:8 · Aberto, sem mudança: o `allowWrite` na pasta inteira ainda dá à sessão de projeto escrita em `~/.forge-contrib/wt/*` e nos clones de outros projetos; a skill só orienta. Estreitar no `forge-init` por projeto.

## Sondas
- S1 · `python3 -m unittest tests.test_sobreposicao_quadro` no head 7884b151 · espera: OK · obtido: FAIL test_jarvis_serializa_antes_de_disparar_e_registra_o_quadro (AssertionError: 'serializam' not found)
- S2 · `gh run view 44231327074` (CI do head 7884b151) · espera: suíte verde · obtido: suíte parte 3/5 X em python 3.12 e 3.14, mesmo teste

## Detalhe dos achados
- **A3, defeito provado (não é vulnerabilidade):** a volta E3.184 trocou o texto para satisfazer `tests/test_jarvis_nucleo.py:201` ("Itens com arquivo em comum não andam em paralelo") e quebrou `tests/test_sobreposicao_quadro.py:377` ("serializam"). A `origin/develop` (`791d94e8`, mesma linha 10) traz as duas formas: "Itens com arquivo em comum não andam em paralelo (serializam): ...". Correção mínima: acrescentar " (serializam)" depois de "não andam em paralelo" na linha 10. Bloqueia porque a suíte do head está vermelha e o parecer não aprova sem suíte verde. Dono: `devops-engineer` (autor da volta E3.184).
- **A2, baixa:** mesma análise das rodadas anteriores; o delta não toca o patch nem o `bin/forge-copia`. Dono: `devops-engineer`.
- **A1:** fechado em `a108ef53`, sem regressão.

Conferido, sem achado de segurança: o delta é só texto de processo; a regra do lote continua inteira em `ritmo-e-corte.md:16`. Sem segredo, dependência, workflow nem rede no delta.

Provas: `python3 -I tests/catraca.py --base origin/develop` rc=0; `python3 -m unittest tests.test_jarvis_nucleo` 43 OK; `tests.test_metricas_texto` 2 OK; `tests.test_sobreposicao_quadro` 61 testes, 1 FAIL (S1). CI `44231327074` do head: suíte parte 3/5 vermelha (S2); `bateria (pareceres)` vermelha por parecer desatualizado (esperado, resolve-se com os novos pareceres).

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`: não rodados (o delta não toca segredo, dependência nem workflow).
