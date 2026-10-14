---
tipo: review
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: 2a2f10cb9de03b8c51f53535fcf1fc37dee64656
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Code review: `scripts/ci-local` (CI local enquanto o Actions está sem cota, decisão A do dono)

## Re-review da volta 2 (HEAD 2a2f10c)
Escopo: `git diff 0fb51fc..2a2f10c -- scripts/ci-local tests/test_ci_local.py docs/devops/ci-local.md CHANGELOG.md`. Os commits são b2f7adc (merge da `develop`), e901d63 (correção) e 2a2f10c (parecer de autor). O resto do diff do merge (`bin/forge-check`, `tests/test_forge.py`, `docs/reviews/anti-alucinacao-medicao.md`) veio da `develop` e não entra neste review.

### Conferido (execução real nesta worktree, HEAD 2a2f10c)
- `python3 -m unittest tests.test_ci_local -v`: **27 testes, OK** (0,17 s). Na volta 1 eram 19.
- Suíte completa: **não rodada**. O load estava em 9,95 (`uptime`, 16:43), acima do limite de 4 combinado. O resultado da suíte completa da volta 1 (567 OK em 935f2dc) não vale para este HEAD. Ela precisa rodar antes do merge.
- Sondagem do novo avaliador de `if:` (`$TMPDIR/sonda.py`, módulo carregado com `python3 -I`), com 16 entradas hostis:
  - O payload do B1 (`'\' == ' and 1 #'`) virou dois literais comparados e deu `False`. Nada foi executado.
  - Foram recusadas com `ValueError`: `${{ ... }}`, `!x`, `()`, `a == b == c`, aspas duplas, `#`, NUL, parêntese sobrando, `'x' || __import__` e `'a'' == 'a'`.
  - Sem `eval` em todo o arquivo.
  - `bash -e -c 'false | true'` sai 0 (ver B3).

### Bloqueantes da volta 1
- **B1 (`eval` do `if:`): resolvido.** O `eval` saiu. Entrou um tokenizador de regex com um grupo por token (`TOKEN_SE`, `scripts/ci-local:38`) e descida recursiva (`ou` → `e` → `comparacao` → `operando`). Sobra de texto ou token desconhecido levanta `ValueError`. Há teste de regressão com o payload original e com o `touch` de marca (`tests/test_ci_local.py:74`), e testes de precedência e de entrada malformada. Também não consegui quebrar a versão nova (ver sondagem). Mudou o comportamento de `if:` sem suporte: antes era `FALHOU`, agora é `PULADO` com `ausente=True`. Em job obrigatório isso continua `failure` (`scripts/ci-local:231`), e há teste para isso. Em `workflows`, que é opcional, não reprova. Isso é aceitável.
- **B2 (`pipefail`): retratado. O erro foi meu na volta 1, e a correção que ele induziu é o novo B3.** Afirmei que o GitHub roda `run:` com `bash --noprofile --norc -eo pipefail {0}`. Isso só vale quando o passo declara `shell: bash`. Sem `shell:`, que é o caso de todos os passos de `ci.yml` e `catraca.yml` (`grep shell .github/workflows/*.yml` não acha nenhuma chave `shell:`), o runner Linux usa `bash -e {0}`. Fonte: a tabela de `jobs.<job_id>.steps[*].shell` da documentação do GitHub Actions, linhas "unspecified" e "bash". Portanto `false | true` **passa** no Actions, e o `bash -e -c` da volta 1 era o comportamento fiel.

