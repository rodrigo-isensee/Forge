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
8. Marque **Require status checks to pass**. Deixe **Require branches to be up to date before merging** desmarcado (decisão do dono, E8 da 0.45.6): o servidor fica como está (D1 do dono para a BP2) e o novo teste sempre que a base anda (D3) é da fila da `R-FLUXO`, à mão pelo `tech-lead` até a I4 (`skills/trabalho-em-paralelo/ritmo-e-corte.md`); em `melhoria/*`, se a base andou sem conflito, o próprio `bin/forge-fechar` a traz por merge e reenvia (passo 2b, H4). A garantia é o CI contra a base real: o do PR roda sobre o merge com a base, o `bin/forge-fechar` para quando o `git merge-tree` acusa conflito com a base que andou (passos 2b e 6a, `docs/fechamento-integrador.md`) e o CI de `push` em `develop`, `homolog` e `main` confere cada merge.
9. Em "Add checks", acrescente os dois abaixo e, em cada um, deixe a fonte (Source) fixada em **GitHub Actions**. Sem a fonte fixada, um status gravado por token com o mesmo nome vale como verde.
- Check exigido: `bateria`
- Check exigido: `catraca`
10. Create.

Os nomes são os `name:` dos jobs em `.github/workflows/ci.yml` e `.github/workflows/catraca.yml`; um teste confere que continuam existindo.

F6 (v0481): a suíte do PR roda uma vez, no Python 3.12; o agregador `bateria (python 3.14)` agora só junta a instalação e a fumaça. Os dois checks exigidos acima não mudam de nome. O `.github/workflows/diario.yml` (suíte no 3.14, e2e no 3.12 e mutantes, uma vez por dia na `develop`) não é check exigido: se quebra, abre uma issue.

F6, corte do envio (v0481 E32.9): no push na `develop`, o job `arvore-envio` (`scripts/arvore-testada.py --do-pr`) pula a suíte quando o commit é o merge de um PR do próprio repositório com a mesma árvore do head e o run do `ci.yml` desse PR (evento `pull_request`, mesmo número, base `develop`, base do run ancestral do head) tem o job `bateria` em success na tentativa mais recente; o agregador `checagem rápida (push na develop)` aceita as pernas puladas só com esse job em success. Sem a prova, erro ou falha do job, a suíte roda inteira. O check `bateria` solto (de outra base, outro workflow ou criado pela API) não prova.

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

