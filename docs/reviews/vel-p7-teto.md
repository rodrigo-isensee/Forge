---
tipo: review
contrato: 1
pedido: vel-p7-teto
branch: melhoria/vel-p7-teto
commit: ae10c85731aacab165aea36f10335e889a89721e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: vel-p7-teto

Diff lido: `234dbe0...ae10c85` (c44f4d5 e ae10c85), 2 arquivos: `agents/jarvis.md` (1 linha trocada) e `changelog.d/vel-p7-teto.md` (novo).

## Achados
- A1 (recomendado) agents/jarvis.md:44 · "linha de base do VEL-30MIN" cita um pedido e um estudo que não estão no repositório (o agente vai para todos os projetos); sugestão: na próxima mexida, citar só "p90 medido da 1.ª rodada" ou apontar um doc versionado no Forge.
- A2 (recomendado) agents/jarvis.md:44 · limite de 53 min sem critério de revisão no texto (o plano VEL diz rever após 10 entregas, n=17 com cauda de um caso só); sugestão: registrar a revisão no cartão de medição da P7, sem linha nova no agente.

## Conferência
- Frase nova de `agents/jarvis.md:44`: diz o limite (53 min), o alcance (review, segurança ou QA, 1.ª rodada), a ação (parado e relançado) e a conferência antes do relançamento; o trecho antigo "antes de relançar um lento, confira se o anterior ainda roda" fica literal. Faz o que o E1 pede, nem mais nem menos.
- p90 citado: conferido em `~/.forge-contrib/docs/propostas/vel-30min-linha-de-base.md:44` (portões 1.ª rodada, p90 53.0, n=17, `medido`).
- Tamanho: `wc -l agents/jarvis.md` = 109, dentro do `limite_linhas.agente` 110 (`tests/config.json:76`); nenhuma linha nova.
- Coerência: `docs/economia-de-tokens.md:13` (checar se está ativo antes de relançar) e `docs/praticas-agentes-pesquisa.md:87` (checar worktree/branch/commit do anterior) seguem valendo; a frase nova só acrescenta o gatilho de tempo, sem contradizer.
- Invariantes: nenhum trecho de `tests/config.json` protege essa frase; o E2 não pedia invariante novo (era condicional).
- Fragmento `changelog.d/vel-p7-teto.md`: seção `### Alterado`, uma linha, descreve a mudança.
- Teto M14: `git diff --numstat --no-renames 234dbe0...HEAD` dá 1+1 em `agents/jarvis.md` e 2+0 em `changelog.d/`; ambos fora da conta (texto `.md` e fragmento), logo 0 de 150 linhas de código e teste. Um comportamento só.
- Regras: `R-NEUTRO` sem nome de projeto nem stack (A1 é de rastreabilidade, não de neutralidade); `R-CUSTO` nada pago; nenhuma regra com ID afrouxada; sem gatilho de segurança (texto de processo).
- Ferramentas: `python3 -m unittest tests.test_forge tests.test_changelog tests.test_textos_dono_f7 tests.test_textos_dono_f10` no head revisado: `Ran 501 tests`, `OK (skipped=1)`. A suíte inteira fica com o CI do PR. Sem `docs/engineering/praticas.md` no Forge: sem regra "leitura" ou "ferramenta" extra.
- Commits: Conventional Commits em português, um por item (texto e fragmento).
- Achados recorrentes (PA-7): nenhuma classe de `docs/engineering/achados-recorrentes.md` se repete; a classe de A1 e A2 é "referência ou limite sem fonte versionada", sem linha AR nesta rodada (DECISÃO TÉCNICA 2026-10-29 15:28 do T1-CONF-ESCOPO-REV).

## Parecer
Aprovado. A mudança cumpre o E1 na mesma linha, com o número conferido na linha de base e o texto antigo preservado; A1 e A2 são recomendações que não devolvem.