### Bloqueia (volta 2)
- **B3. `scripts/ci-local:10`, `:290`, `tests/test_ci_local.py:176-177`, `docs/devops/ci-local.md:26` e `CHANGELOG.md:8` afirmam um comportamento do GitHub que não existe.**
  - O problema: os cinco pontos dizem "como no GitHub (`-eo pipefail`)". Com isso, o portão local fica **mais estrito** que o CI. Uma pipeline com o lado esquerdo falhando reprova local e passa no Actions. É o caso de `ci.yml:119` (`git diff ... | wc -l`) com `$BASE` inválido, ou de um `cmd | head` futuro que leve SIGPIPE.
  - O impacto hoje é nulo: com `$BASE` válido, nenhum passo atual diverge.
  - Por que bloqueia: o propósito do script é fidelidade ao CI, e o texto que vai para o `CHANGELOG` e para o parecer de autor documenta uma premissa falsa sobre o Actions.
  - **Sugestão (escolha do autor, as duas resolvem):**
    - (a) Voltar a `["bash", "--noprofile", "--norc", "-e", "-c", script]`. O `--noprofile --norc` é inócuo em `-c` não interativo. Inverter o teste: `false | true` deve dar `OK`, com docstring citando o `bash -e {0}` do passo sem `shell:`. Corrigir os textos.
    - (b) Manter o `pipefail` como escolha deliberada mais estrita e trocar "como no GitHub" por "mais estrito que o CI (o GitHub usa `bash -e` em passo sem `shell:`)" nos cinco pontos, renomeando o teste.
  - Recomendo (a): fidelidade primeiro. Se um dia um passo declarar `shell: bash`, o aviso de `shell` (que já existe) avisa da divergência.

### Recomendados da volta 1
- **3 (chaves ignoradas): resolvido parcialmente, aceito.** Em vez de falhar o job, o script **avisa** em stderr (`avisos_do_workflow`) sobre `env`/`defaults` de workflow e de job e sobre `working-directory`/`shell`/`continue-on-error` de passo. Há teste para isso. Ressalva: o aviso não muda o status. O job `workflows` (`ci.yml:47`) dispara o aviso em toda execução, o que tende a ser ignorado. Ele é opcional e o passo de download é tratado como preparo, então não reprova.
- **4 (`HEAD^`/`HEAD~` restante): resolvido como aviso** (`avisos_do_script`, com teste). Mesma ressalva: não falha.
- **5 (cabeça × merge): resolvido por documentação** (docstring e `docs/devops/ci-local.md`: "atualize a branch com a base antes de rodar").
- **6 (`gh auth token` vazio, PR não `OPEN`): resolvido como aviso** (`scripts/ci-local:329-335`).
- **7 (teste de recusa fraco): resolvido.** Os testes cobrem o escape real, entradas malformadas e o token só no passo que o declara. O teste do `pipefail` cai no B3.

### Recomendados novos
- **N1. `scripts/ci-local:165`: chave `github.*` desconhecida vale `""` em silêncio.** Prova: `github.__class__ == ''` dá `True`, e `github.repository == 'x/y'` dá `False`. Se um workflow futuro condicionar um passo obrigatório a um contexto que o `contexto_do_pr` não conhece, o passo é pulado e o job sai `PULADO` sem ausência, ou seja, `success` (falso verde). Hoje todos os `if:` dos dois workflows usam só chaves conhecidas. **Sugestão:** `ValueError` quando a chave não estiver em `ctx`, mais um teste.
- **N2. `scripts/ci-local:270`: `RecursionError` escapa do `except ValueError`.** Prova: `"(" * 5000 + "'a'" + ")" * 5000` levanta `RecursionError`, e o processo cai com traceback. Não é falso verde (o `finally` limpa e nada é publicado), mas é falha sem motivo legível. **Sugestão:** limitar a profundidade ou capturar `RecursionError` como `ValueError`.
- **N3.** `if: ${{ ... }}`, forma válida no GitHub, é recusado. É o lado conservador (vira ausência), basta saber disso. Nenhum workflow atual usa essa forma.

### Para o `security-engineer` (aponto, não decido; `R-SEGURANCA`)
- **Conferido:** o token agora só chega aos passos que o declaram em `env:`. Em `scripts/ci-local:286`, `GITHUB_TOKEN`/`GH_TOKEN` saem do ambiente herdado. O `os.environ.update` global (`:343`) só põe `GITHUB_REPOSITORY`. O teste `test_token_so_chega_ao_passo_que_o_declara` prova isso com um `GITHUB_TOKEN` do usuário no ambiente. Os passos que precisam de `PR_NUMBER`/`HEAD_SHA`/`PR_AUTOR` (`catraca.yml:32-36`, `ci.yml:214-218`) os declaram em `env:`, então a retirada do `update` global não quebra nada.
- **Aberto:**
  - Os passos continuam herdando o resto do ambiente do usuário.
  - Um `gh` chamado dentro de um passo lê a credencial do usuário em `~/.config/gh` mesmo sem `GITHUB_TOKEN` no ambiente. O escopo dessa credencial é o do usuário, não o `contents: read` do Actions.
  - O status `ci-local` continua autodeclarado.

