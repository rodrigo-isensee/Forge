# Trocar a conta dos agentes por uma conta robô sem poder de administrador

Para quem: o dono do repositório do Forge. Tempo: cerca de 15 minutos. Custo: zero (conta gratuita, sem plano pago, `R-CUSTO`).
Origem: cartão TOKEN-AGENTES-BOT, opção A (o robô escreve código, mas não administra); desenho na ADR 0009, seção 9.
Quem faz: só você, pelo site do GitHub e pelo seu editor de texto. Nenhum agente executa estes passos nem recebe a chave (`R-CONFORMIDADE`).

## Por que fazer isso
Hoje os agentes entram no GitHub com a sua conta. Ela é de administrador, e as travas do repositório (os checks obrigatórios) podem não valer para ela: um agente conseguiria mesclar por cima de um check vermelho. Com uma conta robô sem administração, a trava vale para todos os agentes, e só você consegue desligá-la.

## Antes de começar
- O GitHub muda o nome dos botões de vez em quando. Confira os textos abaixo com o que aparece na tela. Se algo for muito diferente, pare e avise o Jarvis; não improvise com permissões.
- Abra uma janela anônima (privada) do navegador só para o robô, para não confundir com a sua conta.
- Separe um e-mail para o robô. O GitHub não aceita o mesmo e-mail em duas contas. Truque gratuito: se o seu é `voce@exemplo.com`, use `voce+robo@exemplo.com` (a maioria dos provedores entrega na sua caixa normal).
- Tenha à mão um aplicativo de senhas para guardar a senha e a chave do robô. Nunca no repositório.
- Anote o endereço do repositório do Forge como aparece no navegador: `https://github.com/<seu-usuário>/<repositório>`. Nos passos, troque `<seu-usuário>/<repositório>` por ele.
- O GitHub permite a cada pessoa uma conta de máquina gratuita além da pessoal; o robô é essa conta.

## Passo 1. Criar a conta do robô (3 minutos)
Na janela anônima:
1. Abra `https://github.com/signup`.
2. Preencha o e-mail do robô, uma senha forte e um nome de usuário que diga o que é (exemplo: `forge-agentes-bot`). Anote o nome.
3. Resolva a verificação e confirme pelo e-mail que o GitHub enviar.
4. Se o GitHub oferecer plano, fique no gratuito ("Free"). Pule qualquer teste de plano pago.
5. Ligue a verificação em duas etapas: foto no canto, "Settings", "Password and authentication", "Enable two-factor authentication". Guarde os códigos de recuperação junto da senha.

O que você vê no fim: o painel do GitHub com o nome do robô no canto de cima, à direita.

## Passo 2. Convidar o robô com permissão de escrita (3 minutos)
Na sua janela normal, com a sua conta:
1. Abra `https://github.com/<seu-usuário>/<repositório>/settings/access`.
2. Clique em "Add people".
3. Digite o nome do robô e escolha-o na lista.
4. No papel, marque **Write** (escrita). Não marque Admin, Maintain nem Triage.
5. Confirme. Aparece "Pending invite" (convite pendente).

Na janela anônima, com o robô:
6. Abra `https://github.com/<seu-usuário>/<repositório>/invitations` e clique em "Accept invitation".

O que você vê no fim: na sua lista de acessos, o robô com o papel "Write".

Ainda na sua conta, confira a lista de exceção das travas: "Settings", "Rules", "Rulesets"; abra cada ruleset e olhe o campo "Bypass list". Num repositório da sua conta pessoal, essa lista guarda papéis, não pessoas: você não vai achar o nome do robô ali. Confira que **nem "Write" nem "Maintain" estão na lista**; só o papel de administrador ("Repository admin") pode estar. Se "Write" ou "Maintain" aparecer, tire-o. Não mexa no resto da lista agora: tirar a exceção do administrador é outro cartão (AV1-BYPASS-RULESET), que vem depois desta troca.

## Passo 3. Gerar a chave de acesso do robô (4 minutos)
A chave de acesso (o GitHub chama de "token") é uma senha longa que o programa usa no lugar da senha da conta.

Na janela anônima, com o robô:
1. Abra `https://github.com/settings/tokens` (foto, "Settings", no fim da barra lateral "Developer settings", "Personal access tokens").
2. Escolha "Tokens (classic)", clique em "Generate new token" e depois em "Generate new token (classic)". O GitHub pode pedir a senha ou o código de duas etapas.
3. Em "Note" (o nome da chave), escreva `agentes-forge`.
4. Em "Expiration" (validade), escolha **90 dias** ou menos. Nunca "No expiration". Ponha um lembrete no calendário uns 10 dias antes de vencer.
5. Nas permissões ("scopes"), marque **só `repo`**. **Não marque `workflow`**: sem ela o robô não altera os arquivos de automação do CI, de propósito. Não marque `admin:*`, `delete_repo` nem outra.
6. Clique em "Generate token", no fim da página.

O que você vê no fim: a chave, começando por `ghp_`. **Ela só aparece agora.** Copie-a direto para o aplicativo de senhas; se fechar a página antes, gere outra.

Por que a chave "classic" e não a "Fine-grained", mais nova? A nova só alcança repositórios da própria conta da chave ou de uma organização; o robô é só convidado no repositório do seu usuário, então ela não o enxergaria. A "classic" com `repo` alcança só o que o robô pode acessar: o Forge, com papel de escrita. Se o Forge passar para uma organização, vale trocar para a nova.

