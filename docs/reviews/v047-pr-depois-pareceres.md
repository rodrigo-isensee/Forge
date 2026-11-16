---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pr-depois-pareceres
commit: dc0f9de88d63b1c9b3b4c1a60b7fe3ebd006a7c7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (E1.6 e E1.23, code review da E1.3, classe C)

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

## Revalidação (E1.23, delta a8e80f2e..2530ab49, volta E1.9)
Delta lido por `forge-check parecer delta`: agents/tech-lead.md (linhas 36 e 37 fundidas numa só), skills/trabalho-em-paralelo/SKILL.md (linhas 14 e 17), fragmento do changelog.
- A1 corrigido: a regra e o rascunho cabem numa linha (`--draft`, depois do push e dos pareceres no head, `forge-check classe`, marcar pronto); orçamento verde.
- A2 corrigido: voltaram "150 linhas alteradas de código e teste" e "uma classe de comportamento por PR" ao texto do Jarvis; TetoPorPr verde.
- A3 corrigido (fusão das linhas).
- A4 (recomendado): frase em R-FLUXO não coube nos tetos e foi revertida; segue como recomendado, não bloqueia.
Aprovado no head 2530ab49. Prova: os mesmos 10 módulos afetados, `Ran 112 tests`, `OK` (o CI do PR, quando houver, é a suíte inteira).

## Revalidação (E1.48, delta 2530ab49..dc0f9de8)
Delta lido por `forge-check parecer delta` (escopo sem o que veio da base): agents/tech-lead.md (linha 36 enxugada, 8637 para 8615) e skills/trabalho-em-paralelo/SKILL.md (linha D2, 3035 para 3006); o resto do intervalo é a junção com a `develop`, sem marcadores de conflito (a linha D2 da skill ficou a da branch sobre a base da develop).
- Nada se perdeu: a regra segue com `--draft`, depois do push e dos pareceres aprovados no head, e `gh pr ready` pelo tech-lead; D2 mantém "o PR abre com os pareceres aprovados no head" e CI verde para entrar na `develop` (`R-FLUXO`). Cortaram-se só "da classe" (a ferramenta `forge-check classe` decide o alcance) e "O CI roda uma vez"; `TetoPorPr` (150 linhas, uma classe por PR) e `RegrasInviolaveis` seguem verdes.
- A4 (recomendado) segue aberto, não bloqueia.
Aprovado no head dc0f9de8. Prova: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.TetoPorPr tests.test_orcamento_instrucao tests.test_forge.Neutralidade`: `Ran 17 tests`, `OK`. CI do PR 528: suíte 3/3 e 2/3 de 3.12, 2/3 de 3.14, bateria, catraca e instalação verdes; partes restantes pendentes na leitura.
