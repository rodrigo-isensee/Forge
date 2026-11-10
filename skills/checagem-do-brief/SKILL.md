---
name: checagem-do-brief
description: Lista do que o forge-check brief selar não confere num brief, mais a lista local opcional do projeto (docs/engineering/brief-checklist.md). Use em todo brief, antes de selá-lo.
---

# Checagem do brief antes de selar

O `forge-check brief selar` confere a forma, o corte, as etapas, as decisões por referência e as citações (`R-BRIEF`). Esta skill cobre o que ele não sabe: o estado do mundo fora do texto e as regras locais do projeto. Ela só **acrescenta** checagens.

## Lista neutra (vale para todo projeto)
- **Estado do remoto citado:** branch, PR, tag ou sha que o brief cita existe agora e é o que o brief diz (leia com `git ls-remote` ou `gh`, não de memória).
- **Rede ou credencial:** o brief diz qual comando precisa delas, e o agente tem o escopo; sem ele, o passo é ato do dono.
- **Efeito fora da worktree:** escrita em outra pasta, no remoto, no quadro ou na configuração aparece no Entregar com o caminho literal.
- **Arquivo temporário e log:** levam o pedido ou o slug da branch no nome, numa pasta por papel e pedido (`${TMPDIR:-/tmp}/<papel>-<pedido>/`; o `:-/tmp` vale quando o ambiente do agente não define `TMPDIR`).
- **Etapa seguinte:** o Entregar deixa pronto o que ela lê (commit, parecer, caminho).
- **Gatilho de outra etapa:** se o Entregar toca o que dispara segurança, devops ou rótulo do dono, a etapa já está no pedido.
- **Pontos da decisão do dono:** cada ponto da opção escolhida tem um item no Entregar.

## Lista local do projeto
Se existir `docs/engineering/brief-checklist.md` no projeto, confira cada item cujo `quando:` casa com o tipo do brief. Ele é opcional; o modelo vazio fica em `templates/projeto/docs/engineering/brief-checklist.md`. Um item local nunca dispensa portão, review, QA, segurança nem rótulo do dono, nem afrouxa uma regra; o que pretenda isso vira pergunta ao dono (`R-DECISAO`).

## Manutenção
Item que a ferramenta passar a cobrir sai desta lista no mesmo PR. Item novo entra só quando uma omissão se repete, com a medida (`R-DECISAO`).
