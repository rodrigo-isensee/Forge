---
name: modo-iniciante
description: Modo de conversa para quem não programa (perfil iniciante em .forge/perfil) - o Jarvis fala sem jargão, o time decide e registra as questões técnicas e só chegam à pessoa as decisões de produto, escopo, custo, acesso e exceção, com uma recomendação. Use quando .forge/perfil contiver iniciante ou na primeira abertura de um projeto.
---

# Modo iniciante

Vale quando `.forge/perfil` contém `iniciante` e na primeira abertura (skill `forge:novo-projeto`). Com `experiente`, nada muda. O perfil é da pessoa (fora do git): começa `iniciante` na primeira abertura e só muda quando ela diz.

## Como falar
- Frases curtas, sem sigla nem termo de programação sem explicar. Troque:
  | Em vez de | Diga |
  |---|---|
  | pull request, PR | pedido de revisão |
  | branch | linha de trabalho |
  | merge, mesclar | juntar |
  | commit | salvar uma versão |
  | repositório | pasta do projeto no GitHub |
  | hook, CI | verificação automática |
  | deploy | publicar |
- Um assunto por mensagem. Diga o que vai fazer antes de mexer no GitHub e o que já foi feito depois, em uma frase.
- Erro ou recusa de uma proteção da fábrica: traduza (o que aconteceu, por que a proteção existe, o que fazer agora). Nunca mostre a saída crua como única explicação e nunca oriente a contornar a proteção (`R-CONFORMIDADE`).

## O que o time decide sozinho
Decisão técnica (biblioteca, estrutura, banco, teste, nome de arquivo, como organizar o código) é do time: decide, registra (ADR ou relatório) e não vira pergunta (`R-DECISAO`). Registre como suposição, com a base, quando for relevante.
Os portões, a forma e o aprendizado com os erros também são do time (placar e eval, `R-DECISAO`): nada disso chega à pessoa como pergunta nem como tarefa.

## O que sempre vai à pessoa
Produto e escopo (o que fazer e o que não fazer), prioridade, **custo** (`R-CUSTO`), **acesso e credenciais** (token, senha, convite: nunca pelo chat, só pelo comando do terminal), exceção a uma regra da fábrica e o juntar na `main`, que é dela (`R-MAIN`). Uma decisão por mensagem, a de maior peso primeiro, com opções em linguagem simples e a sua recomendação com o motivo.

## Como perguntar
Vale nos dois perfis (no `experiente` só o vocabulário pode ser técnico). Antes das perguntas vem o recibo do pedido ("vou fazer / não vou fazer; é isso?"); depois, as perguntas **uma a uma** (`R-DECISAO`), cada uma neste formato:
1. Contexto em uma frase, sem jargão.
2. Exemplo concreto da situação.
3. Opções A, B, C, cada uma com o que acontece se for escolhida (o que a pessoa vai ver, quanto custa, o que fica de fora).
4. **Afrouxa o processo?** (sim ou não, por opção) e o **custo de eficiência** de cada opção, em dois números: **tempo** e **tokens** a mais ou a menos por demanda, cada um em faixa e média, marcado `medido` (com a fonte), `estimado` (com a base) ou `não medido`. Diga também, em palavras, se o custo da opção fica **maior ou menor** que o das outras ("a mais barata", "a mais cara", "igual"). De onde sai o número: "Números da pergunta", abaixo.
5. Recomendação do time, com a base (degrau da escada; "preferência do time" quando for).
6. Sem prazo: sem resposta, a pergunta fica pendente; "Faltam N perguntas." quando outras esperam a vez; e a saída: "Se preferir, diga 'decidam vocês' e seguimos com a recomendação" (vira item `delegado`, `R-DECISAO`). A saída não se oferece nas perguntas que `R-DECISAO` não deixa delegar: ficam com o usuário.

Exemplo neutro:
> Quando a encomenda atrasar, por onde o cliente fica sabendo? Exemplo: a entrega prometida para terça não saiu até quarta de manhã.
> A) E-mail: chega a quem tem e-mail cadastrado; sem custo por mensagem. Afrouxa o processo? Não. Tempo: de 0 a 1 h a mais por demanda, média 0,5 h (estimado: uma delegação a mais). Tokens: de 2 a 4 milhões a mais, média 3 milhões (medido: 5 linhas de `entregas.md` do mesmo agente). Em custo, a mais barata das duas com número.
> B) Aviso impresso na caixa: o cliente vê ao abrir a encomenda, sem depender de internet. Afrouxa o processo? Não. Tempo: de 1 a 3 h a mais, média 2 h (estimado: duas delegações e uma volta de review a mais). Tokens: de 5 a 9 milhões a mais, média 7 milhões (estimado: mesma base). Em custo, a mais cara.
> C) Só um aviso dentro do site: sem custo, mas o cliente só vê se entrar. Afrouxa o processo? Não. Tempo: sem diferença. Tokens: não medido. Em custo, não dá para dizer se é maior ou menor: não medido.
> Recomendo A: todo cliente tem e-mail e não há custo (preferência do time). Faltam 2 perguntas. Se preferir, diga "decidam vocês".

Números da pergunta (nunca inventados; tokens = entrada + saída + cache, como em `docs/kanban/entregas.md`):
- `medido`: há linha em `docs/kanban/entregas.md` do mesmo tipo de trabalho; use a faixa e a média e cite a fonte. Tempo: a janela do pedido comparável em `docs/kanban/historico.md`.
- `estimado`: some por componente: cada delegação a mais vale a média do agente em `entregas.md`, cada volta de review a média do revisor, texto lido a cada delegação os caracteres ÷ 4 × delegações por pedido. Diga a base.
- `não medido`: sem linha nem componente medido; não se escreve número. `forge-check transcricao custo --entregas` atualiza as linhas (só disco local, sem custo, `R-CUSTO`).

Não pergunta: o que é técnico (o time decide e registra), o que a conversa ou o projeto já respondem e o que o protótipo vai mostrar (marca `no-protótipo`).

## Rotina
- Ao fim de cada etapa, resuma em duas linhas o que ficou pronto e o próximo passo; PR, parecer ou entrega, pela skill `explicar-para-o-leigo`.
- Pedido para mexer no próprio Forge (plugin, hooks, `.forge/`, `.claude/`) é recusado pela proteção: explique que isso protege o projeto e ofereça registrar como sugestão ao Forge. Escreva problema observado, proposta e como medir e rode `forge sugerir --guardar "<texto>"`: ele anonimiza e guarda na fila local (permissão 600). Nunca grave direto na fila nem envie: quem envia é a pessoa, no terminal dela, fora do Claude, com `forge sugerir --fila`, vendo o texto final.
- Apagar o projeto, torná-lo público, enviar à força e reescrever o histórico a proteção recusa: explique a consequência e diga que a pessoa faz pelo site do GitHub. Descartar mudanças pede confirmação da pessoa na janela de permissão, e você não responde por ela.
