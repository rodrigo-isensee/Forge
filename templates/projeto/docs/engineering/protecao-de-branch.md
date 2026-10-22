# Proteção de branch no GitHub: passo a passo para o dono do projeto

Público: o dono do repositório. Este texto vale para a branch de integração e para a `main` do projeto. O time entrega o roteiro; **quem configura é o dono** (`R-CONFORMIDADE`): nenhum agente altera proteção nem ruleset, nem chama a API de escrita, nem recebe ou cola token para isso. Feito uma vez; refaça quando o CI ganhar ou perder um job exigido.

Por que existe: o hook `pre-push` local é pulado por `--no-verify` e pelo envio pelo site (`R-MAIN`, `R-VERIFY`). Só o servidor barra o merge com o check vermelho ou ainda rodando, inclusive o do dono.

## Antes de começar
- O repositório precisa aceitar rulesets. Em repositório privado no plano gratuito, a proteção **não existe**; subir de plano custa dinheiro e é decisão do dono (`R-CUSTO`). Sem decisão, o repositório fica sem esta camada, e o time diz isso em vez de propor atalho pago.
- Os checks exigidos são os jobs do CI do projeto. O `devops-engineer` lista os nomes exatos dos jobs (o `name:` de cada job em `.github/workflows/`) e o dono usa essa lista no passo 9.
- O gatilho dos workflows exigidos fica sem filtro de caminho: com filtro, o PR que não toca o caminho deixa o check pendente para sempre, e a pressão leva ao desvio. Para pular trabalho, pule o passo dentro do job.
- O PR roda a versão do workflow da própria branch. Mudança em `.github/` passa pelo parecer do `devops-engineer` e do `security-engineer` (`R-REVIEW`, `R-SEGURANCA`) antes do merge.

## Ruleset dos portões
Repositório > Settings > Rules > Rulesets > New ruleset > New branch ruleset. Um passo por linha:
1. Name: `portoes`.
2. Enforcement status: **Active**. O modo Evaluate aparece como configurado, mas não barra.
3. Bypass list: **vazia**, sem ator de bypass: nem o papel de administrador, nem o dono, nem o bot.
4. Target branches: Add target > Include by pattern, uma entrada para a branch de integração e outra para `main`.
5. Marque **Restrict deletions** (bloqueio de deleção).
6. Marque **Block force pushes** (bloqueio de force push).
7. Marque **Require a pull request before merging**. Não marque aprovação obrigatória de revisor: a decisão é "checks verdes", e o bot não aprova o próprio PR.
8. Marque **Require status checks to pass** e **Require branches to be up to date before merging** (branch atualizada com a base).
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

## Limites
- Repositório privado no plano gratuito: veja "Antes de começar".
- "Branch atualizada com a base" repete o CI quando há vários PRs na fila. Tirar essa regra afrouxa o processo e é escolha do dono (`R-DECISAO`).
- A interface do GitHub muda; a conferência por `gh api` não depende dela.
