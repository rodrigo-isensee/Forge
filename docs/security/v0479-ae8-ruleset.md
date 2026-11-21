---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae8-ruleset
commit: c2f75cacdf29be4eea6ffb8bd96a263f89399021
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-ae8-ruleset (revalidação)

Etapa E58.11 do pedido v0478 (AE8.1), revalidação depois da volta única (E58.9). A rodada anterior (E58.4, head `a298cdbc`, parecer `aprovado` com A1 recomendado) fica no git.

## Gatilhos
Gatilhos: nenhum item da R-SEGURANCA no diff; revisão pedida pelo brief porque o texto orienta a autorização de merge na `develop` (configuração do servidor, ADR 0008).

## Delta lido
`forge-check parecer delta`, intervalo `a298cdbc..c2f75cac`: no domínio, `docs/protecao-de-branch.md` e `templates/projeto/docs/engineering/protecao-de-branch.md`, lidos inteiros no diff; fora do domínio, `changelog.d/v0479-ae8-ruleset.md`. Nenhum código, workflow, hook nem controle do Forge. O aviso do delta (merge `26827d3` fora da `origin/develop` local) conta o merge inteiro; o que ele trouxe no domínio são os mesmos dois arquivos, já lidos.

## Resumo
- Os comandos seguem só leitura (chamada à API sem método nem campo, GET); nenhum passo pede token, escrita na API ou alteração de ruleset por agente (`R-CONFORMIDADE`).
- O ruleset do bypass Always (`checks-obrigatorios-develop-main`) passa a ser nomeado e entra na exigência de lista vazia; só o `main-do-dono` mantém bypass, e só na `main`.
- O modelo de projeto segue neutro (branch de integração, portões), sem nome do Forge (`R-NEUTRO`).

## Achados anteriores
- A1 (recomendado): **atendido**. A lista de rulesets vem de `rules/branches/develop` (`docs/protecao-de-branch.md:54-58`) e o passo 1 da remoção manda não escolher à mão (`:45`); o critério aceita `develop`, `~ALL`, `~DEFAULT_BRANCH` ou padrão que a case e exige que o `exclude` não a tire (`:64`). O mesmo no modelo: `templates/projeto/docs/engineering/protecao-de-branch.md:50`, `:57-61` e `:67`.

Observação sem achado: o endpoint `rules/branches/<b>` devolve só regras de rulesets ativos; um `portoes` em Evaluate some da lista em vez de aparecer com `enforcement` errado. A conferência de `:39-41` (regras `pull_request` e `required_status_checks` esperadas na `develop`) e o passo 3 (Enforcement Active) já pegam essa ausência; a AE8.2 pode tratar "regra esperada ausente" como falha.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Suíte não rodada (brief: sem suíte local; diff só de texto); o CI do PR fica com o integrador. Ferramentas: leitura estática do delta; a ferramenta de varredura de segredos não está no PATH (lacuna registrada, sem instalação, `R-CUSTO`); o delta não traz credencial nem valor sensível, conferido à mão.
