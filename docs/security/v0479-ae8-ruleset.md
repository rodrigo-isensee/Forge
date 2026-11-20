---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae8-ruleset
commit: a298cdbcdccf035d91769e2beb5707e22ec162cd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-ae8-ruleset

Etapa E58.4 do pedido v0478 (AE8.1). Diff lido inteiro, `5ccac0bf..a298cdbc`: `docs/protecao-de-branch.md` (+25), `templates/projeto/docs/engineering/protecao-de-branch.md` (+18), `changelog.d/v0479-ae8-ruleset.md` (+2). Só texto ao dono; nenhum código, workflow, hook nem controle do Forge.

## Gatilhos
Gatilhos: nenhum item da R-SEGURANCA no diff; revisão pedida pelo brief porque o texto orienta a autorização de merge na `develop` (configuração do servidor, ADR 0008).

## Resumo
- O texto cumpre o AE8: lista de bypass vazia no ruleset dos portões, inclusive para o dono; "For pull requests only" declarado insuficiente no `portoes` (correto: é o merge do PR com check vermelho que o desvio libera); Enforcement Active e não Evaluate.
- A configuração continua do dono (`R-CONFORMIDADE`): os comandos do texto são só leitura (chamada à API sem método nem campo, portanto GET); nenhum passo pede token, escrita na API ou alteração de ruleset por agente.
- "Campo ausente é não verificado, nunca sem bypass" (`docs/protecao-de-branch.md:58`, modelo `:61`) fecha o falso negativo real: a API omite `bypass_actors` para quem não administra o ruleset.
- A saída da integração vermelha é o conserto da BP2, sem bypass nem portão dispensado, e a reabertura do bypass volta ao dono (`R-DECISAO`), coerente com a D2 e a D5 da BP2 do dono (20/11 07:47).
- O `main-do-dono` mantém o bypass "For pull requests only" só na `main`, que não alcança a `develop` e não tira os checks do `portoes`: sem regressão.
- Modelo de projeto neutro (branch de integração, portões), sem nome do Forge (`R-NEUTRO`).

## Achados
- A1 (recomendado) docs/protecao-de-branch.md:54 · A lista de rulesets "que atingem a develop" é escolhida à mão e o critério é `conditions.ref_name.include` citar `develop`: ruleset com `~ALL` ou padrão (`refs/heads/*`) escapa. Derivar a lista de `ruleset_id` de `rules/branches/develop` e conferir `exclude`. Idem no modelo :57.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `docs/protecao-de-branch.md:45` (passo 1, "anote cada ruleset cujo alvo inclui `develop`"), `:54` e `:58` (lista pelo endpoint `rulesets` e critério `conditions.ref_name.include` cita `develop`); o mesmo no modelo, `templates/projeto/docs/engineering/protecao-de-branch.md:50`, `:57` e `:61`. Caminho: um segundo ruleset com alvo `~ALL`, `~DEFAULT_BRANCH` ou padrão curinga e ator de bypass Always alcança a `develop` sem citá-la literalmente; o dono (e, depois, a auditoria AE8.2 que herda o critério) o descarta, e o merge com check vermelho segue possível. Não é ataque externo: é desvio do próprio portão por quem já administra o repositório, o risco que o AE8 fecha; por isso recomendação. Severidade: baixa. Correção mínima, nos dois arquivos: obter os ids pelo endpoint `repos/<dono>/<repo>/rules/branches/develop` (cada regra traz `ruleset_id`; já é a leitura da seção "Conferência"), ler cada um pelo endpoint `rulesets/<id>` e exigir que `conditions.ref_name.exclude` não cite a branch; aceitar como alvo `develop`, `~ALL` ou padrão que a case. Esforço: P. Dono: `devops-engineer`.

Observação sem achado: `current_user_can_bypass` reflete a conta que roda a leitura; a conta que mescla no dia a dia é o bot do `tech-lead`, além do dono. A AE8.2 pode ler o campo com as duas credenciais (só leitura).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte não rodada (brief: sem suíte local; diff só de texto); o CI do PR fica com o integrador. Ferramentas: leitura estática do diff e das referências (`skills/trabalho-em-paralelo/ritmo-e-corte.md`, `tests/config.json`); a ferramenta de varredura de segredos não está no PATH (lacuna registrada, sem instalação, `R-CUSTO`); o diff não traz credencial nem valor sensível, conferido à mão.
