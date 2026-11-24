# Ruleset da develop (apagar e reescrever) e criação de tags v*: passos do dono

Pedido v0478, etapa E172.4. Cartões `RULESET-DEVELOP-APAGAR-REESCREVER` e `RULESET-TAGS-CRIACAO`. Público: o dono. **Quem aplica é o dono, pela interface** (`R-CONFORMIDADE`): nenhum agente altera ruleset nem chama a API de escrita. Custo zero (`R-CUSTO`): rulesets e chave de implantação são gratuitos em repositório público. Leitura do estado em 24/11, só por GET.

## Estado lido (GET, 24/11)
Repositório público, de conta pessoal (fora de organização).

| Ruleset | Alvo | Regras | Bypass |
|---|---|---|---|
| `checks-obrigatorios-develop-main` (26701749) | `develop`, `main` | só `required_status_checks`: `bateria`, `bateria (python 3.14)`, `catraca` (fonte GitHub Actions, id 15368; `strict` falso) | `[]` |
| `merge-commit-homolog-main` (25432260) | `homolog`, `main` | `pull_request` (só merge commit), `required_status_checks`, `non_fast_forward`, `deletion` | `[]` |
| `tags-v-imutaveis` (27992073) | tags `v*` | `update`, `deletion` | `[]` |
| `mainRuleset` (24947028) | branch | desligado | n/a |

`rules/branches/develop` devolve uma regra só, do 26701749. Conclusão: **a `develop` hoje pode ser apagada e reescrita por force push**; `homolog` e `main` não (25432260 cobre as duas). As tags `v*` não podem ser movidas nem apagadas, mas **qualquer ator com escrita pode criar** uma `v*` nova.

## Cartão RULESET-DEVELOP-APAGAR-REESCREVER
Objetivo: acrescentar `deletion` e `non_fast_forward` ao 26701749, sem tocar nos três checks.

Passos (interface; Settings > Rules > Rulesets):
1. Abra o ruleset `checks-obrigatorios-develop-main` (id 26701749).
2. Confirme **Enforcement status: Active** e a lista de alvos como está (`develop` e `main`). Não mexa em alvos.
3. Em **Rules**, marque **Restrict deletions**.
4. Marque **Block force pushes**.
5. **Não desmarque nem reedite** "Require status checks to pass": ela já traz `bateria`, `bateria (python 3.14)` e `catraca`, cada um com fonte GitHub Actions. Acrescentar duas regras não mexe nessa lista; os checks só se perdem se alguém tirar a marca ou apagar linha.
6. **Bypass list** continua vazia. Salve (Save changes).

Efeito em `main`: o 26701749 também a alcança; as regras repetem as do 25432260 (sem conflito, valem a soma).

Não use `gh api` com PUT/PATCH: o PUT substitui a lista inteira de regras e um campo omitido apaga os checks.

Conferência (só leitura), depois de salvar:
```
gh api repos/rodrigo-isensee/Forge/rulesets/26701749 --jq '{enf:.enforcement,bypass:.bypass_actors,tipos:[.rules[].type],checks:[.rules[]|select(.type=="required_status_checks")|.parameters.required_status_checks[].context]}'
gh api repos/rodrigo-isensee/Forge/rules/branches/develop --jq '[.[].type]'
```
Esperado: `enf` igual a `active`, `bypass` igual a `[]`, `tipos` com `required_status_checks`, `deletion` e `non_fast_forward`, e `checks` com os três nomes. A segunda saída lista as mesmas três regras da `develop`. Campo ausente é "não verificado".

Teste sem escrever na `develop`: o PR seguinte para a `develop` ainda deve exigir os três checks (o botão de merge fica desabilitado com check pendente).

Reversão: no mesmo ruleset, desmarque as duas caixas e salve. Nada mais muda, os checks ficam. Se um check sumir por engano, recoloque pela mesma tela (Add checks, fonte GitHub Actions) e confira pela leitura acima.

