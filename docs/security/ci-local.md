---
tipo: revisao-seguranca
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: 27d86b505ee4564f7cbfa0e293297e420affb2f6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: ci-local

> **Revalidação (27d86b5): aprovado mantido; ver a seção no fim.** **Re-review (18aa46c): aprovado.** O A1 foi corrigido, e os recomendados A2, C1 e D também. Veja a seção "Re-review" no fim. O texto abaixo, até ela, é o parecer original sobre 083bb7b e fica como histórico.

Escopo: `scripts/ci-local` (HEAD 083bb7b), `docs/devops/ci-local.md` (seção Segurança) e os riscos que o review do `tech-lead` passou a este papel (`docs/reviews/ci-local.md`). A revisão foi estática, com sondas locais num diretório descartável em `$TMPDIR`. Nada foi publicado, o `--publicar` não rodou e o código não foi alterado.

## Gatilhos
- **Segredos e credenciais:** o script lê a credencial do `gh` do usuário (`scripts/ci-local:340`) e a entrega aos passos (`:120`, `:296`).
- **CI/CD:** o script executa localmente os `run:` de `.github/workflows/ci.yml` e `catraca.yml`, tal como estão na cabeça do PR (`:355-364`).

## Veredito
**Reprovado.** Um achado bloqueia (A1), e a correção custa pouco (P). O avaliador de `if:` passou em todas as sondas (B). Os demais achados ficam como recomendações, ou viram condição para uma decisão futura do dono (D).

Modelo de confiança, em uma frase: o `ci-local` lê os workflows **e** o código da cabeça do PR e os executa com os privilégios de quem o roda. É o equivalente local de `pull_request_target` com checkout da cabeça. Quem controla o PR controla o que roda, inclusive os `env:` dos passos. Só um portão **antes** da execução protege de verdade. Os filtros aplicados durante a execução só reduzem vazamento acidental.

## Achados

### A1. Falta o portão de confiança, e a documentação afirma uma mitigação que não existe (média; alta se o repositório ficar público). **Bloqueia.**
- **Evidência:** `docs/devops/ci-local.md:36` lista "só PRs do próprio repositório" entre as mitigações atuais. O script não faz essa verificação: `scripts/ci-local:326` não pede `isCrossRepository` nem `headRepositoryOwner`, e `:331` busca `pull/<n>/head`, que também traz PR de fork. O comentário em `scripts/ci-local:293` diz que o token do usuário "não vaza para os demais" passos. Isso só vale para a variável de ambiente (ver A2).
- **Caminho de ataque:** alguém com acesso de leitura ao repositório abre um PR a partir de um fork. Num repositório privado, isso inclui quem consegue fazer fork. O PR altera um `run:` ou um teste para ler `gh auth token` (a credencial em disco, fora do sandbox), ou declara `env: X: ${{ github.token }}` em qualquer passo. O mantenedor roda `scripts/ci-local <n>`. O token do usuário, com o escopo inteiro dele (e não o `contents: read` do Actions), sai pela rede. Com esse token, o atacante pode escrever no repositório e nos workflows. Hoje o repositório responde 404 à API sem autenticação, o que indica que é privado, e por isso a severidade é média. Se ele ficar público, a severidade vira alta.
- **Correção mínima (dono: `devops-engineer`; esforço P):**
  1. Pedir `isCrossRepository,headRepositoryOwner` em `:326`. Se `isCrossRepository` for verdadeiro, **recusar** com saída diferente de 0, a menos que venha a flag explícita `--confiar`. Com `--confiar`, imprimir um aviso dizendo que o código do PR vai rodar com a credencial do usuário. Num PR do próprio repositório, a branch da cabeça só pode receber push de quem tem permissão de escrita, e isso basta como prova de autor confiável.
  2. Corrigir `docs/devops/ci-local.md:36` e o comentário de `scripts/ci-local:293` para dizerem o que de fato vale: o filtro remove o token das variáveis de ambiente, mas não impede o `gh` de usar a credencial em disco, e o PR controla os próprios `env:`.
  3. Adicionar um teste de regressão: PR com `isCrossRepository: true` e sem `--confiar` sai com código diferente de 0 antes de criar a worktree.

