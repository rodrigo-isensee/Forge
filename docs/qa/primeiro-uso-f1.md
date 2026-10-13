---
tipo: qa
contrato: 1
pedido: primeiro-uso-f1
branch: melhoria/primeiro-uso
commit: 38571c0
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 4
bugs_baixos: 5
aceite_usuario: sim
data: 2026-10-13
---

# QA - primeiro uso do Forge, entrega F1 (`forge novo-projeto`)

Testado no checkout do HEAD do PR #96 (38571c0), em worktree temporária. Rede real e conta real do GitHub não foram usadas: `gh` e `claude` falsos (os de `tests/test_novo_projeto.py`), HOME temporário, variáveis `GH_*`/`GITHUB_*` removidas do ambiente.

Nota de honestidade: no primeiro exploratório de "sem gh" o PATH ainda enxergava o `gh` real da máquina, que respondeu só a `gh auth status` e `gh api user` (leitura, sem criar nada; o script parou na pergunta da pasta). Repeti o caso com um PATH sem `gh` e o resultado vale o da repetição.

## Resultado da suíte
`python3 -m unittest discover -s tests`: 302 testes, OK, 153 s. Nenhum `skip`.

## Matriz critério -> teste -> resultado
Escopo da F1: o comando de terminal (`bin/forge`, `bin/forge-novo-projeto`) e as skills; a conversa com o Jarvis é texto de skill, sem teste de comportamento automatizável.

| CA | Cobertura automatizada | Exploratório | Resultado |
|---|---|---|---|
| CA-1 apresentação com tempo antes de qualquer pergunta | nenhuma (teste só confere que a skill existe) | o comando imprime uma linha e já pergunta o nome; a apresentação com "10 minutos" só vem na skill, depois do repositório criado | **Parcial** (BUG-02) |
| CA-2 PR em até 15 min | não aplicável (H, medir no teste real; PR "adota o Forge" é da F1 só na skill) | não medido | Pendente (Q2 do UX) |
| CA-3 até 10 interações | nenhuma | contagem: terminal 3 (nome, pasta, confirma) + skill 8 (perfil, objetivo, quem usa, stack, regras, pronto, confirmação do PR, primeiro pedido) = 11 (iniciante: 10, sem stack) | **Parcial** (BUG-03) |
| CA-4 só "sim"/Enter conclui com os padrões | nenhuma | Enter no nome trava (sem padrão); Enter na confirmação recusa (`[s/N]`, seguro e coerente com CA-5) | **Falha** (BUG-02) |
| CA-5 confirmação antes de criar | `test_recusa_na_confirmacao...`, `test_aceite_na_confirmacao...`, `test_sim_cria_sem_perguntar` | "sim", "s", "SIM" criam; "Sim.", "yes", "n" e Enter não criam | Ok para o repositório; a do PR é da skill (sem teste) |
| CA-6 privado | `test_caminho_feliz` (`--private`), `test_retomada_recusa_repositorio_de_fora_publico` | idem | Ok |
| CA-7 erro: o que houve + próximo passo, sem segredo | `test_sem_gh_auth...`, `test_nome_existente...`, `test_nome_invalido...`, `test_retomada_recusa_...`, `test_nome_ou_email...`, `test_conta_diferente...` | sem gh, sem rede e sem permissão ver abaixo | **Parcial** (BUG-01, BUG-04, BUG-08) |
| CA-8 retomar informando a etapa | `test_retomada_depois_de_parar_no_meio`, `test_rodar_de_novo...`, `test_conta_diferente...` | retomada diz "já feito: ['repo_criado']", não "etapa X de Y"; nunca repete o que existe | Ok no comportamento; texto ruim (BUG-06) |
| CA-9 sem token/senha | `test_caminho_feliz` (sem `auth token`), `test_estado_de_retomada_nao_guarda_segredo` | `gh.log` e estados sem segredo; o script nunca pede senha | Ok |
| CA-10 só o que já existe | `test_caminho_feliz` (só `gh`, `git`, `claude`) | idem | Ok |

## Exploratórios (todos com `gh`/`claude` falsos)
| Cenário | Observado | Avaliação |
|---|---|---|
| Sem `gh` | "não encontrei 'gh'. Instale e rode de novo." | Sai limpo, nada criado. Não explica o que é `gh`, não dá link (BUG-06) |
| `gh` sem login | mensagem manda rodar `gh auth login`, nada criado | Ok (coberto) |
| Confirmação recusada | para, nada criado, diz como voltar | Ok |
| Confirmação aceita | cria uma vez, privado | Ok |
| Nome existente: público com conteúdo, vazio, privado | todos recusados na pergunta do nome, sugerem `<nome>-2`, nada escrito no existente | Seguro. Desvio do UX 3.2: lá "usar o existente se estiver vazio" é opção; aqui só na retomada (BUG-09 baixo) |
| Parar no meio e retomar (falha do clone) | retoma sem recriar, `repo create` uma vez | Ok; pede o nome de novo (ok), mostra lista crua (BUG-06) |
| Pasta apagada depois de concluir e rodar de novo | erro cru do git (`fatal: cannot change to`) e pergunta o nome do commit | BUG-07 |
| Conta trocada | recusa e cita as duas contas | Ok |
| Nome com acento ou espaço | recusado com a regra dita, sem sugerir o nome corrigido; `MeuApp` aceito sem normalizar | BUG-05 |
| Sem rede (`gh api user` falha) | **sai sem mensagem em português**, só o erro cru do `gh` | BUG-01 |
| Sem rede (`gh auth status` falha) | mensagem "você ainda não entrou no GitHub" (culpa o login) | Inferido do `gh` falso; não verificado com `gh` real (BUG-08) |
| Sem permissão (HTTP 403 no `repo create`) | "o GitHub não criou ... rode de novo" | Sem opções; rodar de novo repete a falha (BUG-04) |
| Pasta existente e cheia | recusa antes de criar o repositório | Ok |

