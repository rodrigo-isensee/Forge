---
tipo: review
contrato: 1
pedido: catraca-ci
branch: melhoria/catraca-ci
commit: 57b77c1
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: catraca anti-piora do CI (ADR 0008, seção 3)

Escopo: `tests/catraca.py`, `tests/test_catraca.py`, `.github/workflows/ci.yml` (jobs `catraca`, `pr-texto`, `segredos`, `pareceres` e gatilhos), `tests/config.json` (`dono`, `custo_permitido`) e `CHANGELOG.md`, diff `origin/develop..57b77c1`.

Conferido: 41 testes de `tests/test_catraca.py` verdes. `python3 tests/catraca.py --base origin/develop` sai 0. O modo `pareceres` barra, como esperado, enquanto este parecer não estiver aprovado. Experimentos feitos numa árvore de trabalho descartável.

## O que está bom
- Nenhum `pull_request_target` nem `workflow_run`. Permissão `contents: read` no workflow, e o `catraca` acrescenta só `pull-requests: read`. Ações fixadas por SHA. Nenhum segredo além do `github.token`.
- O corpo do PR, `head_ref` e `base_ref` entram só por `env:`, sempre entre aspas, sem `${{ }}` dentro de `run`. O corpo não é executado, só lido por regex.
- Base lida com `git show`, comparação por conjuntos e o `dono` lido da config da **base**: um PR não se autoriza trocando o `dono` (teste `test_rotulo_do_novo_dono_da_pr_nao_vale`).
- Custo zero: só biblioteca padrão, sem chave e sem chamada paga.
- Mensagens no formato `<R-ID>: <o quê>. Por quê: ... Corrigir: ... (<doc>)`. Nunca imprimem valor de segredo.
- Renomear uma chave de `tests/config.json` ou mover o arquivo de um invariante aparece como remoção e barra, o que é conservador e está correto. Trocar o `command` de um hook também barra.
- Commits limpos, em Conventional Commits.

## Achados

### Bloqueia
1. **`tests/catraca.py:248-250` e `:222`: o "depois do último push" usa a data de commit do git, que pode ser forjada ou ficar antiga.** O `ultimo_push` é o maior `commit.committer.date` dos commits do PR (ou um `head_ref_force_pushed`). Essa data vem do cliente (`GIT_COMMITTER_DATE`, `git commit --date`) e não registra quando o commit chegou ao servidor. Dois caminhos fazem o rótulo continuar valendo para código que o dono não viu:
   - **Sem má-fé:** um commit criado às 10h e enviado às 11h, depois de o rótulo ser aplicado às 10h30.
   - **De propósito:** um agente envia um commit com data anterior ao rótulo.

   É justamente o caso que a camada 1 da ADR 0008 quer impedir: um agente contornando o portão. Comprovado: `rotulo_liberado` devolve `True` com o rótulo às 10:00 e o "push" declarado às 09:00.

   **Sugestão:** usar um instante do servidor para o head atual, por exemplo o `created_at` mais antigo de `GET /repos/{repo}/actions/runs?head_sha=<head.sha>` (permissão `actions: read`) ou de `GET /repos/{repo}/commits/<head.sha>/check-suites` (`checks: read`). Também vale guardar o `head.sha` como `HEAD_SHA` no `env` do job. Teste novo: commit com data anterior ao rótulo, mas com a execução do head posterior a ele, não libera.

2. **`tests/catraca.py:277-298` e `ci.yml:193-209`: o `pareceres` reprova toda promoção que carregue código sensível.** Em `develop` → `homolog`, `ramo` é `develop`, então o job exige review e QA com `branch: develop`. Em `homolog` → `main`, exige review com `branch: homolog`. Nada no processo produz esses pareceres para a `main`, e `docs/hooks.md:16` diz que a promoção é liberada pelo hook `parecer`. A próxima promoção desta própria mudança (que toca `ci.yml`) para a `main` fica vermelha.

   **Sugestão:** decidir e documentar. Recomendo:
   - (a) na base `main`, não exigir parecer novo, porque a `homolog` já cobrou;
   - (b) na base `homolog`, exigir QA e review do pedido de promoção com `branch: develop`, como em `docs/qa/release-0.5.0.md`, e registrar isso no `tech-lead` e em `docs/hooks.md`.

   Acrescentar teste para cada promoção.

### Recomendado (média)
3. **`ci.yml:152,184,205`: a base vem de `github.event.pull_request.base.sha`, mas o checkout é o merge commit (`refs/pull/N/merge`), montado sobre a ponta **atual** da base.** Se a base andou depois do evento, `merge-base(base.sha, HEAD)` devolve `base.sha` e o diff inclui commits de outros PRs já mesclados. O resultado são falsos positivos em `regra_protegidos`, `pareceres` e `segredos`, que usa `base...HEAD`.

   **Sugestão:** `BASE=$(git rev-parse HEAD^1)` (primeiro pai do merge commit) e, no `pareceres`, head = `HEAD^2`, ou o `HEAD_SHA` do evento.

