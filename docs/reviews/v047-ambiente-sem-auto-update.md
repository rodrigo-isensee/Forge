---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: 93deca84eea3d06142d5f31fb7d26db3361d3cd2
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (AMBIENTE-SEM-AUTO-UPDATE, E1.92 e E1.96)

## Achados
- A1 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:10 · o corte tirou "(serializam)": test_sobreposicao_quadro.RegrasEmTexto.test_jarvis_serializa_antes_de_disparar_e_registra_o_quadro falha no head (passa em afba389e); devolver a palavra; R-REVIEW
- A2 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:10 · o corte tirou "e traz a `develop` uma vez" da série por arquivo: instrução que existia e a regra do dono de 13/11 proíbe apagar; devolver a frase
- A3 (recomendado) skills/trabalho-em-paralelo/SKILL.md:12 · saiu "Onde um pedido está: `forge-check proximo <pedido>`": a pista segue no título de agents/jarvis.md, mas era texto existente; devolver
- A4 (recomendado) skills/trabalho-em-paralelo/SKILL.md:13 · "avise o dono antes" virou "avise o dono": o "antes" fixa quando avisar; devolver
- A5 (recomendado) bin/forge-testes:104 · o módulo novo foi para o fim da tupla (A2 anterior resolvido), mas a linha ficou longa; opcional quebrar

## Sondas

## Parecer
Reprovado por dois bloqueantes, ambos na redação da skill, no head 93deca84. Delta lido: bd282fa7..93deca84 (README, bin/forge-testes, skills/trabalho-em-paralelo/SKILL.md); depois dele, a branch só ganhou pareceres de segurança e QA.

Resolvido: o A1 da volta anterior (teto). A linha "Tamanho por risco" voltou à skill com 150 linhas e a classe única em `hooks/`; `TetoPorPr` passa (3 testes) e `test_ambiente_sem_auto_update` passa. README encurtado (A3 anterior) e módulo no fim da tupla (A2 anterior).

Cortes de redação, julgados um a um contra a regra do dono (texto existente não se apaga nem se resume):
- "(serializam)": tirou regra de teste; A1.
- "e traz a `develop` uma vez": tirou instrução; A2. O R-FLUXO a guarda em geral, mas a skill a dizia ao Jarvis neste ponto.
- Ponteiro do `forge-check proximo`: pista existente, sobra no título do Jarvis; A3, recomendado.
- "avise o dono antes": A4, recomendado.
- Sem perda de regra: "(gargalo)", "enquanto couber no teto" para "no teto", "modo auto" para "auto", "não roda mais" para "parou", "revert do commit", "e encha as vagas", "com as regras" para "nas regras". Nenhum teste lê essas formas.

Provas rodadas aqui (sem PR, só afetados): test_sobreposicao_quadro 61 testes, 1 falha (A1); TetoPorPr OK; test_ambiente_sem_auto_update OK; test_achado_teto_doc e test_medidas_m14b OK. Sem guarda de código mudada: sem mutante a declarar. Tamanho: 5 linhas de código e teste no delta.