### A2. Os passos herdam o ambiente inteiro do usuário (média; recomendado, não bloqueia)
- **Evidência:** `scripts/ci-local:294` copia todo o `os.environ`, menos `GIT_*`, `GITHUB_TOKEN` e `GH_TOKEN`. Sonda: um passo sem `env:` rodou `env | cut -d= -f1` e viu duas variáveis com nome de credencial da sessão (um `*_PASSWORD` de proxy e um `*_TOKEN` de mensageria; só os nomes foram lidos, nunca os valores). As variáveis `GIT_*`, `GITHUB_TOKEN` e `GH_TOKEN` foram removidas, como prometido. Na mesma sonda, `gh auth token` dentro do passo falhou, mas só porque o sandbox desta sessão bloqueia a leitura da configuração do `gh`. No terminal do usuário, fora do sandbox, o `gh` lê a credencial em disco (ou no chaveiro) e o filtro não a alcança.
- **Caminho de ataque:** é o mesmo do A1. Com o portão do A1, sobra um colaborador de escrita mal-intencionado, ou uma conta dele comprometida. Esse risco é residual.
- **Correção mínima (dono: `devops-engineer`; esforço P):** trocar a lista negra por uma lista branca: `PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `LANG`, `LC_*`, `TERM`, `TMPDIR`, `TZ`, mais as variáveis que o script define (`RUNNER_TEMP`, `GITHUB_STEP_SUMMARY`, `CI`, `GITHUB_REPOSITORY`) e o `env:` do passo. Isso não fecha a credencial em disco: sob `HOME`, o `gh` continua lendo a dele. A defesa contra isso é o A1.

### A3. O token entregue tem escopo maior que o do CI (baixa; recomendado)
- **Evidência:** `scripts/ci-local:120` põe em `github.token` o token do `gh auth token`. No CI, o mesmo `${{ github.token }}` (`.github/workflows/catraca.yml:33`) vale `contents: read`.
- **Caminho de ataque:** é o do A1. O passo que declara o token recebe o escopo do usuário. A restrição "só nos passos que o declaram" funciona contra vazamento acidental, mas não contra um PR mal-intencionado, porque é o próprio PR que escreve os `env:`.
- **Correção mínima (dono: `devops-engineer`; esforço P):** aceitar um token dedicado por variável (por exemplo, um token de granularidade fina, só leitura, só neste repositório). Quando ele não existir, cair no `gh auth token` com um aviso. Documentar no `docs/devops/ci-local.md`.

### B. Avaliador de `if:` sem `eval`: sem achado (informativa)
- **Evidência:** `scripts/ci-local:38` (um token por grupo) e `:141-205` (descida recursiva). Não há `eval`, `exec` nem shell no caminho do `if:`.
- **Sondas** (o módulo foi carregado por caminho, com `python3 -I`, e cada sonda mediu resultado e tempo):

| Entrada | Resultado |
|---|---|
| payload de escape da volta 1 (`'\' == ' and [... __subclasses__() ...] #'`) | `False`, como comparação de dois literais; nada executou |
| `__import__('os').system(...)` | `ValueError` (token inesperado) |
| `'a' == 'a' ; touch <arquivo>` | `ValueError`; o arquivo não foi criado |
| `${{ github.token }}`, `contains(...)`, `always()`, `!(...)` | `ValueError`: o job fica pulado por falta de suporte e conta como falha se for obrigatório |
| `github.__class__` | `ValueError` (contexto desconhecido) |
| 5.000 parênteses aninhados | `ValueError` (aninhada demais), sem `RecursionError` solto |
| aspa aberta seguida de 400 mil aspas | `ValueError` em 0,02 s, sem retrocesso catastrófico |
| 50 mil `&&` | `True` em 1,2 s; o custo é linear e aceitável |
| `'a' == 'a' == 'b'` | `ValueError` (sobra de texto) |

