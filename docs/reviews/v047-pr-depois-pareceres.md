---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pr-depois-pareceres
commit: a8e80f2e1944aeee27126b3361afde4cb8345b5d
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v047 (E1.6, code review da E1.3, classe C)

Diff revisado: `a986c292...a8e80f2e` (agents/tech-lead.md +2/-1, skills/trabalho-em-paralelo/SKILL.md +2/-2, fragmento em changelog.d/). Sem PR aberto, logo sem CI: rodei só os módulos afetados (`forge-testes --listar`) a partir da raiz da worktree, e os mesmos módulos na árvore da base (`git archive a986c292`), que passam (11 testes, OK).

## Achados
- A1 (bloqueante) agents/tech-lead.md:36 · o bullet novo estoura o orçamento do agente: tests.test_orcamento_instrucao falha (agente_caracteres 8960 > 8615, total 30048 > 29861, marcadores 57 > 56); na base passa. Sugestão: fundir a regra na linha 37 (rascunho) e enxugar, sem subir teto.
- A2 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:17 · o encurtamento tirou regra: sumiram do texto do Jarvis "150 linhas alteradas de código e teste" e "uma classe de comportamento por PR" (minúscula); TetoPorPr.test_orientacao_e_classe_unica falha 2 subtestes, verde na base. Restaurar a linha da base.
- A3 (recomendado) agents/tech-lead.md:37 · com o PR aberto só depois dos pareceres, o rascunho (`--draft`) e o `gh pr ready` com pareceres aprovados ficam redundantes com a linha 36; uma linha só diz as duas coisas e devolve margem ao orçamento (A1).
- A4 (recomendado) docs/regras/R-FLUXO.md:15 · a regra nova vale no Forge e nos projetos e cita R-FLUXO, mas o texto único da regra não diz quando o PR abre; considerar uma linha lá e só o ID nos agentes, para o texto não viver em dois lugares.

## Sondas

## Parecer
Reprovado. A intenção da E1.3 está atendida e a regra cita `R-REVIEW` e `R-FLUXO` pelo ID, sem copiar a frase delas (conferido contra docs/regras/R-REVIEW.md e R-FLUXO.md). Mas a entrega quebra testes que passam na base (A1, A2: defeito provado, `R-REVIEW`), e o encurtamento da linha Tamanho por risco tirou regra protegida por teste (pergunta do brief: tirou, sim). A correção é de texto, sem código: A1 cabe fundindo as linhas 36 e 37 (A3); A2 é desfazer a mudança da linha 17 da skill e achar a folga noutra linha, se a skill tiver teto.

Provas (comando e saída):
- Módulos afetados no head (`python3 -m unittest tests.test_forge.TetoPorPr tests.test_forge.Neutralidade tests.test_forge.Referencias tests.test_forge.AntiDuplicacao tests.test_jarvis_nucleo tests.test_jarvis_n_jar_a tests.test_textos_034 tests.test_permissao_agentes_md tests.test_orcamento_instrucao tests.test_changelog`): `Ran 112 tests`, `FAILED (failures=3)`: TetoPorPr (arquivo='agents/jarvis.md', frase='150 linhas alteradas de código e teste'), idem frase 'uma classe de comportamento', Orcamento.test_nenhum_agente_passa_do_teto.
- `python3 -m unittest tests.test_forge.TetoPorPr tests.test_orcamento_instrucao` na base a986c292: `Ran 11 tests`, `OK`.
