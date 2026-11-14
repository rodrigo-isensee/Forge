---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-pr-depois-pareceres
commit: dc0f9de88d63b1c9b3b4c1a60b7fe3ebd006a7c7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047-pr-depois-pareceres

## Gatilhos
Toca `agents/tech-lead.md` e `skills/trabalho-em-paralelo/SKILL.md` (texto de agente e skill que descrevem portões, `R-REVIEW`, `R-FLUXO`). Sem código, hook, workflow, segredo nem dependência.

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/SKILL.md:17 · corrigido na volta E1.9: "de código e teste" voltou à contagem das 150 linhas; fechado.
- A2 (recomendado) skills/trabalho-em-paralelo/SKILL.md:14 · a frase "o PR abre com os pareceres da classe aprovados no head" perdeu "só" e "commitados"; o portão segue em agents/tech-lead.md:36 (rascunho, `gh pr ready`) e no CI/merge; sem caminho de ataque.

## Sondas

## Detalhe dos achados
Análise do diff `origin/develop...a8e80f2e` (3 arquivos, 6 inserções, 3 remoções):
- A regra move a abertura do PR para depois dos pareceres aprovados e commitados no head. Reforça o portão (`R-REVIEW`): nenhum portão cai, nenhum afrouxamento. O merge continua exigindo CI verde, e a main continua só do usuário (`R-MAIN`).
- O texto em `agents/tech-lead.md` mantém o PR em rascunho e o `gh pr ready` só com pareceres aprovados; não cria atalho para pular degrau da `R-FLUXO`.
- Sem caminho de ataque realista: nada executável, sem permissão nova, sem entrada externa.
- A1: era recomendação de redação (esforço P, dono tech-lead), corrigida na volta E1.9.
- A2: recomendação de redação (esforço P, dono tech-lead); não bloqueia.

## Revalidação por delta (a8e80f2e..2530ab49, E1.24)
`forge-check parecer delta` apontou no domínio só `agents/tech-lead.md` e `skills/trabalho-em-paralelo/SKILL.md` (o fragmento de changelog está fora). Releitura do que toca controle do Forge: a volta E1.9 encurtou as frases para caber nos tetos; o parágrafo "PR depois dos pareceres" do tech-lead foi fundido na linha do rascunho, que mantém push, pareceres da classe aprovados no head e `gh pr ready`. Nenhum portão cai: `R-REVIEW`, `R-FLUXO`, CI verde no merge e `R-MAIN` intactos; texto sem código, hook, workflow, segredo ou dependência. A4 do review (revertido por não caber nos tetos) não muda a postura. Sem PR, sem CI: rodei `tests.neutralidade` e `tests.test_invariante_gatilho` (OK) e conferi o diff; a suíte inteira roda no CI do PR. Nenhum achado bloqueante.

## Revalidação por delta (2530ab49..dc0f9de8, E1.49)
`forge-check parecer delta` aponta no domínio `agents/tech-lead.md` e `skills/trabalho-em-paralelo/SKILL.md`; o resto do intervalo veio da base (develop) e fica fora. Os dois commits da branch: a junção com a develop (conflito na linha D2 resolvido mantendo a develop e a linha D2 da branch) e o enxugamento `dc0f9de8`, que mexe só em duas linhas. Diff contra `origin/develop`: a linha do tech-lead passa de "aberto pelo autor depois do push ... com os pareceres aprovados" para "depois do push e dos pareceres aprovados no head ... você o marca pronto"; a D2 passa a "o PR abre com os pareceres aprovados no head; CI verde, entra na `develop` (`R-FLUXO`)". Sem regra nem invariante perdida: `gh pr ready` pelo tech-lead, rascunho, `R-FLUXO`, CI verde e `R-MAIN` seguem; o enxugamento tirou só "da classe" e a menção a `forge-check classe` da linha (a ferramenta segue nas demais regras), mesma natureza do A2. Texto sem código, hook, workflow, segredo ou dependência. Testes rodados na worktree: `tests.test_orcamento_instrucao` (8, OK) e `tests.test_forge.RegrasInviolaveis` e `Neutralidade` (6, OK); a suíte inteira roda no CI do PR. Nenhum achado bloqueante.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem ferramenta de varredura necessária (mudança só de texto).
