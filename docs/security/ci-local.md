---
tipo: revisao-seguranca
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: 083bb7b02260135e6db2cc402adb8c8f1b7beff8
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-14
---
# Review de segurança: ci-local

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
