# Proteção de branch no GitHub: passo a passo para o dono (Forge)

Público: o dono do repositório. Origem: decisão do dono (F8): `develop`, `homolog` e `main` só recebem merge com a bateria e a catraca verdes, **valendo também para o dono**. Desenho: ADR 0008, seção "Servidor". O time entrega este texto; **quem configura é o dono** (`R-CONFORMIDADE`): nenhum agente altera proteção nem ruleset, nem chama a API de escrita, nem recebe ou cola token para isso (`skills/ci-cd/SKILL.md`). Feito uma vez; refaça só se um nome de job mudar.

Por que existe: sem o servidor barrando, o PR é mesclado com o check ainda rodando ou vermelho, e o `--no-verify` e o site passam pelo hook local (`R-MAIN`, `R-VERIFY`).

## Antes de começar
- O repositório precisa aceitar rulesets. Em repositório privado no plano gratuito, a proteção **não existe**; subir de plano custa dinheiro e é decisão do dono (`R-CUSTO`). Sem decisão, o repositório fica sem esta camada, e o time diz isso em vez de propor atalho pago.
- Os workflows exigidos rodam em todo PR, sem filtro de caminho no gatilho (o `.github/workflows/ci.yml` pula passo, nunca usa `paths-ignore`): com filtro, o check exigido fica pendente para sempre e a pressão leva ao desvio.
- O PR roda a versão do workflow da própria branch. Mudança em `.github/` passa pelo parecer do `devops-engineer` e do `security-engineer` (`R-REVIEW`, `R-SEGURANCA`) antes do merge.

## Ruleset `portoes`
Repositório > Settings > Rules > Rulesets > New ruleset > New branch ruleset. Um passo por linha:
1. Name: `portoes`.
2. Enforcement status: **Active**. O modo Evaluate aparece como configurado, mas não barra.
3. Bypass list: **vazia**, sem ator de bypass: nem o papel de administrador, nem o dono, nem o bot. Foi o desvio de administrador que deixou passar o merge com o check pendente.
4. Target branches: Add target > Include by pattern, uma entrada para cada: `develop`, `homolog` e `main`.
5. Marque **Restrict deletions** (bloqueio de deleção).
6. Marque **Block force pushes** (bloqueio de force push).
7. Marque **Require a pull request before merging**. Não marque aprovação obrigatória de revisor: a decisão é "checks verdes", e o bot não aprova o próprio PR.
8. Marque **Require status checks to pass** e **Require branches to be up to date before merging** (branch atualizada com a base).
9. Em "Add checks", acrescente os dois abaixo e, em cada um, deixe a fonte (Source) fixada em **GitHub Actions**. Sem a fonte fixada, um status gravado por token com o mesmo nome vale como verde.
- Check exigido: `bateria`
- Check exigido: `catraca`
10. Create.

Os nomes são os `name:` dos jobs em `.github/workflows/ci.yml` e `.github/workflows/catraca.yml`; um teste confere que continuam existindo.

## Ruleset `main-do-dono`
1. New branch ruleset, Name: `main-do-dono`, Enforcement status: **Active**.
2. Target branches: só `main`.
3. Marque **Restrict updates**.
4. Bypass list: só o dono, com o modo **For pull requests only**. O dono mescla o PR da `homolog` na `main`, nunca por push direto, e este ruleset não tira a exigência dos checks do `portoes`.
5. Create.

## Conferência (só leitura)
Depois de configurar, o dono roda, para cada `<b>` entre `develop`, `homolog` e `main`:

`gh api repos/<dono>/<repo>/rules/branches/<b>`

A resposta lista as regras: `pull_request`, `required_status_checks` com os dois checks, `non_fast_forward` e `deletion`. Para ver a lista de bypass, abra o ruleset na página de rulesets, como administrador: ela precisa estar vazia no `portoes`. O comando não escreve nada. O `forge doutor` não lê a lista de bypass: uma regra de PR com desvio de administrador parece protegida e não está.

## Limites
- Repositório privado no plano gratuito: veja "Antes de começar".
- "Branch atualizada com a base" repete a bateria quando há vários PRs na fila. Tirar essa regra afrouxa o processo e é escolha do dono (`R-DECISAO`).
- A interface do GitHub muda; a conferência por `gh api` não depende dela.
- Com o ruleset ligado e sem desvio, o próprio dono espera a bateria. É o que a decisão pede.