- **Achado relacionado, sem caminho de ataque:** `expandir` (`:229-230`) põe o corpo do PR, que é controlado pelo autor, só como **valor** de variável de ambiente. Os textos de `run:` não passam por `${{ }}`. Sonda: um corpo com `$(touch ...)` e crases chegou ao passo como texto literal e nada executou. É mais seguro que o Actions, onde `${{ }}` dentro de `run:` gera injeção.

### C. Worktree temporária (baixa; recomendado, não bloqueia)
- **Caminho previsível: não.** `scripts/ci-local:348` usa `tempfile.mkdtemp`, com nome aleatório e modo `700` (conferido na sonda). Não há corrida de nome nem pré-criação por outro usuário.
- **Limpeza:** `:365-368` (`worktree remove --force`, `rmtree`, `worktree prune`) roda no `finally`, inclusive com `sys.exit` e Ctrl-C. O `shutil.rmtree` desta versão do Python resiste a symlink (`avoids_symlink_attacks = True`, conferido). Sonda: um symlink dentro da worktree apontando para fora foi removido sem tocar no alvo.
- **C1, symlink no workflow (baixa):** `:356-360` faz `read_text` em `.github/workflows/<arquivo>` da cabeça do PR e segue symlink. Sonda: um repositório descartável com `ci.yml` como symlink para um arquivo fora da árvore levou a worktree a ler o conteúdo do alvo. O impacto é baixo, porque o código do PR já roda com os mesmos privilégios, mas a leitura acontece **antes** de qualquer portão. **Correção (P):** se `caminho.is_symlink()`, tratar como "workflow ausente", o que vira `failure`.
- **C2, persistência e processos órfãos (baixa, informativa):** a worktree compartilha o diretório comum do `.git` do clone do usuário. Um passo pode gravar ganchos ou configuração ali, e o efeito sobrevive à limpeza e roda na próxima operação git do usuário. Além disso, o `timeout` de `:301-303` mata só o `bash` direto: processos em segundo plano que o passo lança continuam vivos depois da limpeza. As duas coisas são consequência do A1 (o código do PR já roda como o usuário), e o portão do A1 é a defesa. **Melhoria opcional (P):** `start_new_session=True` em `rodar` e `os.killpg` no timeout e no fim de cada passo. Registrar a persistência no `docs/devops/ci-local.md`.

### D. Status `ci-local` autodeclarado com `--publicar` (média se virar check exigido; hoje informativa; não bloqueia)
- **Evidência:** `scripts/ci-local:372-377` publica `state` e `description` no sha da cabeça com a credencial do usuário. Nada liga o status a uma execução: qualquer conta com escrita publica `success` em `context=ci-local` com uma única chamada à API, sem rodar nada. Além disso, os jobs vêm dos workflows **do próprio PR** (`:356`). Um PR que esvazia os `run:` (inclusive o da catraca) recebe `success` das próprias regras. O status é publicado na cabeça, mas foi medido sem o merge com a base (`:12`).
- **Caminho de ataque:** se o dono tornar `ci-local` um check exigido, um colaborador com escrita satisfaz o portão sem passar pela bateria. Enquanto o check não for exigido, isso não tem efeito.
- **O que o texto deve dizer** (`docs/devops/ci-local.md:33` e a ajuda do `--publicar`; dono: `devops-engineer`; esforço P): (1) o status é autodeclarado e não prova que a bateria rodou; (2) os workflows executados são os do PR, sem merge com a base; (3) o status não substitui o CI nem a revisão; (4) torná-lo check exigido é decisão do dono (`R-CONFORMIDADE`) e, se isso acontecer, primeiro o `--publicar` precisa recusar PR que altera `.github/workflows/` ou `tests/catraca.py` (ou ler esses arquivos da base). Sugestão para a `description`: um prefixo fixo, como `local, cabeça sem merge: <n> ok / <n> falharam`.

