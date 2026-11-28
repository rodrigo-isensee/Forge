# Proteção de branch no GitHub: passo a passo para o dono do projeto

Público: o dono do repositório. Este texto vale para a branch de integração e para a `main` do projeto. O time entrega o roteiro; **quem configura é o dono** (`R-CONFORMIDADE`): nenhum agente altera proteção nem ruleset, nem chama a API de escrita, nem recebe ou cola token para isso. Feito uma vez; refaça quando o CI ganhar ou perder um job exigido.

Por que existe: o hook `pre-push` local é pulado por `--no-verify` e pelo envio pelo site (`R-MAIN`, `R-VERIFY`). Só o servidor barra o merge com o check vermelho ou ainda rodando, inclusive o do dono.

## Antes de começar
- O repositório precisa aceitar rulesets. Em repositório privado no plano gratuito, a proteção **não existe**; subir de plano custa dinheiro e é decisão do dono (`R-CUSTO`). Sem decisão, o repositório fica sem esta camada, e o time diz isso em vez de propor atalho pago.
- Os checks exigidos são os jobs do CI do projeto. O `devops-engineer` lista os nomes exatos dos jobs (o `name:` de cada job em `.github/workflows/`) e o dono usa essa lista no passo 9.
- O gatilho dos workflows exigidos fica sem filtro de caminho: com filtro, o PR que não toca o caminho deixa o check pendente para sempre, e a pressão leva ao desvio. Para pular trabalho, pule o passo dentro do job.
- O PR roda a versão do workflow da própria branch. Mudança em `.github/` passa pelo parecer do `devops-engineer` e do `security-engineer` (`R-REVIEW`, `R-SEGURANCA`) antes do merge.

## Suíte dividida em partes: o check exigido é o agregador
Quando o `devops-engineer` divide a suíte em partes (matriz de jobs) para o PR e a integração ficarem rápidos, valem estas regras, que a proteção acima pressupõe:
- **Orçamento de tempo.** Fixe o alvo do PR e o da integração e divida a suíte em partes iguais por **unidade de teste**, não por arquivo (um arquivo grande desequilibra a divisão). A conta é T = alvo menos o overhead do job (meça o do projeto em `gh run view`); cada parte cabe em T.
- **O check exigido é o job agregador**, com o nome que o dono listou no passo 9. As pernas da matriz têm nome livre ("parte K/N") e **não** entram na lista de exigidos: renomear, somar ou tirar uma perna não mexe na proteção. Renomear o agregador mexe, e é do dono (`R-CONFORMIDADE`).
- **O agregador só passa com todas as N pernas em `success`.** Perna vermelha, pulada ou cancelada reprova (job pulado conta como verde para a regra de proteção; por isso o agregador roda com `always()` e exige `success` de cada necessário, nunca `!contains(failure)`). Ele só lê o resultado dos jobs necessários e não executa código da branch; o teto de testes pulados, quando existe, é um job próprio listado nos necessários dele.
- **Guarda de completude.** A divisão por fatia das ferramentas da stack (por exemplo `pytest-split` ou `vitest --shard K/N`) não prova sozinha que a suíte inteira rodou. O agregador (ou o job de soma que ele exige) confere que a quantidade de testes executados somada nas N pernas é igual à de testes coletados, que nenhuma perna coletou zero, e que o N da matriz, o do `--shard K/N` e o da soma são o mesmo número (um teste do CI lê o YAML e compara). O plugin de divisão entra com versão fixa no lockfile, licença permissiva e sem custo (`R-CUSTO`).
- **Tempo por teste sai por anotação, não por log**: a perna verde grava os tempos em anotação de check run (só nome de teste e segundos), lida pela API; nenhum workflow grava de volta no repositório (`R-MAIN`). O que fundir para ganhar tempo (por exemplo, o teto no agregador) vale só para a integração, nunca para o agregador exigido do PR, que continua sem rodar código da branch.

## Ruleset dos portões
Repositório > Settings > Rules > Rulesets > New ruleset > New branch ruleset. Um passo por linha:
1. Name: `portoes`.
2. Enforcement status: **Active**. O modo Evaluate aparece como configurado, mas não barra.
3. Bypass list: **vazia**, sem ator de bypass: nem o papel de administrador, nem o dono, nem o bot.
4. Target branches: Add target > Include by pattern, uma entrada para a branch de integração e outra para `main`.
5. Marque **Restrict deletions** (bloqueio de deleção).
6. Marque **Block force pushes** (bloqueio de force push).
7. Marque **Require a pull request before merging**. Não marque aprovação obrigatória de revisor: a decisão é "checks verdes", e o bot não aprova o próprio PR.
8. Marque **Require status checks to pass**. Deixe **Require branches to be up to date before merging** desmarcado: o novo teste sobre o topo sempre que a base anda é da fila da `R-FLUXO` (seção "Fila de merge"), e marcar a caixa para o servidor barrar é escolha do dono. A garantia é o CI contra a base real: o do PR roda sobre o merge com a base, e o da branch de integração (gatilho de `push` nela) confere cada merge.
9. Em "Add checks", acrescente cada job da lista do `devops-engineer` e, em cada um, deixe a fonte (Source) fixada em **GitHub Actions**. Sem a fonte fixada, um status gravado por token com o mesmo nome vale como verde.
10. Create.

