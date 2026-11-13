---
tipo: revisao-seguranca
contrato: 1
pedido: v047-pr-depois-pareceres
branch: melhoria/v047-pr-depois-pareceres
commit: a8e80f2e1944aeee27126b3361afde4cb8345b5d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v047-pr-depois-pareceres

## Gatilhos
Toca `agents/tech-lead.md` e `skills/trabalho-em-paralelo/SKILL.md` (texto de agente e skill que descrevem portões, `R-REVIEW`, `R-FLUXO`). Sem código, hook, workflow, segredo nem dependência.

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/SKILL.md:17 · "Tamanho por risco" perdeu "de código e teste" da contagem das 150 linhas; orientação sem trava, sem efeito de segurança.

## Sondas

## Detalhe dos achados
Análise do diff `origin/develop...a8e80f2e` (3 arquivos, 6 inserções, 3 remoções):
- A regra move a abertura do PR para depois dos pareceres aprovados e commitados no head. Reforça o portão (`R-REVIEW`): nenhum portão cai, nenhum afrouxamento. O merge continua exigindo CI verde, e a main continua só do usuário (`R-MAIN`).
- O texto em `agents/tech-lead.md` mantém o PR em rascunho e o `gh pr ready` só com pareceres aprovados; não cria atalho para pular degrau da `R-FLUXO`.
- Sem caminho de ataque realista: nada executável, sem permissão nova, sem entrada externa.
- A1: recomendação de redação (esforço P, dono tech-lead), não bloqueia.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Não houve PR, então sem CI; conferência local do diff e de `forge-check docs`. Sem ferramenta de varredura necessária (mudança só de texto).