## Mensagens: português claro para quem não programa
Pontos bons: frases curtas, sem culpar a pessoa, dizem que o login acontece no navegador e que o script não vê a senha, avisam que nada foi criado quando é o caso.
Ainda com jargão (BUG-06): "main, develop e homolog" na mensagem final; "commit inicial", "enviar a main", "clonar" nas falhas; "Seu nome para os commits"; `gh` sem explicação; `[s/N]` sem "sim/não" por extenso; lista Python crua `['repo_criado', 'clonado']` na retomada; "(use --sim ...)" é de teste. Os prompts vão para stderr e saem sem quebra de linha antes da mensagem seguinte ("Qual o nome do projeto? Nome inválido: ...").

## Bugs
Todos para o agente de desenvolvimento da fábrica (dono de `bin/`). Nenhum crítico nem alto.

### BUG-01 - média - sem rede em `gh api user` encerra sem mensagem em português
Passos: `gh` cuja `api user` falha (`error connecting to api.github.com`, exit 1); `forge novo-projeto`.
Esperado (UX 3.2, CA-7): "Não consegui falar com o GitHub (sem conexão). Nada foi criado ainda. Verifique a rede e tente de novo."
Obtido: só `error connecting to api.github.com`, exit 1. Causa: `dono="$(gh api user --jq .login)"` com `set -e` encerra antes do `die` da linha seguinte. Correção: `dono="$(...)" || die "..."`.

### BUG-02 - média - Enter no nome não usa padrão (CA-4); nome não é normalizado
Passos: `forge novo-projeto` e Enter em tudo.
Esperado (UX passo 1): "[padrão: nome da pasta]" e Enter vale. Obtido: "Nome inválido" em loop até acabar a entrada. A pessoa de primeira viagem que só aperta Enter nunca passa da primeira pergunta.

### BUG-03 - baixa - 11 interações para quem programa (CA-3), sem teste do roteiro
Contagem do roteiro (terminal 3 + skill 8). O UX conta 10 (nome e repositório, 1 e 2; aqui pasta e confirmação ficaram no terminal). Decidir: tirar a pergunta da pasta (usar `~/<nome>` e avisar) ou juntar perfil/objetivo. Não há teste que prenda o limite.

### BUG-04 - média - sem permissão não oferece caminho (CA-7)
Passos: `repo create` com 403.
Esperado (UX 3.2): opções A) criar na conta pessoal, B) pedir permissão, C) criar vazio no site e passar a URL. Obtido: "o GitHub não criou X. Rode de novo", que repete a falha. Impede seguir sem contorno claro.

### BUG-05 - baixa - acento, espaço e maiúscula
`Meu Aplicativo` e `meu-aplicação` são recusados só com a regra; o UX manda normalizar (minúsculas, hífen). `MeuApp` passa com maiúsculas. Sugerir `meu-aplicativo` e aceitar com Enter.

### BUG-06 - baixa - jargão e texto cru nas mensagens
Lista no tópico "Mensagens" acima. Reproduzir: caminho feliz (mensagem final), falha do clone e retomada. Sugerir "ramos de trabalho", explicar `gh`, mostrar "já feito: repositório criado, cópia na pasta" em vez da lista Python.

### BUG-07 - baixa - pasta apagada depois de concluir
Passos: concluir, apagar a pasta, rodar de novo com o mesmo nome. Obtido: `fatal: cannot change to ...` e pergunta "Seu nome para os commits". Esperado: "A pasta X não existe mais. Quer clonar de novo em X? (sim/não)" ou instrução clara.

### BUG-08 - baixa - sem rede pode aparecer como "sem login"
`gh auth status` com rede fora costuma sair com erro e o script conclui "você ainda não entrou". Não verificado com `gh` real (proibido). Sugestão: distinguir pelo texto do erro, ou checar `gh api user` primeiro.

### BUG-09 - baixa - repositório existente e vazio não é oferecido no passo do nome
UX 3.2 oferece "usar o existente se estiver vazio". O script recusa sempre ao perguntar o nome e só aceita vazio e privado na retomada. É seguro; só difere do roteiro. Decisão do dono: seguir o UX ou atualizar o UX.

## Cobertura que falta (não bloqueia)
Sem teste: CA-1 e CA-3 (texto de skill), mensagem "etapa X de 11" (CA-8, só na skill), CA-2 (medição real, Q2 do UX). Sugestão: teste estrutural que confira a apresentação no início da skill e a contagem de perguntas.

## Parecer
Aprovado para a `develop`, com aceite do usuário para 4 bugs médios e 5 baixos abertos (`aceite_usuario: sim`). Segurança dos atos irreversíveis (privado, confirmação, nunca escrever em repositório alheio ou com conteúdo, sem segredo) está sólida e testada; os defeitos são de experiência de quem não programa. Recomendo corrigir BUG-01, BUG-02 e BUG-04 antes do primeiro uso por alguém de fora (D1 hoje é só o dono).