## O que bloqueia
Bloqueia só o **A1**: o portão `isCrossRepository` com `--confiar`, a correção do texto em `docs/devops/ci-local.md:36` e do comentário em `scripts/ci-local:293`, e o teste de regressão. A2, A3, C1 e o texto do D são recomendados, e cada um custa P. A2 e o texto do D cabem na mesma volta. O D passa a bloquear se o dono decidir tornar o `ci-local` um check exigido.

## Casos de abuso para o `qa-engineer`
1. PR de fork sem `--confiar`: sai com código diferente de 0 e não cria worktree.
2. Passo sem `env:` imprime os nomes das variáveis: nenhum nome fora da lista branca aparece (depois do A2).
3. `ci.yml` como symlink: o job fica `workflow ausente` e o resultado é `failure` (depois do C1).
4. `if:` com o payload de escape da volta 1: o resultado é `False`, sem efeito colateral (já coberto pelo avaliador; manter o teste).

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum. Nenhum aceite foi pedido.
- Ferramentas: `python3 -I` com sondas locais em `$TMPDIR`. `shellcheck` está no PATH, mas não se aplica, porque o script é Python. **Lacunas no ambiente:** `gitleaks`, `semgrep`, `zizmor` e `actionlint` não estão no PATH. Não foram instaladas (`R-CUSTO`), e os workflows não mudaram neste PR.
- Suposição: o repositório é privado, inferido pelo 404 da API sem autenticação. A severidade do A1 depende disso.

## Re-review (commit 18aa46c)
Escopo: `git diff 2d8ea23..18aa46c -- scripts/ci-local tests/test_ci_local.py docs/devops/ci-local.md` (commit de correção a86a0bc e a volta 3 em `docs/devops/ci-local.md`). O código não foi alterado e nada foi publicado.

**Veredito: aprovado.** O A1, que bloqueava, está corrigido. A2, C1 e D (o texto e a recusa) também. A3 e C2 continuam recomendados e fora desta volta, como registra a volta 3.

### O que mudou e onde
- **A1:** `scripts/ci-local` passa a pedir `isCrossRepository,headRepositoryOwner` ao `gh pr view` em `main`. `recusar_fork` roda antes de qualquer `git fetch` e antes da worktree, e sai com código diferente de 0 se faltar `--confiar`. Com `--confiar`, avisa que a credencial fica exposta. O comentário enganoso do antigo `:293` saiu. O `docs/devops/ci-local.md` (seção Segurança) agora descreve o modelo de confiança como ele é e não afirma mitigação que não existe.
- **A2:** `ambiente_minimo` aplica a lista branca (`ENV_PERMITIDO` mais `LC_*`). Ficam de fora `GIT_*`, `GH_TOKEN`, `GITHUB_TOKEN` e qualquer outra variável do usuário.
- **C1:** `ler_workflow` devolve `None` para symlink ou arquivo ausente, e o job vira "ausente (ou symlink)", que conta como falha se for obrigatório.
- **D:** `recusar_publicacao` roda antes da worktree e antes do `gh auth token`, e recusa o `--publicar` quando o diff `merge-base..cabeça` toca `.github/workflows/` ou `tests/catraca.py`. A ajuda do `--publicar` e o `docs/devops/ci-local.md` dizem que o status é **autodeclarado**, que usa os workflows do PR, que mede a cabeça sem merge com a base e que não substitui o CI nem a revisão.
- **Testes:** `PortoesDeSegurancaTest` em `tests/test_ci_local.py` cobre os quatro casos de abuso do parecer original. `python3 -m unittest tests.test_ci_local`: 41 testes OK.

