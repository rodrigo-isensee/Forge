---
name: checagem-do-brief
description: Lista do que o forge-check brief não confere num brief, mais a lista local opcional do projeto (docs/engineering/brief-checklist.md). Use em todo brief, antes de rodar forge-check brief mensagem e mandar o brief ao conferente.
---

# Checagem do brief antes de enviar

O `forge-check brief` confere forma, corte, decisões cobradas e citações. Esta skill cobre o que ele não sabe: o estado do mundo fora do texto e as regras locais do projeto. Ela só **acrescenta** checagens ao brief (`R-BRIEF`).

## Quando usar
Em todo brief, depois de montá-lo (`forge-check brief gerar`) e de vê-lo passar no `forge-check brief <arquivo>`, e antes de `forge-check brief mensagem`. Na rodada de confirmação, confira de novo só os itens que o texto alterado alcança.

## Lista neutra (vale para todo projeto)
Para cada item, ou o brief já o resolve, ou você o corrige antes de enviar:
- **Estado do remoto citado:** branch, PR, tag ou sha que o brief cita existe agora no remoto e é o que o brief diz (leia com `git ls-remote` ou `gh`, não de memória); o `Base-sha` é o da base atual.
- **Comando que precisa de rede ou de credencial:** o brief diz qual, e a credencial do agente tem o escopo que o comando pede; sem ele, o passo vira ato do dono no brief, não tentativa do agente.
- **Efeito fora da worktree:** escrita em outra pasta, no remoto, no quadro ou na configuração aparece no Entregar com o caminho literal; o que o brief não nomeia, o agente não faz.
- **Arquivo temporário e log:** levam o pedido ou o slug da branch no nome, numa pasta por papel e pedido, nunca um nome genérico.
- **Etapa de outro agente que depende desta:** o Entregar deixa pronto o que a etapa seguinte lê (commit, parecer, caminho), e a ordem entre etapas paralelas está escrita.
- **Gatilho de outra etapa:** se o Entregar toca o que dispara segurança, devops ou rótulo do dono, a etapa correspondente já está no pedido.
- **Pontos da decisão do dono:** cada ponto da opção escolhida tem um item no Entregar.

## Lista local do projeto
Se existir `docs/engineering/brief-checklist.md` no projeto, confira cada item dele cujo `quando:` casa com o tipo do brief. Sem o arquivo, a lista neutra basta: ele é opcional e nenhum projeto precisa criá-lo. O modelo vazio fica em `templates/projeto/docs/engineering/brief-checklist.md`.

Limite da lista local: ela só acrescenta. Um item dela nunca dispensa conferente, review, QA, segurança nem rótulo do dono, nem afrouxa uma regra de `docs/regras/`; item que pretenda isso não se aplica e vira pergunta ao dono (`R-DECISAO`).

## Manutenção
Item que o `forge-check` passar a cobrir sai da lista (desta skill ou da local) no mesmo PR que dá a cobertura. Item novo entra quando uma omissão no brief se repete; cite o cartão de origem na linha.