## Tirar o bypass de um ruleset que já existe (a `develop` está com exceção)
Estado registrado no quadro de 15/11 (AV1-BYPASS-RULESET): o ruleset `checks-obrigatorios-develop-main`, que atinge a `develop`, tem um ator na lista de bypass com o modo **Always**. Depois desse registro, o dono mesclou PRs direto nela, sem esperar o CI (sete merges, #680 a #715, em três dias, dois com a `develop` quebrada); a data dos merges é posterior a 15/11. Texto pedindo lista vazia não tirou o ator; só o dono tira, uma vez, pela interface:
1. Repositório > Settings > Rules > Rulesets. Anote cada ruleset que alcança a `develop`: o `checks-obrigatorios-develop-main` (o do bypass Always), o `portoes` e qualquer outro. Não escolha à mão pelo nome nem pelo alvo que cita `develop`: pegue a lista pela leitura abaixo (`rules/branches/develop`), que traz os rulesets que alcançam a branch, inclusive por `~ALL`, `~DEFAULT_BRANCH` ou curinga.
2. Abra cada um, como administrador, e olhe **Bypass list**. Remova cada ator listado (papel de administrador, o dono, app, bot). A lista tem de ficar **vazia**; trocar Always por "For pull requests only" **não basta** no `portoes`, porque o merge do PR com check vermelho é justamente o desvio.
3. Confirme **Enforcement status: Active** (Evaluate não barra) e `develop` entre os alvos. Salve.
4. Se outro ruleset alcança a `develop` com bypass próprio (o `checks-obrigatorios-develop-main` ou um terceiro, inclusive de alvo `~ALL`, `~DEFAULT_BRANCH` ou curinga), repita nele. O `main-do-dono` não alcança a `develop` e mantém o bypass "For pull requests only" só para a `main`.
5. Confira pela leitura abaixo e anote a data e o resultado no histórico do pedido.

Efeito esperado: nenhum merge na `develop` sem `bateria` e `catraca` verdes, inclusive o do dono; o botão de merge fica desabilitado com check pendente ou vermelho.

## Conferência de bypass (só leitura)
1. Ache os rulesets que alcançam a `develop`, pelo endpoint que já aplica include e exclude:

`gh api repos/<dono>/<repo>/rules/branches/develop`

Cada regra da resposta traz `ruleset_id`; a lista de ids vem daí, não de `rulesets` filtrado à mão. É só leitura (GET, sem método nem campo). Cobre o ruleset do bypass Always (`checks-obrigatorios-develop-main`), o `portoes` e qualquer outro, mesmo de alvo `~ALL`, `~DEFAULT_BRANCH` ou curinga.

2. Para cada `ruleset_id`:

`gh api repos/<dono>/<repo>/rulesets/<id>`

Na resposta, `bypass_actors` tem de ser `[]` em todos os que alcançam a `develop` (o `checks-obrigatorios-develop-main` e o `portoes`; só o `main-do-dono` pode ter bypass, e só na `main`), `enforcement` tem de ser `active`, e `conditions.ref_name` tem de alcançar a `develop`: o `include` cita `develop`, `~ALL`, `~DEFAULT_BRANCH` ou um padrão que a case, **e o `exclude` não a tira**. Confira o `exclude` também: ruleset que a exclui não a alcança, e o que a inclui por curinga com bypass não escapa. Se vier `current_user_can_bypass`, o esperado para a conta que mescla é `never`. A auditoria diária (AE8.2 do pedido MELHORIAS-ANTI-ERRO) passa a ler esses campos; até ela entrar, a conferência é do dono. Campo ausente é "não verificado", nunca "sem bypass".

## Develop vermelha sem bypass (saída pelo conserto)
Sem bypass, a `develop` vermelha não se conserta empurrando nem mesclando por fora. A saída é o modo conserto da BP2 (`R-FLUXO`; "Conserto da integração vermelha" em `skills/trabalho-em-paralelo/ritmo-e-corte.md`, decisão D2 do dono):
1. PR de conserto numa branch `melhoria/*`, com o diff ligado ao vermelho (toca o arquivo do teste que falhou, um arquivo mudado desde o último verde, ou reverte o merge do intervalo).
2. O CI do PR roda a bateria e a catraca inteiras, e cada teste que falhou no vermelho roda e passa nele. Nada é pulado nem dispensado.
3. O `tech-lead` confere as condições do conserto, mescla preso ao head revisado e acompanha o CI de `push` da `develop` até o verde; sem verde, a `develop` segue fechada para o resto.
4. No Forge, o `bin/forge-fechar` passa a conferir o conserto (BP2 I1 e I4); até lá o `tech-lead` confere à mão. O dono espera a bateria como em qualquer PR: o custo é o tempo de uma rodada.
5. Se a `develop` ficar vermelha por mais de 4 h, em dois episódios, sem saída por esse caminho, o dono decide de novo sobre o bypass (`R-DECISAO`); antes disso o time não propõe atalho.

## Limites
- Repositório privado no plano gratuito: veja "Antes de começar".
- Sem "branch atualizada com a base" (passo 8), o servidor não barra o PR testado sobre uma `develop` velha. Quem barra é a fila da `R-FLUXO` (decisão D1 do dono para a BP2, 20/11: sem mudar endereço nem ruleset). Até a I4 entrar no `bin/forge-fechar`, ela é à mão, pelo `tech-lead` (`skills/trabalho-em-paralelo/ritmo-e-corte.md`): hoje o passo 6a só para no conflito e não retesta sobre a base que andou; merge sem essa conferência não passa pela fila, e a quebra sem conflito só aparece no CI de `push` da `develop`. Reabre quando o Forge for para uma organização: lá, a fila nativa do GitHub (BP9).
- A interface do GitHub muda; a conferência por `gh api` não depende dela.
- Com o ruleset ligado e sem desvio, o próprio dono espera a bateria. É o que a decisão pede.