### Sondas (repositório descartável em `$TMPDIR`)
Montagem: um repositório nu como `origin`, a cabeça do PR empurrada para `refs/pull/7/head` e um `gh` **simulado** no início do `PATH`, que registra cada chamada e responde a `pr view`, `repo view`, `auth token` e `api` sem rede. O `ci.yml` de sonda tem dois passos: um grava só os **nomes** das variáveis de ambiente (`env | cut -d= -f1`) e o outro declara `TOKEN: ${{ github.token }}`. O ambiente de quem roda recebeu variáveis fictícias com nome de credencial (`SONDA_CRED_TOKEN`, `SONDA_PROXY_PASSWORD`, `GH_TOKEN`, `GITHUB_TOKEN` e `GIT_SONDA`, todas com valor falso). Nenhum valor real foi lido.

| Sonda | rc | Efeito |
|---|---|---|
| A1: PR de fork (`isCrossRepository: true`) sem `--confiar` | 1 | Recusado com "o PR vem de um fork". Não houve `git fetch` (sem `FETCH_HEAD`), não houve worktree e nenhum passo rodou (nenhum arquivo de sonda criado) |
| A1: o mesmo PR com `--confiar` | 0 | O aviso "o código do PR de fork de 'terceiro' vai rodar ... com a credencial do gh em disco" aparece em stderr, e a bateria roda |
| A2: PR do mesmo repositório, passo sem `env:` de credencial | 0 | O passo viu só `CI GITHUB_REPOSITORY GITHUB_STEP_SUMMARY HOME LANG LOGNAME PATH RUNNER_TEMP SHELL TERM TMPDIR USER`, o `env:` do próprio passo e as variáveis que o `bash` cria (`PWD`, `SHLVL`, `_`). Nenhum `SONDA_CRED_*`, `SONDA_PROXY_*`, `GH_TOKEN`, `GITHUB_TOKEN` ou `GIT_*`. O token só chegou ao passo que o declarou |
| C1: `ci.yml` como symlink para um workflow fora da árvore | 1 | `ci.yml PULADO (obrigatório: conta como falha) (workflow ausente (ou symlink))`. O alvo do link não foi lido: a marca que ele criaria não existe. O resultado é `failure` |
| D: `--publicar` com `.github/workflows/ci.yml` alterado | 1 | "--publicar recusado: o PR altera a própria bateria". 0 chamadas a `gh api` e nenhum passo rodou |
| D: `--publicar` com `tests/catraca.py` alterado | 1 | Recusado, com 0 chamadas a `gh api` |
| D: `--publicar` com workflow novo em `.github/workflows/` | 1 | Recusado, com 0 chamadas a `gh api` |
| D, controle: `--publicar` com só o `README` alterado | 0 | Passa do portão e chama o `gh api` **simulado** (`POST .../statuses/<sha>`). Isso mostra que a recusa não é incondicional |

### Observações novas (informativas, não bloqueiam)
- **D1, renomeação e falha do `git diff` (informativa):** `recusar_publicacao` usa `git diff --name-only`, que detecta renomeação e só lista o caminho novo. Sonda: renomear `tests/catraca.py` para `tests/outro.py` passou do portão (rc 1, `gh api` simulado chamado com `state=failure`). Não é desvio, porque sem o arquivo a catraca falha e o status sai `failure`, nunca `success`. Pelo mesmo motivo, renomear `ci.yml` para fora deixa o workflow ausente, e isso vira falha. Também não se confere o `returncode` do `git diff`: se ele falhar, a lista vem vazia e o portão abre. Hoje esse caso é improvável, porque o `sha` e a `base` já foram verificados antes. **Melhoria opcional (P, dono `devops-engineer`):** `git diff --name-only --no-renames -z` e sair com erro se o `returncode` for diferente de 0.
- **D2, o alcance do portão D é só a bateria literal (informativa):** o PR ainda pode mudar o que os workflows chamam (os testes em `tests/`, scripts). Isso é o mesmo que o CI faz com `pull_request`, e o texto já diz que o status é autodeclarado. Só importa se o dono quiser tornar o `ci-local` um check exigido, e aí volta a ser decisão dele (`R-CONFORMIDADE`).