## Ruleset da `main`
1. New branch ruleset, Name: `main-do-dono`, Enforcement status: **Active**.
2. Target branches: só `main`.
3. Marque **Restrict updates**.
4. Bypass list: só o dono, com o modo **For pull requests only**. Este ruleset não tira a exigência dos checks do ruleset dos portões.
5. Create.

## Conferência (só leitura)
Depois de configurar, o dono roda, para a branch de integração e para a `main`:

`gh api repos/<dono>/<repo>/rules/branches/<b>`

A resposta lista as regras: `pull_request`, `required_status_checks` com os jobs da lista, `non_fast_forward` e `deletion`. Para ver a lista de bypass, abra o ruleset na página de rulesets, como administrador: ela precisa estar vazia nos portões. O comando não escreve nada.

## Tirar o bypass de um ruleset que já existe
Se o ruleset da branch de integração foi criado com um ator na lista de bypass (papel de administrador, o dono, app, bot) no modo **Always**, o merge de PR com check pendente ou vermelho continua possível, inclusive para o dono. Só o dono tira, uma vez, pela interface:
1. Repositório > Settings > Rules > Rulesets. Anote cada ruleset que alcança a branch de integração, pegos pela leitura abaixo (`rules/branches/<integração>`), não à mão: um ruleset com alvo `~DEFAULT_BRANCH` ou `~ALL` (comum quando a integração é a branch padrão) ou com curinga também a alcança, e o nome do ruleset não diz isso.
2. Abra cada um, como administrador, e em **Bypass list** remova cada ator. A lista tem de ficar **vazia**; trocar Always por "For pull requests only" não basta nos portões.
3. Confirme **Enforcement status: Active** (Evaluate não barra) e a branch de integração entre os alvos. Salve.
4. Se outro ruleset alcança a branch de integração com bypass próprio (inclusive por `~DEFAULT_BRANCH`, `~ALL` ou curinga), repita nele. O ruleset da `main` não a alcança.
5. Confira pela leitura abaixo e anote a data e o resultado no histórico do pedido.

## Conferência de bypass (só leitura)
1. Ache os rulesets que alcançam a branch de integração, pelo endpoint que já aplica include e exclude:

`gh api repos/<dono>/<repo>/rules/branches/<integração>`

Cada regra da resposta traz `ruleset_id`; a lista de ids vem daí, não de `rulesets` filtrado à mão. É só leitura (GET, sem método nem campo). Cobre rulesets de alvo `~ALL`, `~DEFAULT_BRANCH` ou curinga.

2. Para cada `ruleset_id`:

`gh api repos/<dono>/<repo>/rulesets/<id>`

Na resposta, `bypass_actors` tem de ser `[]` em todos os que alcançam a branch de integração (nos portões e em qualquer outro), `enforcement` tem de ser `active`, e `conditions.ref_name` tem de alcançá-la: o `include` cita a branch, `~ALL`, `~DEFAULT_BRANCH` ou um padrão que a case, **e o `exclude` não a tira**. Confira o `exclude` também. Se vier `current_user_can_bypass`, o esperado para a conta que mescla é `never`. Campo ausente é "não verificado", nunca "sem bypass".

## Integração vermelha sem bypass
Sem bypass, a integração vermelha não se conserta por merge por fora. A saída é o conserto da fila (`R-FLUXO`; "Conserto da integração vermelha" em `ritmo-e-corte.md`, da skill `trabalho-em-paralelo`): PR de conserto em branch própria, diff ligado ao vermelho, CI completo do PR com cada teste que falhou rodando e passando, merge preso ao head revisado, um conserto por vez e o CI da integração acompanhado até o verde. Nenhum portão é dispensado; o custo é o tempo de uma rodada. Se a integração ficar vermelha por mais de 4 h, em dois episódios, sem saída por esse caminho, o dono decide de novo sobre o bypass (`R-DECISAO`).

## Fila de merge (`R-FLUXO`)
A integração recebe um merge por vez, cada PR testado sobre o topo dela, e com ela vermelha só entra o conserto (detalhe em `ritmo-e-corte.md`, da skill `trabalho-em-paralelo`). Quem garante a fila depende de onde mora o repositório:
- **Repositório de organização** (público, ou privado com GitHub Enterprise Cloud): a fila nativa do GitHub. No ruleset dos portões, o dono marca **Require merge queue**; o workflow de cada check exigido precisa do gatilho `merge_group`, senão o check não é reportado e o merge falha.
- **Conta pessoal** (sem fila nativa): o `tech-lead` faz a fila à mão. Antes do merge, ele confere se o CI do PR rodou sobre o topo da integração; se a base andou, traz a base e espera o CI de novo. Se o dono quiser o servidor barrando, ele marca a caixa do passo 8 (escolha dele, `R-DECISAO`).
- Em repositório privado, cada novo teste gasta minutos da cota gratuita do plano (`R-CUSTO`).

## Limites
- Repositório privado no plano gratuito: veja "Antes de começar".
- "Branch atualizada com a base" repete o CI quando há vários PRs na fila. Tirar essa regra afrouxa o processo e é escolha do dono (`R-DECISAO`).
- A interface do GitHub muda; a conferência por `gh api` não depende dela.
