---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: bd282fa7f5cfaf04f4c6b1bfe035e35853dc5a55
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (AMBIENTE-SEM-AUTO-UPDATE, E1.92)

## Achados
- A1 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:17 · a linha "Tamanho por risco" saiu e a regra do teto (150 linhas, uma classe por PR em hooks/) deixou de existir no texto do Jarvis; TetoPorPr falha 2 subtestes em agents/jarvis.md (passa em afba389e); R-REVIEW
- A2 (recomendado) bin/forge-testes:103 · o módulo novo entrou no meio da tupla LEITORES_DE_TEXTO, que ficou com a linha mais longa; melhor no fim, ou em linha própria, para o diff ficar legível
- A3 (recomendado) README.md:51 · o parágrafo novo traz cinco ideias numa linha só (motivo, data, nome da opção, atualizar de propósito, retomada); a mesma orientação já está curta no modelo de projeto, dá para encurtar

## Sondas

## Parecer
Reprovado por um bloqueante. A orientação ao dono (README e modelo do projeto) e a retomada na skill estão corretas e cobertas pelo teste novo (2 testes, passam). Mas o commit remove a linha "Tamanho por risco" da skill trabalho-em-paralelo sem mover a regra: agents/jarvis.md a lê dessa skill (texto_do_jarvis), e o teste TetoPorPr.test_orientacao_e_classe_unica_no_jarvis_no_tech_lead_e_na_skill exige "150 linhas alteradas de código e teste" e "uma classe de comportamento por PR em `hooks/`, com corpus próprio" no texto do Jarvis. Rodado no head: FAILED (failures=2); no Base-sha: OK. Perda de regra real: o tech-lead e engineering-practices ainda a guardam, mas o Jarvis, que orienta o autor, não. Correção: devolver a linha (encurtada) em outro ponto do texto do Jarvis ou ajustar o teste com o dono do teto, sem afrouxar. O CI do PR cobriria o mesmo; não há PR aberto.

Dentro do alcance: sem mudança de guarda em código (só tupla de módulos), sem mutante a declarar. Tamanho: bin/forge-testes e tests/*.py somam 26 linhas, dentro da orientação. Itens do Entregar conferidos contra o commit bd282fa7: orientação ao dono e retomada presentes.
