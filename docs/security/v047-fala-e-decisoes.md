---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-fala-e-decisoes
commit: 05797223ac8b884b8d44874803878cfb356eedbc
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (fala só no marco e pedido das decisões)

Intervalo revisado: `origin/develop` (c5c3a449) até 05797223, um commit (E1.282): `agents/jarvis.md`, `skills/falar-com-o-dono/SKILL.md`, `skills/modo-iniciante/SKILL.md`, `tests/config.json` e o fragmento `changelog.d/v047-fala-e-decisoes.md`.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `tests/config.json` (invariantes). Os demais arquivos são texto de agente e skill, sem autenticação, segredo, dependência, CI, hook nem `docs/regras/`.

**Invariantes:** o diff só acrescenta. As três linhas removidas de `tests/config.json` voltam idênticas no mesmo lugar (a lista de `skills/modo-iniciante/SKILL.md` vira superconjunto; nas listas de `agents/jarvis.md` e `skills/falar-com-o-dono/SKILL.md` só muda a vírgula). São 15 padrões novos, todos com `regra` e `porque` (R-DECISAO). Nenhuma proteção foi afrouxada, e o pedido não precisa do rótulo `afrouxa-regra`.

**Texto removido, conferido contra a fonte:**
- `agents/jarvis.md`: a lista "à pessoa, só decisão, rótulo, merge na `main` e comando em arquivo travado" saiu da regra do dono, mas está inteira na linha nova "Falar só no marco". A frase "quando algo dá errado e muda prazo ou risco" e as decisões (o que inclui o aceite de risco de `R-SEGURANCA`) continuam saindo na hora, fora do resumo de 30 min. Recibo e perguntas seguem completos (invariante novo). "Telegram ... sem segredo; não mude a allowlist" não mudou.
- `skills/falar-com-o-dono/SKILL.md`: saíram a menção a `decisoes --resposta` e os campos do corte recomendado (`origem:`, `procurado:`, `seguir:`, `não seguir:`). Quem os exige é a ferramenta (`bin/forge_dono.py`), que não muda. "Uma decisão por mensagem" e a origem de cada decisão continuam na fonte (`docs/regras/R-DECISAO.md:14`). A trava da Q2 (a escolha provisória não cobre aceite de risco, gasto, `afrouxa-regra`, merge na main nem ato destrutivo) não mudou, e o pedido das decisões grava cada resposta por `forge-check anotar`.
- `skills/modo-iniciante/SKILL.md`: a tradução de recusa sem orientar contorno (`R-CONFORMIDADE`), a fila do `forge sugerir` e a confirmação na janela de permissão não mudaram.

Neutralidade (`R-NEUTRO`): a extensão citada é um editor genérico, não um projeto. O teste de neutralidade passa (abaixo).

## Achados
- A1 (recomendado) skills/modo-iniciante/SKILL.md:55 · O modo foco recolhe comandos e agentes. Diga ao iniciante que a janela de permissão continua aparecendo e que ele pode abrir a linha para ver o comando antes de aprovar, para que o foco não vire aprovação sem leitura.
- A2 (recomendado) skills/modo-iniciante/SKILL.md:21 · Saiu o aviso "o que já foi feito depois" de um ato no GitHub. Um ato visível fora (comentário, issue, rótulo) que não fecha marco fica sem registro à pessoa. Mantenha uma frase depois de um ato externo no GitHub, ou registre que o marco o cobre.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `skills/modo-iniciante/SKILL.md:55`. Caminho: um texto injetado (de uma issue ou de um arquivo lido) leva um agente a propor um comando. O sistema de permissões ainda pede confirmação, mas o iniciante, com a visão recolhida, tende a aprovar sem abrir o comando. A barreira técnica (permissão e hook `conformidade`) não muda, por isso não bloqueia. Severidade: baixa. Correção mínima: meia frase na mesma linha. Esforço: P. Dono: o autor do pedido.

**A2.** Evidência: `skills/modo-iniciante/SKILL.md:21`, antes "e o que já foi feito depois, em uma frase". Caminho: não há atacante. O risco é de auditoria: um ato público feito em nome do dono não chega a ele até o próximo marco ou resumo. Severidade: informativa. Correção mínima: devolver o aviso só para o ato externo no GitHub, ou dizer explicitamente que o resumo de 30 min o cobre. Esforço: P. Dono: o autor do pedido.

## Riscos aceitos e ferramentas
Sem riscos aceitos.

Conferido no head 05797223:
- Os padrões de `invariantes` dos três arquivos casam com o texto (script local, sem falta).
- `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.NeutralidadeDoNucleo`: OK (6 testes).
- `tests.test_forge.RegrasInviolaveis`: OK (3 testes).

A branch ainda não tem PR nem execução de CI. A suíte inteira roda no CI do PR e é obrigatória para o merge (`R-QA`).

Ferramentas de varredura de segredo, de dependência e de workflow: não se aplicam, porque o diff é só texto e configuração de teste, sem segredo, dependência nem workflow.
