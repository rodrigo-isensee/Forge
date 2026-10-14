---
tipo: review
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: 935f2dcb8fd3f30dbd94cdeff9b41302975bff5c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Code review: `scripts/ci-local` (CI local enquanto o Actions está sem cota, decisão A do dono)

Escopo: `scripts/ci-local`, `tests/test_ci_local.py`, `CHANGELOG.md`, `CONTRIBUTING.md` e `docs/devops/ci-local.md`, diff `origin/develop...935f2dc` (a1dc534..935f2dc). A branch saiu de `4bfeb25`, e a `develop` já avançou (`9095efa`). Antes do PR, traga a `develop` com merge.

## Conferido (execução real nesta worktree, HEAD 935f2dc)
- `python3 -m unittest discover -s tests`: **567 testes, OK** (351 s). `tests.test_ci_local`: 19 testes, OK.
- `scripts/validar-plugin.sh`: **Validation passed**.
- `python3 tests/catraca.py --base origin/develop` (modo `regras`): sai 0. O diff não toca nenhum caminho de `PROTEGIDOS` (`tests/catraca.py:37`), então **o PR não precisa do rótulo `afrouxa-regra`**. Ele toca `scripts/`, que está em `SENSIVEIS`: o job `pareceres` exige este parecer com `parecer: aprovado`.
- shellcheck não se aplica, porque o script é Python. Este repositório não tem `docs/engineering/praticas.md` com regras de ferramenta, então não há saída de comando de ferramenta a citar.

## O que está bom
- Os jobs vêm dos `run:` dos workflows do próprio PR, e nenhuma lógica do CI foi copiada para o script. As únicas adaptações são textuais e estão documentadas: `git rev-parse HEAD^1` vira o sha da base, e `/tmp/` vira `$RUNNER_TEMP/`.
- A limpeza está correta: `try/finally` faz `worktree remove --force`, depois `rmtree` e `worktree prune`. A limpeza roda também quando `sys.exit` é chamado dentro do `try`, e o `prune` recolhe as worktrees que os jobs criam em `$RUNNER_TEMP`.
- A política de status é conservadora: ferramenta ausente em job obrigatório vale `failure`, e `if:` fora do subconjunto aceito vale `FALHOU`, nunca passa em silêncio. Há teste de regressão para o `RUNNER_TEMP` por job.
- Só biblioteca padrão e custo zero (`R-CUSTO`). Nada em `.github/`. A entrada no CHANGELOG está em `## [Não publicado]`. O parecer de autor do devops lista o que fica de fora e aciona o `security-engineer`.
- Commits limpos, em Conventional Commits, em português.

## Achados

### Bloqueia
1. **`scripts/ci-local:33` e `:127`: o `eval` do `if:` executa código arbitrário apesar da regex `SEGURA`.** O literal `'[^']*'` aceita barra invertida. Para a regex, `'\'` é um literal fechado. O Python lê `\'` como aspa escapada, e o texto que a regex tomou como "dentro do segundo literal" vira código. Prova, executada nesta worktree (imprimiu `EXECUTOU`):
   ```
   '\' == ' and [x for x in ().__class__.__base__.__subclasses__() if x.__name__ == "Popen"][0](["echo","EXECUTOU"]).wait() == 0 #'
   ```
   `{"__builtins__": {}}` não impede o escape por `__subclasses__`. O impacto prático é limitado: quem controla o workflow do PR já controla os `run:`. Mesmo assim, o comentário "validada acima" é falso, e a execução acontece no processo do `ci-local`, antes de qualquer filtro de passo. **Sugestão:** trocar o `eval` por um avaliador de tokens. São poucas linhas: tokenizar com uma regex que tenha um grupo por token, depois avaliar `==`/`!=` entre valores e `&&`/`||` com parênteses por descida recursiva. Se o autor mantiver o `eval`, no mínimo `'[^'\\]*'`, mais um teste de regressão com o payload acima.
