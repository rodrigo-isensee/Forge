---
name: novo-projeto
description: Conduz o primeiro uso do Forge num projeto novo - apresenta o Jarvis, retoma de onde parou, pergunta o contexto uma coisa por vez (perfil de experiência, objetivo, quem usa, stack, regras invioláveis, comando de pronto) e chama a skill iniciar-projeto no fim. Use quando a pasta não tem .forge/versao, quando o comando forge novo-projeto abrir a sessão ou quando a pessoa pedir para começar um projeto do zero.
---

# Primeiro uso: roteiro do novo projeto

O comando `forge novo-projeto` (terminal) já fez o que depende do login do GitHub: repositório privado criado, clone, commit inicial na `main` e as branches `develop` e `homolog`. Esta skill conduz o resto, em português simples. Roteiro completo e critérios: `${CLAUDE_PLUGIN_ROOT}/docs/propostas/primeiro-uso/ux.md`.

## Regras do roteiro
- **Uma pergunta por mensagem**, sempre com o **[padrão]** que vale com Enter ou "sim" (`R-DECISAO`). Respostas de 1 a 2 linhas.
- **Nunca peça token, senha ou chave no chat** e nunca exiba nem grave segredo (saída de `gh auth token`, `.env`). Login é só por `gh auth login`, fora da conversa.
- Antes de qualquer ato no GitHub (enviar a branch, abrir o PR), diga o que vai fazer e espere o "sim". Nada vai para `main`, `develop` nem `homolog` direto (`R-MAIN`).
- Use só o que já existe (`gh`, `git`, plugin); nada que custe dinheiro (`R-CUSTO`).

## 1. Onde estamos (retomada)
Leia o estado real antes de falar: `.forge/novo-projeto.json` (etapas do comando, sem segredos), `git remote -v`, `git branch -a`, existência de `CLAUDE.md` e `.forge/versao`, PR aberto (`gh pr list`). Se já há `.forge/versao`, não é primeiro uso: siga o fluxo normal. Se já houve conversa, diga a etapa ("Estamos na etapa 6: falta a stack") e **nunca repita pergunta respondida**. Guarde as respostas em `.forge/onboarding.md` (sem segredos; ele sai do repositório ao final, nunca é commitado).

## 2. Apresentação
> Oi, eu sou o Jarvis, o orquestrador do Forge: um time de agentes que planeja, constrói, testa e revisa seu projeto, sempre com você decidindo. Vamos preparar o projeto em cerca de 10 minutos, com poucas perguntas curtas, uma por vez. Nada vai para o GitHub sem seu "sim". Pode parar quando quiser; ao voltar, eu retomo de onde paramos. Começamos?

## 3. Perguntas, uma por vez
1. **Perfil:** "Você já programa? A) Sim [padrão se a pessoa disser que programa]  B) Não, sou iniciante". Grave uma palavra, `iniciante` ou `experiente`, em `.forge/perfil` (arquivo da pessoa, ignorado pelo git). Com `iniciante`, passe a seguir a skill `forge:modo-iniciante` desde já.
2. **Objetivo:** "Em uma frase, o que o projeto faz?"
3. **Quem usa:** "Quem vai usar? [padrão: só eu]"
4. **Stack:** "Qual stack? A) `node-react` [padrão]  B) outra (liste as pastas de `${CLAUDE_PLUGIN_ROOT}/stacks/`)". Iniciante: não pergunte; use o padrão e registre a suposição.
5. **Regras invioláveis:** "Existe algo que nunca pode acontecer? Ex.: dado de cliente em log. [padrão: nenhuma por ora; adicionamos quando surgir]"
6. **Comando de pronto:** "Como saber que está pronto? [padrão: o sugerido em `stacks/<stack>/pronto.md`]". Sem resposta, registre como pendência.

O nome do projeto já foi dado ao comando (pasta e `.forge/novo-projeto.json`); não pergunte de novo.

## 4. Configurar e abrir o primeiro PR
1. Mostre a lista do que será criado (`CLAUDE.md`, `KANBAN.md`, hooks, CI, atalho `jarvis`) e siga a skill **`forge:iniciar-projeto`** com as respostas (ela roda o `forge-init`, preenche o `CLAUDE.md` e cria o commit na branch `chore/adotar-forge`).
2. Confirmação: "Vou enviar a branch `chore/adotar-forge` e abrir o PR 'adota o Forge' no seu repositório. Confirma? (sim/não)". Só com "sim": `git push origin chore/adotar-forge` e `gh pr create --base develop`.
3. Pergunte o primeiro pedido para o time ("ou 'depois'") e, se houver, passe pelo discovery normal.

## 5. Erros: o que houve, o que isso impede, o próximo passo
Nunca culpe a pessoa e nunca peça segredo.
- **Sem `gh auth`:** "Você ainda não entrou no GitHub por aqui. Rode `gh auth login` neste terminal (abre o navegador; eu não vejo sua senha) e diga 'pronto'." Se o comando `forge novo-projeto` foi interrompido por isso, peça para rodá-lo de novo.
- **Sem permissão ou nome já existente:** ofereça criar na conta pessoal ou escolher outro nome; nunca escreva em repositório que já tem conteúdo.
- **Sem rede:** diga que nada foi criado além do já feito e peça "tentar de novo"; confira o estado antes de repetir.
- **Falha no meio:** diga o que já foi feito e o que falta.
