---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp12-dado-real
commit: 82277931ea878065aea1c2edfa5f14fbbd41759f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E144.3, BP12, PR #832)

Diff `0ed441e9..82277931`: `skills/ux-design/SKILL.md` (4 linhas), `templates/projeto/docs/constituicao.md` (1 linha), fragmento `changelog.d/v0480-bp12-dado-real.md`. Só documentação; sem guarda de código, sem mutante a declarar.

## Requisito (BP12, `docs/propostas/boas-praticas-1911.md`)
- A parte do discovery está coberta: a etapa Empatizar pede "prova de dado real antes de painel simulado", e a constituição do modelo fixa o portão (coleta real ou amostra anonimizada, com origem, data e quantidade; sem ela o painel é hipótese).
- A segunda metade do BP12 (o QA não aprova teste de banco ou navegador que não rodou) fica fora deste PR, e o fragmento do changelog diz isso ("só a parte do discovery").

## Os três trechos enxutos da skill
1. Validar: "deve conseguir fazer" vira "deve fazer". Mesmo requisito; nada perdido.
2. Especificar: "Formato da seção ... abaixo, referenciando" vira "Seção ..., citando". A seção continua nomeada e a referência às etapas continua; nada perdido.
3. Regra do upstream: "Correções e tarefas técnicas sem impacto de interface" vira "Trabalho técnico sem impacto de interface". A condição que decide (sem impacto de interface) ficou; correção sem impacto de interface é trabalho técnico. Nada perdido.

## Neutralidade (R-NEUTRO)
Nenhum nome de projeto, stack ou regra de negócio no diff.

## Testes e CI
- Rodados no clone, só os dos arquivos tocados: `tests.test_metricas_texto` (2, OK; teto de 5117 caracteres da skill sem alteração) e `tests.test_forge -k ux -k constituicao -k Neutralidade -k metricas` (19, OK).
- CI do PR #832 na hora da leitura: catraca, baterias e instalação verdes; partes da suíte ainda pendentes. A suíte completa é do CI e não foi rerrodada aqui.

## Commits
Um commit, Conventional Commits em português; a mensagem explica o enxugamento sem subir o teto. Só documentação, dentro do H1.