2. **`scripts/ci-local:196`: falta `pipefail`, o que dá falso verde.** O GitHub roda `run:` em bash com `bash --noprofile --norc -eo pipefail {0}`. O script usa `bash -e -c`. Prova: o passo `false | true` dá `ok` no `ci-local`, e no Actions falha. Isso atinge o `ci.yml` de hoje: em `:119`, `git diff ... | wc -l` com `$BASE` inválido falha no CI e passa local com `0`. Um portão local que aprova o que o CI reprovaria é exatamente o defeito que ele precisa evitar. **Sugestão:** `["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", script]`, mais um teste com `false | true` esperando `FALHOU`.

### Recomendado
3. **`scripts/ci-local:54-101`: o parser ignora em silêncio as chaves que mudam a execução.** São elas: `env:` de job e de workflow (o job `workflows` tem `env:` de job, em `ci.yml:47`), `defaults.run`, `working-directory`, `shell`, `continue-on-error` e `${{ }}` dentro de `run:`. Prova: um job com `env: X` e um passo com `working-directory: sub` saem do `ler_jobs` sem os dois campos. **Sugestão:** fazer o job `FALHOU` com "chave não suportada: <chave>" quando uma dessas chaves aparecer, como já acontece com o `if:` fora do subconjunto. Assim, uma mudança futura no workflow não diverge sem aviso.
4. **`scripts/ci-local:190`: a troca textual de `git rev-parse HEAD^1` é frágil.** Se o workflow passar a usar `HEAD^`, `HEAD~1` ou `git rev-parse HEAD^1 --verify`, o passo roda localmente contra o pai do commit da cabeça, sem aviso. **Sugestão:** depois da troca, se ainda restar `HEAD^` ou `HEAD~` no script, fazer o job falhar com motivo explícito.
5. **Fidelidade: o código testado é a cabeça do PR, não o merge com a base.** O CI testa o merge commit (cabeça + base atual). O `ci-local` testa só a cabeça, e com a base no merge-base. Os diffs dos jobs batem com os do CI quando não há conflito. Já os testes e a catraca (que lê o `tests/config.json` da base) podem divergir quando a base avançou. O `docs/devops/ci-local.md` cita o merge-base, mas não diz que a árvore testada não inclui a base nova. **Sugestão:** documentar e exigir, no fluxo, a branch atualizada com a base antes de rodar. Outra opção é montar o merge localmente (`git merge --no-commit` na worktree destacada) e falhar em caso de conflito.
6. **`scripts/ci-local:235`: falha do `gh auth token` passa em silêncio.** O token fica vazio, e a catraca falha mais adiante com uma mensagem que não aponta a causa. **Sugestão:** sair com mensagem clara quando o token estiver vazio. Ainda na entrada: avisar ou recusar quando `state` não for `OPEN`.
7. **`tests/test_ci_local.py:70-72`: o teste de recusa cobre só o caso óbvio.** Faltam o escape do item 1 e o `pipefail` do item 2. Pela regra 11 do checklist, o teste de ausência precisa cobrir o caso que de fato fura a regra.

### Para o `security-engineer` (aponto, não decido; `R-SEGURANCA`)
- `scripts/ci-local:243`: `os.environ.update({"GITHUB_TOKEN": token, ...})` põe o token do `gh` do usuário (com o escopo dele, não o `contents: read` do Actions) no ambiente de **todos** os passos. No CI, só o passo da catraca recebe o token (`catraca.yml:33`). Além disso, os passos herdam o ambiente inteiro do usuário, menos `GIT_*`. O item 1 também é dele: código no `if:` roda no processo do `ci-local`, que tem o token.
- O status `ci-local` publicado é autodeclarado. Torná-lo check exigido é decisão do dono (`R-CONFORMIDADE`), como o parecer de autor já registra.

## O que precisa do dono
- Nada para este review. O PR não pede `afrouxa-regra`. A decisão de transformar o `ci-local` em check exigido continua com o dono.

## Parecer
**Reprovado** (ajustes necessários). Os itens 1 e 2 voltam ao autor (`devops-engineer`), cada um com teste de regressão. Os itens 3 a 7 são recomendados. Depois da correção, novo review sobre o novo HEAD e, em seguida, o review do `security-engineer`.
