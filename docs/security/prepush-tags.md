---
tipo: revisao-seguranca
contrato: 1
pedido: prepush-leve
branch: melhoria/prepush-tags
commit: 24e055ce0157013cee88f2873b3147eb37ab2b4e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: prepush-tags (pedido prepush-leve, PR-a)

## Gatilhos
Controle do Forge: `.githooks/pre-push` (caminho novo `tags_ja_no_remoto`, subitem de tags do E2). Gatilho da R-SEGURANCA.

## Achados
- A1 (recomendado) tests/test_pre_push_tags.py:23 · Faltam casos de falha fechada que só a sonda cobriu: tag de árvore (o ^{commit} recusa), remoto de nome que é prefixo de outro (orig contra origin) e tag mais remoção de branch. Passaram; um subTest para cada fixa o comportamento.

## Detalhe dos achados
**A1.** Evidência: `tests/test_pre_push_tags.py:23` (`test_falha_fechada_entra_na_fila`) e `.githooks/pre-push:198-201`. Sonda descartável com o `Repo` de `tests/apoio_pre_push.py` (repositório temporário, trava presa por fora): tag apontando para árvore, remoto `.`, remoto `orig` com só `refs/remotes/origin/*`, tag mais remoção de `refs/heads/y` entram na fila; tag mais remoção de tag sai sem teste (correto, nenhum commit novo); `refs/tags/t` enviada para `refs/heads/main` é barrada. Caminho de ataque: nenhum hoje; o risco é regressão silenciosa numa mudança futura da função. Severidade: informativa. Correção mínima: acrescentar esses quatro casos ao laço de `test_falha_fechada_entra_na_fila`. Esforço P. Dono: devops-engineer.

Conferido sem achado:
- R-MAIN e R-FLUXO: a recusa de `refs/heads/main|homolog|develop` (`.githooks/pre-push:161`) e a de tag movida (R-VERIFY, `:153`) ficam no laço das refs, que sai com 1 antes do caminho novo (`:206`). Coberto por `test_tag_nao_abre_develop_homolog_main_nem_tag_movida` e pela sonda (tag local para `refs/heads/main`).
- Falha fechada de `tags_ja_no_remoto` (`:193-204`): sem ref, ref que não é tag (`so_tags=0`, inclusive remoção de branch), nenhuma tag enviada, remoto vazio, começando com `-` ou fora de `[A-Za-z0-9._-]` (URL), sha fora de hexadecimal, objeto que não chega a commit, erro do `git` e commit fora de `refs/remotes/<remoto>/*` voltam ao caminho de sempre, com trava e fila. O modo `--suite` não entra (`:206`). O padrão de `--remotes=<nome>` sem curinga vira `refs/remotes/<nome>/*`, então `orig` não casa `origin`.
- A2 da rodada 1 (`16f5660`, confiança nas refs de acompanhamento locais): fechado como pedia a correção mínima; o registro está em `docs/hooks.md:115` e no comentário de `.githooks/pre-push:186-192`. Segue baixa: a tag não dispara workflow (`ci.yml` reage a PR e push de `develop|homolog|main`; `release.yml`, a push de `main`) e o código só chega à develop pelo PR com CI.
- A1 e A3 da rodada 1 (o `*.md` de controle e o modo do arquivo na `sem_codigo`) não se aplicam: a `sem_codigo`/`checagem_leve` não está nesta branch.
- E1 (parecer sem prova de árvore verde) ausente aqui: `so_parecer` (`:236`) está igual à base `b45e40a`; ele fica na `melhoria/prepush-sem-codigo`.
- O hook limpa `GIT_DIR` e afins antes da função (`:183`), e o `git` dela roda na raiz do repositório do push.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `shellcheck -S warning .githooks/pre-push` limpo; `python3 -I -m unittest discover -s tests -p test_pre_push_tags.py` com 3 testes OK; sonda de 6 casos (fora do repositório) OK. Faltaram no PATH: `gitleaks`, `zizmor` e `actionlint` (o diff não toca workflow nem segredo). Parecer de devops em `docs/devops/prepush-tags.md` citado, não refeito.
