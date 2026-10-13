# Primeiro uso do Forge: roteiro da conversa

Origem: `decisoes.md` (etapas, D1, D2). Interface: conversa com o Jarvis no terminal, em português. Itens marcados (H) são hipóteses até o dono validar.

## 1. Persona e objetivo
- **Persona:** pessoa que programa ou toca um produto, tem Claude Code e conta GitHub, e **nunca ouviu falar do Forge** (hoje: o dono, D1). Não conhece "develop/homolog", "hook" nem "PR de adoção".
- **Objetivo:** do `forge novo-projeto` ao primeiro PR "adota o Forge" aberto, e o primeiro pedido feito, sem ler documentação.
- **Princípio:** o Jarvis faz o que é técnico sozinho, pergunta só o que só a pessoa sabe, e diz o que vai fazer antes de tudo que mexe no GitHub.

## 2. Apresentação (primeira mensagem, sem `.forge/versao` na pasta)
> Oi, eu sou o Jarvis, o orquestrador do Forge: um time de agentes que planeja, constrói, testa e revisa seu projeto, sempre com você decidindo.
> Vamos preparar o projeto em cerca de 10 minutos (H): ~8 perguntas curtas, uma por vez. Eu crio o repositório privado, configuro tudo e abro um PR para você revisar. Nada vai para o GitHub sem seu "sim".
> Pode parar quando quiser; ao voltar, eu retomo de onde paramos. Começamos?

## 3. Roteiro
Regra geral: uma pergunta por vez (R-DECISAO), sempre com **[padrão]** que vale com Enter ou "sim". Respostas longas ficam em 1 a 2 linhas.

| # | Passo | Pergunta exata | Jarvis faz sozinho |
|---|---|---|---|
| 0 | Verificação | (sem pergunta) | Checa `git`, `gh`, `claude`, plugin `forge`; mostra um resumo "tudo certo" ou o primeiro item faltando |
| 1 | Nome | "Qual o nome do projeto? [padrão: nome da pasta, ex.: `meu-app`]" | Normaliza para minúsculas com hífen |
| 2 | Repositório | "Quer que eu crie o repositório no GitHub, privado, na sua conta `<login>`? A) Sim, criar `<login>/<nome>` [padrão]  B) Já tenho um vazio: me passe a URL" | `gh api user` para o login; ver 3.2 |
| 3 | Confirmação 1 | "Vou criar `<login>/<nome>` como **privado**. Confirma? (sim/não)" | `gh repo create --private --clone`; cria `develop` e `homolog` |
| 4 | Objetivo | "Em uma frase, o que o projeto faz?" | Rascunha o resumo para o `CLAUDE.md` |
| 5 | Quem usa | "Quem vai usar? [padrão: só eu]" | |
| 6 | Stack | "Qual stack? A) node-react [padrão]  B) outra (lista das disponíveis)" | Lista `stacks/` do plugin |
| 7 | Regras invioláveis | "Existe algo que nunca pode acontecer? Ex.: dado de cliente em log. [padrão: nenhuma por ora; adicionamos depois]" | |
| 8 | Comando de pronto | "Como saber que está pronto? [padrão: `<comando da stack>`]" | Registra pendência se a pessoa não souber |
| 9 | Configuração | (sem pergunta; mostra a lista do que vai criar: `CLAUDE.md`, `KANBAN.md`, hooks, CI, atalho `jarvis`) | `forge-init`, Jarvis como agente principal, atalho; commit em `chore/adotar-forge` |
| 10 | Confirmação 2 | "Vou enviar a branch `chore/adotar-forge` e abrir o PR 'adota o Forge' no seu repositório. Confirma? (sim/não)" | `git push`, `gh pr create` |
| 11 | Primeiro pedido | "Pronto! O PR está em `<url>`. Qual o primeiro pedido para o time? (ou 'depois')" | Passa o pedido pelo discovery |

Total: 8 perguntas de contexto/escolha (passos 1, 2, 4 a 8, 11) mais 2 confirmações = **10 interações**.

### 3.1 Confirmações (atos irreversíveis)
- Só duas: criar repositório (passo 3) e enviar commits/abrir PR (passo 10). A confirmação nomeia o que será afetado: conta, nome, visibilidade, branch.
- Resposta diferente de "sim" não executa. "não" no passo 3 volta ao passo 2.
- Se a pessoa escolher repositório **público**, o Jarvis pergunta separadamente: "Isso deixa o código visível para qualquer pessoa. Confirma público?" Padrão é privado.