### O que segue em aberto
- A3 (token de escopo fino) e C2 (`killpg` e a persistência no `.git` comum): recomendados, fora desta volta. Os dois estão documentados como limitação em `docs/devops/ci-local.md`.
- Pela decisão do dono, o `ci-local` não é check exigido. O resultado vai no PR só como evidência. Se isso mudar, o D, junto com D1 e D2, precisa de nova revisão.
- Riscos aceitos: nenhum. Ferramentas: `python3` e sondas locais. Seguem as mesmas lacunas no PATH (`gitleaks`, `semgrep`, `zizmor`, `actionlint`), e nenhuma ferramenta foi instalada (`R-CUSTO`).

## Revalidação no head (commit 27d86b5)
Escopo: `git diff 5072e69..27d86b5 -- scripts/ci-local tests/test_ci_local.py`, que fecha o D1 (observação do re-review): `arquivos_alterados()` usa `git diff --name-only --no-renames -z` e sai com erro se o `returncode` for diferente de 0, mais 3 testes. O código não foi alterado e nada foi publicado.

**Veredito: parecer mantido, aprovado.** O fechamento do D1 não abre nada novo. O `-z` também fecha um desvio que o D1 não citava: sem ele, o git coloca entre aspas o nome com quebra de linha, e a lista deixaria de começar com `.github/workflows/`.

Sondas: repositório descartável em `$TMPDIR` (origin nu, cabeça em `refs/pull/7/head`), `gh` simulado no `PATH` que registra as chamadas, e `scripts/ci-local 7 --publicar` de ponta a ponta. Para o item 2, um shim de `git` no `PATH` devolve rc 128 só no subcomando `diff`. Os valores de rc abaixo são do script. Nas linhas de controle, o rc 1 vem da bateria do workflow mínimo da sonda; o que importa ali é o portão ter aberto.

| Sonda | rc | Efeito |
|---|---|---|
| Renomear `tests/catraca.py` para `tests/outro.py` | 1 | "--publicar recusado: o PR altera a própria bateria (tests/catraca.py)". 0 chamadas a `gh api` (em 5072e69 passava do portão) |
| `git diff` falha (rc 128 simulado) | 1 | "--publicar recusado: o git diff falhou (rc 128)". 0 chamadas a `gh api`; falha fechada |
| Arquivo `.github/workflows/x<LF>y.yml` (quebra de linha no nome) | 1 | Recusado, com o nome inteiro em `tocados`. 0 chamadas a `gh api`. O `-z` entrega a entrada sem aspas |
| `docs/a<LF>.github/workflows/z` (uma entrada só, que não começa em `.github/workflows/`) | 1 | Não recusado, e está certo: é um arquivo de `docs/`, e a quebra de linha não vira duas entradas. 1 chamada a `gh api` (o portão abriu) |
| Controle: só o `README` alterado | 1 | Portão aberto, 1 chamada a `gh api` simulada. A recusa não é incondicional |

Leitura do diff: a lista é separada por NUL, e `if a` descarta só a entrada vazia final. O `rodar` não usa shell. `base` e `sha` vêm do `gh` e do `git` já verificados antes, e vão como argumentos separados. Não há `eval`. O teste `test_publicar_recusa_no_fluxo_principal_antes_de_rodar_a_bateria` foi ajustado para a saída com NUL.

Continuam como estavam: A3, C2 e D2, informativos e registrados. Pela decisão do dono (decisão A), o `ci-local` não é check exigido; se virar, o D, o D2 e o A3 precisam de nova revisão (`R-CONFORMIDADE`). Riscos aceitos: nenhum. Ferramentas: `python3` e sondas locais; seguem as lacunas `gitleaks`, `semgrep`, `zizmor` e `actionlint` no PATH, e nada foi instalado (`R-CUSTO`).