### O que precisa do dono
- Nada para este review. O PR não pede `afrouxa-regra` (não toca `PROTEGIDOS`). A decisão de tornar o `ci-local` check exigido continua com o dono.

### Parecer (volta 2)
**Reprovado** (ajustes necessários). Volta ao autor (`devops-engineer`) só o **B3**, volta 3 de 3. A correção é pequena: reverter para `bash -e` e inverter o teste, ou manter e corrigir os textos. N1 e N2 são recomendados. B1 está resolvido. Depois da correção: re-review sobre o novo HEAD, suíte completa com load abaixo de 4 e, em seguida, o review do `security-engineer`.

## Review da volta 1 (HEAD 935f2dc, parecer: reprovado)

Escopo: `scripts/ci-local`, `tests/test_ci_local.py`, `CHANGELOG.md`, `CONTRIBUTING.md` e `docs/devops/ci-local.md`, diff `origin/develop...935f2dc` (a1dc534..935f2dc). A branch saiu de `4bfeb25`, e a `develop` já avançou (`9095efa`). Antes do PR, traga a `develop` com merge.

### Conferido (execução real nesta worktree, HEAD 935f2dc)
- `python3 -m unittest discover -s tests`: **567 testes, OK** (351 s). `tests.test_ci_local`: 19 testes, OK.
- `scripts/validar-plugin.sh`: **Validation passed**.
- `python3 tests/catraca.py --base origin/develop` (modo `regras`): sai 0. O diff não toca nenhum caminho de `PROTEGIDOS` (`tests/catraca.py:37`), então **o PR não precisa do rótulo `afrouxa-regra`**. Ele toca `scripts/`, que está em `SENSIVEIS`: o job `pareceres` exige este parecer com `parecer: aprovado`.
- shellcheck não se aplica, porque o script é Python. Este repositório não tem `docs/engineering/praticas.md` com regras de ferramenta, então não há saída de comando de ferramenta a citar.

### O que está bom
- Os jobs vêm dos `run:` dos workflows do próprio PR, e nenhuma lógica do CI foi copiada para o script. As únicas adaptações são textuais e estão documentadas: `git rev-parse HEAD^1` vira o sha da base, e `/tmp/` vira `$RUNNER_TEMP/`.
- A limpeza está correta: `try/finally` faz `worktree remove --force`, depois `rmtree` e `worktree prune`. A limpeza roda também quando `sys.exit` é chamado dentro do `try`, e o `prune` recolhe as worktrees que os jobs criam em `$RUNNER_TEMP`.
- A política de status é conservadora: ferramenta ausente em job obrigatório vale `failure`, e `if:` fora do subconjunto aceito vale `FALHOU`, nunca passa em silêncio. Há teste de regressão para o `RUNNER_TEMP` por job.
- Só biblioteca padrão e custo zero (`R-CUSTO`). Nada em `.github/`. A entrada no CHANGELOG está em `## [Não publicado]`. O parecer de autor do devops lista o que fica de fora e aciona o `security-engineer`.
- Commits limpos, em Conventional Commits, em português.

### Achados

#### Bloqueia
1. **`scripts/ci-local:33` e `:127`: o `eval` do `if:` executa código arbitrário apesar da regex `SEGURA`.** O literal `'[^']*'` aceita barra invertida. Para a regex, `'\'` é um literal fechado. O Python lê `\'` como aspa escapada, e o texto que a regex tomou como "dentro do segundo literal" vira código. Prova, executada nesta worktree (imprimiu `EXECUTOU`):
   ```
   '\' == ' and [x for x in ().__class__.__base__.__subclasses__() if x.__name__ == "Popen"][0](["echo","EXECUTOU"]).wait() == 0 #'
   ```
   `{"__builtins__": {}}` não impede o escape por `__subclasses__`. O impacto prático é limitado: quem controla o workflow do PR já controla os `run:`. Mesmo assim, o comentário "validada acima" é falso, e a execução acontece no processo do `ci-local`, antes de qualquer filtro de passo. **Sugestão:** trocar o `eval` por um avaliador de tokens. São poucas linhas: tokenizar com uma regex que tenha um grupo por token, depois avaliar `==`/`!=` entre valores e `&&`/`||` com parênteses por descida recursiva. Se o autor mantiver o `eval`, no mínimo `'[^'\\]*'`, mais um teste de regressão com o payload acima.