4. **`tests/catraca.py:24` (`SENSIVEIS`) e `:145-169`: dá para esvaziar um teste sem a catraca nem o `pareceres` perceberem.** Os testes em `tests/*.py`, exceto `tests/catraca.py`, ficam fora das duas checagens. Basta trocar asserções por `pass`, acrescentar `@unittest.skip` ou passar a usar `lim.get("agente", 10**6)` em `tests/test_forge.py:966`. Também dá para remover cinco testes reais e criar cinco `def test_x(): pass`, porque a contagem fica igual. É o caminho mais curto para afrouxar uma regra protegida, e mudar a regex que lê `invariantes` também passa por aqui.

   **Sugestão:**
   - Incluir `tests/` em `SENSIVEIS`, para exigir parecer.
   - Na catraca, barrar o aumento de `skip`, `skipIf`, `skipUnless`, `expectedFailure` e `skipTest`.
   - Barrar qualquer diff em `tests/*.py` que não seja só acréscimo, ou exigir o rótulo nesse caso.

5. **`tests/catraca.py:327-336`: o rótulo `afrouxa-regra` libera também as violações de `R-CUSTO`.** A ADR dá ao custo outra exceção, a lista `custo_permitido`. Além disso, os padrões de custo diferenciam maiúsculas: GitHub Expressions não diferenciam, e `${{ tojson(secrets) }}` passa pela regra de custo (comprovado). Hoje esse caso só é pego como "mudança em workflow", que o rótulo libera.

   **Sugestão:**
   - Separar `R-CUSTO` da liberação por rótulo.
   - Usar `re.I` em `CUSTO`.
   - Trocar a parte de segredo por `\bsecrets\b(?!\.GITHUB_TOKEN\b)`.

6. **`ci.yml:139-155,193-209`: os jobs `catraca` e `pareceres` executam a versão do PR de `tests/catraca.py` e de `bin/forge-check`.** Um PR que muda a catraca pode tirar dela a regra que barra mudar a catraca. A ADR aceita esse limite para o `ci.yml`, mas, para os scripts, há uma correção barata.

   **Sugestão:** rodar a versão da base com `git show "$BASE:tests/catraca.py" > "$RUNNER_TEMP/catraca.py"` e o mesmo para `bin/forge-check`, voltando à versão do head só quando a base ainda não tem o arquivo, que é a introdução.

7. **`.github/dependabot.yml`, sem `target-branch`: os PRs do dependabot vão para a branch padrão.** Lá o `fluxo` falha, o que já acontecia antes. Mesmo indo para a `develop`, a troca de SHA em `ci.yml` exige o rótulo (`regra_protegidos`) e um parecer com `branch: dependabot/...`, que ninguém escreve. O `pr-texto` já os exclui.

   **Sugestão:** `target-branch: develop` e decidir o rito: rótulo do dono mais parecer do `tech-lead` na própria branch, ou isenção do `pareceres` para `dependabot[bot]` só quando o diff for troca de SHA de ação.

8. **Desvios da ADR 0008 sem registro como pendência no `CHANGELOG.md:7`:**
   - "revisor diferente do autor" não é conferido (`bin/forge-check` não compara);
   - a linha "Hooks que engordam" (linhas de `hooks/*.py` e mediana de 100 ms por fixture) não foi implementada;
   - não há comentário único no PR.

   **Sugestão:** listar no CHANGELOG ao lado do job `workflows`, ou implementar.

### Baixa
9. **`ci.yml:149,181,202`:** `fetch-depth: 0` sem `persist-credentials: false` deixa o token em `.git/config` enquanto o código do PR roda. O token é só de leitura, mas o zizmor aponta isso (`artipacked`). Usar `persist-credentials: false` como no `pr-texto`.
10. **`ci.yml:6` e `:14-16`:** `labeled`, `unlabeled` e `edited` disparam o workflow inteiro, inclusive os dois `npm install` do Claude Code, e cancelam a execução anterior. Não custa dinheiro, mas consome a cota de minutos do repositório privado.

    **Sugestão:** colocar `if:` nos jobs pesados para pular quando `github.event.action` for `labeled`, `unlabeled` ou `edited`, ou mover `catraca` e `pr-texto` para um workflow próprio.
11. **`tests/catraca.py:23` (`PROTEGIDOS`):** ficam de fora `.githooks/`, `.github/dependabot.yml` e um eventual campo `hooks` em `.claude-plugin/plugin.json`, que poderia desviar o registro de hooks para longe de `hooks/hooks.json`. Avaliar a inclusão.
12. **`tests/catraca.py:106-110`:** remover uma chave de `limite_linhas` não é barrado, porque `lh.get(k, 0) > n` dá falso. Hoje o `KeyError` em `tests/test_forge.py:966` cobre esse caso por acaso. Tratar a ausência como violação, e o mesmo para `anti_duplicacao.palavras`.
13. **`tests/catraca.py:266-274`:** `pedidos_da_branch` repete a função de mesmo nome de `bin/forge-check` (`:219`), só que com parser próprio e lendo do disco em vez da ref. Isso fere a ADR 0002 (uma fonte). Reaproveitar a do `forge-check`, que já aceita `--ref`.
14. **`ci.yml:209`:** usar `--ramo="$HEAD_REF"`, com `=`, por robustez no argparse.

## Parecer
**Reprovado.** Os itens 1 e 2 bloqueiam: o primeiro torna a única exceção da catraca contornável e o segundo trava a promoção. Os itens 3 a 8 entram nesta mesma branch ou viram cartão com dono antes da promoção para a `homolog`. Os itens 9 a 14 ficam a critério do autor. Correções de lógica voltam ao autor; novo parecer sobre o commit corrigido.