### 3.2 Erros e como seguir
Formato: o que aconteceu, o que isso impede, o próximo passo (comando ou ação). Nunca culpar a pessoa.
- **Sem `gh` instalado:** "Não encontrei o GitHub CLI (`gh`). Ele é como eu falo com o GitHub. Instale pelo link `<oficial>` e diga 'pronto'."
- **Sem `gh auth`:** "Você ainda não entrou no GitHub por aqui. Rode `gh auth login` neste terminal (abre o navegador); o login acontece lá, eu não vejo sua senha. Diga 'pronto' ao terminar."
- **Sem permissão** (conta/organização não deixa criar): "O GitHub negou a criação em `<dono>`. Opções: A) criar na sua conta pessoal [recomendado]  B) pedir permissão à organização e tentar depois  C) criar vazio no site e me passar a URL."
- **Nome já existe:** "`<login>/<nome>` já existe. A) usar o existente se estiver vazio (verifico para você)  B) escolher outro nome [recomendado, sugiro `<nome>-2`]." Nunca escrever sobre repositório com conteúdo sem pedir.
- **Sem rede:** "Não consegui falar com o GitHub (sem conexão). Nada foi criado ainda. Verifique a rede e diga 'tentar de novo'." Operações são repetíveis: o Jarvis confere o estado antes de repetir.
- **Identidade do git ausente:** pergunta nome e e-mail (dados públicos de commit, não segredo) e configura só neste repositório.
- **Falha no meio de uma etapa:** diz exatamente o que já foi feito e o que falta.

### 3.3 Retomar
- O Jarvis **lê o estado real** ao abrir: remoto configurado? branches `develop`/`homolog`? `CLAUDE.md`? `.forge/versao`? PR aberto? Respostas já dadas ficam em `.forge/onboarding.md` (sem segredos; sai do repositório ao final).
- Mensagem: "Estamos na etapa 6 de 11: repositório criado, falta a stack. Continuo daí?" Nunca refaz o que já existe e nunca repete pergunta respondida.
- Pasta com `.forge/versao`: não é primeiro uso; o Jarvis segue o fluxo normal.

## 4. O que nunca fazer
- Pedir token, senha ou chave no chat; autenticação só por `gh auth login` fora da conversa.
- Exibir ou gravar segredos (saída de `gh auth token`, `.env`) em tela, `CLAUDE.md`, log ou commit.
- Criar repositório público sem pergunta explícita; criar fora da conta da pessoa.
- Escrever em repositório existente com conteúdo; enviar para `main`, `develop` ou `homolog` direto (R-MAIN).
- Fazer duas perguntas na mesma mensagem (R-DECISAO); usar nomes fixos da conta do dono (D2).
- Gastar dinheiro ou usar serviço pago (R-CUSTO).

## 5. Critérios de pronto da experiência
- `CA-1` QUANDO a pessoa roda `forge novo-projeto` numa pasta sem `.forge/versao` O SISTEMA DEVE exibir a apresentação com o tempo estimado antes de qualquer pergunta.
- `CA-2` O SISTEMA DEVE chegar ao PR "adota o Forge" aberto em até 15 minutos, com respostas sem demora e rede normal (H; medir no teste real).
- `CA-3` O SISTEMA DEVE fazer no máximo 10 interações do passo 1 ao 11, cada mensagem com uma única pergunta.
- `CA-4` QUANDO a pessoa responde só "sim"/Enter a todas as perguntas O SISTEMA DEVE concluir com os padrões, sem pedir informação extra.
- `CA-5` ANTES de criar o repositório e de enviar commits O SISTEMA DEVE exibir uma confirmação com conta, nome, visibilidade e branch, e só agir após "sim".
- `CA-6` O repositório criado DEVE ser privado, salvo confirmação explícita em contrário.
- `CA-7` SE ocorrer um dos erros de 3.2 ENTÃO O SISTEMA DEVE dizer o que houve e oferecer o próximo passo, sem pedir segredo.
- `CA-8` QUANDO a sessão é reaberta no meio do roteiro O SISTEMA DEVE informar a etapa atual e continuar sem repetir pergunta respondida.
- `CA-9` Nenhum texto exibido ou arquivo gravado DEVE conter token ou senha.
- `CA-10` O fluxo DEVE usar só o que já existe (`gh`, `git`, plugin), sem serviço pago.

## 6. Perguntas ao dono
**Q1. Onde a pessoa responde sobre "regras invioláveis" (passo 7)?** Hoje é pergunta aberta e abstrata, o ponto mais provável de travar quem é novo.
- A) Manter, com padrão "nenhuma por ora" [recomendado: tira o atrito e a regra entra depois, quando surgir; o Jarvis lembra no primeiro PR de feature].
- B) Oferecer 3 exemplos comuns para escolher (segredos, dados pessoais, produção): mais guiado, porém mais longo.

**Q2. Quando validar o tempo (CA-2) e o roteiro?**
- A) Você roda o roteiro num projeto de teste, em pasta nova, cronometrando [recomendado: único jeito de trocar as hipóteses H por medida].
- B) Só ao primeiro usuário externo: adia o feedback, e D1 mantém só você.