Risco: `non_fast_forward` impede `git push --force` e reescrita de histórico na `develop`; o fluxo normal (merge de PR) não usa isso. `R-VERIFY` já proíbe `--force`.

## Cartão RULESET-TAGS-CRIACAO (recomendação, decisão do dono)
Problema: o 27992073 impede mover e apagar `v*`, mas não impede criar. Quem tem escrita (o token do bot, um workflow comprometido) pode publicar `v9.9.9` falsa, que `bin/forge_versoes.py` e a release tratam como versão (`R-MAIN`: release só depois do merge do dono).

Por que não é só acrescentar `creation`: o `release.yml` cria a tag com `github.token` (`gh release create`, linha 73). O `GITHUB_TOKEN` é o app GitHub Actions e **não pode entrar na lista de bypass**; com `creation` ligado e sem bypass a release do próprio Forge falha.

Recomendação (custo zero, repositório pessoal): **chave de implantação como único ator de bypass**.
1. Gerar um par de chaves dedicado (`ssh-keygen -t ed25519`, sem frase, só para isso). Fora do repositório e do terminal dos agentes.
2. Settings > Deploy keys > Add deploy key, com **Allow write access**; cole a pública.
3. Settings > Environments > criar `release`: restrinja **Deployment branches** a `main`; em repositório público, acrescente **Required reviewers** com o dono (aprovação por release, coerente com `R-MAIN`). Guarde a privada como secret **do environment** `release` (não do repositório).
4. No 27992073, em **Bypass list** > Add bypass, escolha **Deploy keys** (modo Always). Marque **Restrict creations** e salve. Mantenha `update` e `deletion`.
5. Mudança do `release.yml` (escopo `workflow`, só o dono envia; o `devops-engineer` prepara numa branch `melhoria/*` e o parecer de segurança precede): job com `environment: release`, `ssh-agent` com a chave, `git tag` e `git push` da tag por SSH, e depois `gh release create "$tag"` sobre a tag que já existe, com o `github.token` (criar release sobre tag existente não cria ref). Ações fixadas por SHA, `permissions: contents: write` só nesse job.

Alternativa sem chave: organização gratuita. Move-se o repositório para uma organização, onde o bypass aceita papel ou equipe; o `GITHUB_TOKEN` continua fora da lista, então o job ainda precisaria de chave ou de GitHub App próprio. Mais invasiva (muda endereço dos projetos), por isso não é a recomendada.

Alternativa de menor ganho: não fechar a criação e manter só `update` e `deletion` (estado de hoje), aceitando que uma tag falsa nova é possível mas não sobrescreve nenhuma existente; o CI de release recusa tag que já exista (linha 65).

Conferência (só leitura):
```
gh api repos/rodrigo-isensee/Forge/rulesets/27992073 --jq '{enf:.enforcement,bypass:.bypass_actors,tipos:[.rules[].type]}'
```
Esperado: `tipos` com `update`, `deletion` e `creation`; `bypass` com um único ator do tipo `DeployKey`. Prova funcional: na próxima release a tag aparece criada pela chave e o job espera a sua aprovação; um `git push origin refs/tags/v0.0.0-teste` com outra credencial é recusado (o teste da tag falsa é do dono, e a tag nunca é criada se o ruleset estiver certo).

Reversão: no 27992073, desmarque **Restrict creations** (o ruleset volta ao estado de hoje) e, se quiser, apague a chave de implantação e o environment. Se a release falhar por falta do bypass, a tag pode ser criada pelo dono pela interface da release.

Risco: a chave privada vira credencial de longa duração; por isso fica só no environment `release`, restrito à `main` e com aprovação do dono. Rotação: gerar outra, trocar a deploy key e o secret.

## Ordem sugerida
Primeiro o cartão da `develop` (baixo risco, reversível em um clique). A tag fica para depois do parecer de segurança sobre o novo `release.yml`; até lá o estado atual segue válido.
