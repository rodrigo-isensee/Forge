---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-ja1
commit: 3af10697072d98ce2cd78b6a8723acba350459ce
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047-jarvis-ja1 (E2.230, lote JA1 da E2.180)

Parecer completo (não havia parecer anterior). Diff `4138445e..3af10697`: `skills/falar-com-o-dono/SKILL.md` (a ferramenta passou a classe para C), testes de texto em `tests/test_jarvis_nucleo.py`, eval em `tests/evals/test_erros_por_papel.py`, fragmento de changelog e a contagem do AR-4.

## Gatilhos
Regra de processo do Jarvis (`R-DECISAO`, `R-FLUXO`): nenhum hook, workflow, código de guarda, segredo nem permissão tocados. Revisão do que o texto novo poderia afrouxar (decisão do dono, portões) e do isolamento do teste novo.

## Achados
- A1 (recomendado) skills/falar-com-o-dono/SKILL.md:20 · A description passou a listar "continue" como ordem ampla, mas o parágrafo da regra (linha 20) não; com a linha 18 mandando agir a cada "continue", incluir "continue" na lista da linha 20 deixa explícito que ele não confirma o novo nem o irreversível (R-DECISAO).
- A2 (recomendado) skills/falar-com-o-dono/SKILL.md:22 · "resolvido, feche ... sem delegar" pelo grep do cartão pode casar commit que só cita o cartão; dizer que resolvido é o item integrado na develop (pareceres da classe e CI) e que etapa de portão de branch não integrada nunca fecha assim (R-FLUXO).

## Sondas

## Detalhe dos achados
- A1: baixa, esforço P, dono o autor da skill (tech-lead revisa). Caminho: o dono escreve "continue" com uma pergunta irreversível pendente; o Jarvis lê a linha 18 (agir no mesmo turno) e a linha 20 sem "continue" e pode tratar a palavra como confirmação. Hoje o risco é contido porque a linha 18 inclui "pergunta" entre os passos válidos, a linha 24 (Q2) já exclui aceite de risco, gasto, `afrouxa-regra`, merge na main e ato destrutivo da escolha provisória, e a description já cita "continue". Correção mínima: na linha 20, `diante de "resolva", "acabe tudo", "continue" ou "pode fazer"`.
- A2: baixa, esforço P, mesmo dono. Caminho: um commit na develop menciona o cartão (por exemplo, um registro de achado) sem entregar o item; o Jarvis fecha a etapa sem delegar e um portão de review ou segurança deixa de rodar. A frase já exige conferir "o arquivo que ele cita" e a develop só recebe item com pareceres aprovados e CI verde, o que reduz o caminho a erro de leitura. Correção mínima: acrescentar "(integrado na develop com os pareceres da classe; etapa de portão de uma branch ainda não integrada não fecha por esta regra)".
- Conferido sem achado: a linha 18 não autoriza ato novo; os passos são "disparo, portão, registro ou pergunta", e a regra de ordem ampla segue intacta. O eval `EtapaJaResolvidaNaDevelop.develop_com` tira `GIT_*` herdados, isola `HOME`, usa `GIT_CONFIG_NOSYSTEM=1`, `sem_manutencao` e `git -C` na raiz temporária (AR-4 e AR-7 conferidos); o `@expectedFailure` documenta trava ainda inexistente, sem afrouxar teste existente. O `conferir()` herdado (A2 do review, AR-4/AR-5) é anterior ao diff. Nenhum invariante de `tests/config.json` tocado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem PR nem CI (integração do Jarvis); suíte inteira fica no CI do PR. Rodado na raiz do clone: `python3 -m unittest tests.test_jarvis_nucleo tests.evals.test_erros_por_papel` → `Ran 37 tests ... OK (expected failures=2)`. Varreduras de segredo e de workflow não se aplicam (só texto de skill e testes).