2. **`scripts/ci-local:196`: falta `pipefail`, o que dá falso verde.** O GitHub roda `run:` em bash com `bash --noprofile --norc -eo pipefail {0}`. O script usa `bash -e -c`. Prova: o passo `false | true` dá `ok` no `ci-local`, e no Actions falha. Isso atinge o `ci.yml` de hoje: em `:119`, `git diff ... | wc -l` com `$BASE` inválido falha no CI e passa local com `0`. Um portão local que aprova o que o CI reprovaria é exatamente o defeito que ele precisa evitar. **Sugestão:** `["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", script]`, mais um teste com `false | true` esperando `FALHOU`.

#### Recomendado
3. **`scripts/ci-local:54-101`: o parser ignora em silêncio as chaves que mudam a execução.** São elas: `env:` de job e de workflow (o job `workflows` tem `env:` de job, em `ci.yml:47`), `defaults.run`, `working-directory`, `shell`, `continue-on-error` e `${{ }}` dentro de `run:`. Prova: um job com `env: X` e um passo com `working-directory: sub` saem do `ler_jobs` sem os dois campos. **Sugestão:** fazer o job `FALHOU` com "chave não suportada: <chave>" quando uma dessas chaves aparecer, como já acontece com o `if:` fora do subconjunto. Assim, uma mudança futura no workflow não diverge sem aviso.
4. **`scripts/ci-local:190`: a troca textual de `git rev-parse HEAD^1` é frágil.** Se o workflow passar a usar `HEAD^`, `HEAD~1` ou `git rev-parse HEAD^1 --verify`, o passo roda localmente contra o pai do commit da cabeça, sem aviso. **Sugestão:** depois da troca, se ainda restar `HEAD^` ou `HEAD~` no script, fazer o job falhar com motivo explícito.
5. **Fidelidade: o código testado é a cabeça do PR, não o merge com a base.** O CI testa o merge commit (cabeça + base atual). O `ci-local` testa só a cabeça, e com a base no merge-base. Os diffs dos jobs batem com os do CI quando não há conflito. Já os testes e a catraca (que lê o `tests/config.json` da base) podem divergir quando a base avançou. O `docs/devops/ci-local.md` cita o merge-base, mas não diz que a árvore testada não inclui a base nova. **Sugestão:** documentar e exigir, no fluxo, a branch atualizada com a base antes de rodar. Outra opção é montar o merge localmente (`git merge --no-commit` na worktree destacada) e falhar em caso de conflito.
6. **`scripts/ci-local:235`: falha do `gh auth token` passa em silêncio.** O token fica vazio, e a catraca falha mais adiante com uma mensagem que não aponta a causa. **Sugestão:** sair com mensagem clara quando o token estiver vazio. Ainda na entrada: avisar ou recusar quando `state` não for `OPEN`.
7. **`tests/test_ci_local.py:70-72`: o teste de recusa cobre só o caso óbvio.** Faltam o escape do item 1 e o `pipefail` do item 2. Pela regra 11 do checklist, o teste de ausência precisa cobrir o caso que de fato fura a regra.

#### Para o `security-engineer` (aponto, não decido; `R-SEGURANCA`)
- `scripts/ci-local:243`: `os.environ.update({"GITHUB_TOKEN": token, ...})` põe o token do `gh` do usuário (com o escopo dele, não o `contents: read` do Actions) no ambiente de **todos** os passos. No CI, só o passo da catraca recebe o token (`catraca.yml:33`). Além disso, os passos herdam o ambiente inteiro do usuário, menos `GIT_*`. O item 1 também é dele: código no `if:` roda no processo do `ci-local`, que tem o token.
- O status `ci-local` publicado é autodeclarado. Torná-lo check exigido é decisão do dono (`R-CONFORMIDADE`), como o parecer de autor já registra.

### O que precisa do dono
- Nada para este review. O PR não pede `afrouxa-regra`. A decisão de transformar o `ci-local` em check exigido continua com o dono.

### Parecer
**Reprovado** (ajustes necessários). Os itens 1 e 2 voltam ao autor (`devops-engineer`), cada um com teste de regressão. Os itens 3 a 7 são recomendados. Depois da correção, novo review sobre o novo HEAD e, em seguida, o review do `security-engineer`.
