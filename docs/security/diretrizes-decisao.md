---
tipo: revisao-seguranca
contrato: 1
pedido: diretrizes-decisao
branch: melhoria/diretrizes-decisao
commit: 3a86bd3853ad610cbbfa72593b9d29a79d853aca
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: diretrizes-decisao (v046 E26.14)

Revisado: `git diff c340c322..3a86bd38` (R-DECISAO.md, falar-com-o-dono/SKILL.md, fragmento de changelog). Só texto; sem código, workflow nem segredo.

## Gatilhos
`R-SEGURANCA`: regra de decisão do dono e controle de escopo e aceite (texto protegido por invariantes de `tests/config.json`). Sem gatilho de código ou pipeline.

## Achados
- A1 (bloqueante) docs/regras/R-DECISAO.md:11 · Os cortes removeram 6 trechos de `invariantes` (tests/config.json): 5 em R-DECISAO.md e 1 na skill falar-com-o-dono; `RegrasInviolaveis.test_trechos_obrigatorios` falha com 6 subtestes (reproduzido no head).
- A2 (recomendado) docs/regras/R-DECISAO.md:16 · O corte tirou "(não amplia autorização)" da fala gravada; o código ainda o afirma (bin/forge_dono.py:358). Mantenha uma frase curta para o limite não depender só do código.

## Sondas
- S1 · python3 -m unittest tests.test_forge.RegrasInviolaveis.test_trechos_obrigatorios (worktree no head 3a86bd38) · espera: OK, sem trecho invariante ausente · obtido: FAILED (failures=6)

## Detalhe dos achados
A1. Evidência (trechos ausentes no head): R-DECISAO.md: `na entrega, \`pendente:\`` (item "Corte de escopo é explícito"), `a próxima espera a resposta` (item "Uma por vez"), `origem: <coluna>; ação: <o que o usuário faz>; comando:`, `um comando, um efeito` e `evidência no motivo` (painel "Aguardando o dono"). skills/falar-com-o-dono/SKILL.md: `Sem resposta, fica pendente\.`. Nenhuma regra com ID sumiu (R-DECISAO, R-CUSTO e R-CONFORMIDADE seguem citadas); os demais trechos de invariantes dos dois arquivos seguem presentes. O diff não toca tests/config.json, então o CI do PR quebra; afrouxar invariante exige destaque no título do PR (CLAUDE.md), então a saída é restaurar os trechos, não editar a lista.
Caminho de ataque: sem o texto, o controle que reprova corte sem marca na entrega (`pendente:`) e a regra de que sem resposta o item fica pendente perdem o amparo escrito; um agente poderia omitir a entrega de um item sem o gatilho de review. Severidade: média (regra protegida por teste, sem exploração direta). Correção mínima: restaurar literalmente as 6 expressões acima; cada uma tem poucas palavras e o corte pode vir de outras frases não protegidas. Esforço: P. Dono: tech-lead.
A2. Severidade baixa; esforço P; dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As diretrizes 1, 8 e 9 (custo em tokens e ganho por opção, origem do item, conferência de decisão ruim, também a do dono) não afrouxam controle: o texto manda levar ao dono, e a escolha provisória segue vetada para aceite de risco, custo, rótulo, merge na main e ato destrutivo. Suíte inteira: só no CI (sem PR aberto agora); rodado só o teste de invariantes. Sem lacuna de ferramenta (revisão de texto).
