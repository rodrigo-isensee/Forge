---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: baf1bee6aa7f6a7efad97b44cc409a576f8a7762
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047 AMBIENTE-SEM-AUTO-UPDATE (E1.93, revalidada por delta nas E1.97 e E1.105)

## Gatilhos
Nenhum gatilho da `R-SEGURANCA` tocado: só texto (README, modelo de projeto, skill `trabalho-em-paralelo`), um teste de texto e a lista `LEITORES_DE_TEXTO` em `bin/forge-testes`. Sem hook, guarda, workflow, segredo, permissão ou código de produção. Parecer dado por precaução, a pedido do brief.

## Achados

## Sondas

## Detalhe dos achados
Nenhum bloqueante e nenhum recomendado.
- Orientação de desligar a atualização automática da extensão (`README.md:51`, `templates/projeto/CLAUDE.md:24`): não afrouxa controle; o texto não fixa nome de opção nem manda baixar nada. Efeito colateral de segurança: a extensão deixa de mudar sozinha no meio do trabalho (cadeia de suprimentos); o texto manda atualizar de propósito entre entregas, então não congela correções de segurança.
- Retomada (`skills/trabalho-em-paralelo/SKILL.md:17`): relança agentes a partir de briefs já selados e do estado da branch; não cria autoridade nova, não pula portão, não toca `R-MAIN`. Sem caminho de ataque.
- Linha "Tamanho por risco" removida da skill: nenhuma regra se perdeu. O texto integral (150 linhas, um comportamento, `teto: excedido`, uma classe de comportamento por PR em `hooks/` com corpus próprio, e a lista do que conta no Forge) segue em `agents/tech-lead.md:21`, dono da regra (M14).
- `bin/forge-testes:103`: o novo módulo entra em `LEITORES_DE_TEXTO`, coerente com o que o teste lê; a linha ficou comprida, só estilo (vai ao `tech-lead`, se quiser).

## Revalidação por delta (E1.97, head 93deca84)
`forge-check parecer delta` desde bd282fa7: `bin/forge-testes` (só reordena `test_ambiente_sem_auto_update` dentro de `LEITORES_DE_TEXTO`, mesma lista, sem controle afrouxado) e `skills/trabalho-em-paralelo/SKILL.md` (cortes de redação; `R-CONFORMIDADE`, `R-TETO`, `R-WIP`, `R-FLUXO` e a recusa sem contornar seguem citados; a linha "Tamanho por risco" volta ao texto do Jarvis, sem perder a regra). README fora do domínio. Nenhum gatilho novo, nenhum achado. `tests.test_ambiente_sem_auto_update` rerrodado: 2 testes, OK. Sem PR, suíte inteira não citada (CI).

## Revalidação por delta (E1.105, head baf1bee6)
`forge-check parecer delta` desde 93deca84: no domínio, `bin/forge-testes` (a lista `LEITORES_DE_TEXTO` só foi quebrada em linhas, mesmos módulos, sem controle afrouxado) e `skills/trabalho-em-paralelo/SKILL.md` (volta ao texto da `develop`: `git diff afba389e..HEAD -- skills` vazio; a linha de retomada saiu, nenhuma regra nem recusa se perdeu). Fora do domínio: changelog e teste de texto. Nenhum gatilho novo, nenhum achado. `python3 -m unittest tests.test_ambiente_sem_auto_update`: OK. Sem PR, suíte inteira não citada (CI).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste novo rodado: `python3 -m unittest tests.test_ambiente_sem_auto_update` (2 testes, OK). A suíte inteira roda no CI; não havia PR, então não foi citada. Ferramentas de varredura não aplicáveis a texto.