## Passo 4. Guardar a chave no seu computador (3 minutos)
Regra: **a chave nunca vai para uma conversa com o Jarvis, nem para um arquivo do repositório, nem para uma mensagem de commit.** Quem a vê age como o robô.

1. Abra um terminal novo no mesmo computador (ou contêiner) onde o Claude Code roda, fora da conversa com o Jarvis. No VS Code com contêiner, é o menu "Terminal", "New Terminal". Digite `nano ~/.claude/settings.json` e aperte Enter. A pasta `.claude` é oculta (o nome começa com ponto), por isso o comando leva o caminho inteiro; o `nano` é um editor simples, que abre dentro do próprio terminal. É onde está a chave atual.
   No `nano`, mova o cursor com as setas do teclado. Para salvar: Ctrl+O e Enter. Para sair: Ctrl+X.
2. Procure o bloco `"env"` e, dentro dele, a linha `"GH_TOKEN": "..."`.
3. **Antes de mudar, copie a linha antiga para o aplicativo de senhas.** Ela é o seu caminho de volta.
4. Troque o valor entre aspas pela chave nova do robô. Mantenha as aspas e a vírgula como estavam.
5. Salve o arquivo e copie qualquer outra coisa por cima, para a chave sair da área de transferência.
6. Feche todas as janelas do Claude Code e abra uma nova, para ela ler a chave nova.

Esse arquivo é protegido contra edição pelos agentes de propósito (ADR 0009, seção 5): quem faz a troca é você, à mão.

## Passo 5. Conferir que deu certo (2 minutos)
Numa sessão nova, peça ao Jarvis: "rode `gh api user --jq .login` e `gh api repos/<seu-usuário>/<repositório> --jq .permissions`". Os dois só leem; nenhum muda nada.

O que você deve ver:
- No primeiro, o nome do **robô**, e não o seu.
- No segundo, algo como `{"admin":false,"maintain":false,"pull":true,"push":true,"triage":true}`. O que importa: `"admin":false` e `"push":true`.

Se aparecer o seu nome ou `"admin":true`, a chave antiga ainda está em uso: volte ao Passo 4, confira se salvou o arquivo e abra uma sessão nova.

Depois, avise o Jarvis que a troca terminou. Ele registra a conclusão no cartão.

## Como voltar atrás
1. Abra de novo o arquivo, como no Passo 4 (`nano ~/.claude/settings.json`), e recoloque a linha antiga que você guardou no Passo 4.
2. Salve, feche o Claude Code, abra uma sessão nova e repita o Passo 5: deve aparecer o seu nome.
3. Para desligar o robô de vez: na conta dele, apague a chave em `https://github.com/settings/tokens` ("Delete"); na sua conta, remova o robô em `https://github.com/<seu-usuário>/<repositório>/settings/access`.
4. Se suspeitar que a chave vazou (apareceu numa conversa, num arquivo ou num commit), apague-a na hora, no mesmo endereço do item 3, e gere outra pelo Passo 3. Não espere a validade acabar.

## O que muda para o time depois da troca
O robô **pode**: ler o código, criar branches, enviar commits para as branches `melhoria/*`, abrir pedidos de mesclagem (PR), comentar e mesclar na `develop` e na `homolog` quando todas as travas estiverem verdes.

| O robô **não pode** | Quem faz |
|---|---|
| Mesclar na `main` (`R-MAIN`) | você |
| Mesclar por cima de check vermelho | ninguém, sem você mudar a trava |
| Mudar travas, rulesets, segredos e configurações do repositório | você, pelo site |
| Enviar mudança em `.github/workflows/` (a chave não tem `workflow`). Vale também para a branch que só trouxe da `develop` (por merge) um commit que muda essa pasta: o GitHub recusa o envio. É o esperado, não um defeito | você: o time prepara a branch e entrega o comando de envio |
| Apagar o repositório ou mudar quem tem acesso | você |

Os commits dos agentes seguem com o nome e o e-mail do seu `~/.gitconfig`; só o envio passa a ser do robô. O PR da `homolog` para a `main` continua aberto e mesclado por você.

Nos primeiros dias, se algum fluxo dependia do seu poder de administrador para passar por cima de um check, ele vai falhar. É o esperado: trate como defeito do fluxo (corrigir o check ou pedir a sua decisão), nunca como algo a contornar.

## As regras provisórias
As regras provisórias de 10/11 (mantidas em 11/11 enquanto os agentes usam a chave de administrador) continuam valendo até você avisar que terminou o Passo 5. Depois do aviso, o Jarvis propõe quais saem, porque o GitHub passa a impô-las, e quais ficam como regra permanente (por exemplo, `R-MAIN`). A exceção do administrador nas travas sai depois, pelo cartão AV1-BYPASS-RULESET.

## Resumo em uma olhada
1. Criar a conta gratuita do robô, com verificação em duas etapas.
2. Convidar o robô com papel Write (nunca Admin) e conferir que ele não está na lista de exceção das travas.
3. Gerar a chave "classic" só com `repo`, validade de 90 dias.
4. Trocar o valor de `GH_TOKEN` no `~/.claude/settings.json`, guardando a linha antiga; abrir uma sessão nova.
5. Conferir: nome do robô e `"admin":false`; avisar o Jarvis.
