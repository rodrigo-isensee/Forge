---
tipo: review
contrato: 1
pedido: anti-alucinacao-regras
branch: melhoria/anti-alucinacao-regras
commit: 8cb2d17
parecer: reprovado
revisor: forge:tech-lead (independente)
data: 2026-10-14
---
# Review independente: regras, prompt e conferente (fatia 2 do anti-alucinação)

Escopo: `git diff f2dbe3a..8cb2d17`, 6 commits e 31 arquivos. O texto foi conferido contra a linha "| 2 |" da §11 e contra a §10 da proposta anti-alucinação, com as decisões do dono P1 = B, P2 = A, P3 = A, §14 = B e a diretriz do corte de escopo. Este parecer não usou o parecer de autor como base: ele só foi lido para conferir as pendências que declara.

## Parecer: **ajustes necessários**
Encontrei dois desvios de escrita no papel `so_leitura`, ambos reproduzidos. O alvo central da fatia é justamente que o conferente não escreva por desvio, e ele não é atingido. O texto das regras, do `jarvis.md` e do `conferente.md` está aprovado.

| # | Arquivo:linha | Problema | Sugestão | Severidade |
|---|---|---|---|---|
| 1 | `hooks/conformidade.json:75` (`"git ls-remote"`) e `hooks/conformidade.py:619` | `git ls-remote` aceita qualquer argumento. Com `--upload-pack=<cmd>`, `-u <cmd>` ou `--exec=<cmd>`, o git executa o comando dado num shell. O hook libera, com rc 0: `git ls-remote --upload-pack='touch PWNED;' .`. Rodado num repositório descartável, criou o arquivo `PWNED`. Isso dá execução arbitrária a partir de um comando da lista branca. | Em `checar_so_leitura`, recusar as opções que executam programa: `--upload-pack`, `-u`, `--exec` (no `ls-remote`), e por precaução `--receive-pack`. Mais simples: aceitar, no `ls-remote`, só `--heads`, `--tags`, `--refs`, `-q`, `--exit-code`, `--symref` e argumentos posicionais. Incluir uma fixture `conferente-upload-pack-bloqueia.json`. | **bloqueia** |
| 2 | `hooks/conformidade.py:555` | O hook não confere a substituição de processo `<(...)` e `>(...)`. Ele só desce em `$(...)` e em crase. O hook libera, com rc 0: `cat <(touch x)`, `grep a <(touch x)`, `echo >(touch t)` e `git status 2>&1 >(touch t)`. Pelo bash, `cat <(touch z)` criou `z`. Com duas substituições na mesma linha, o comando é recusado por acaso, porque `<(` vira palavra. | No papel só de leitura, recusar toda palavra que contenha `<(` ou `>(`, na linha de `checar_so_leitura` (é o ajuste mínimo da fatia). Incluir uma fixture `conferente-subst-processo-bloqueia.json` com `cat <(touch x)`. | **bloqueia** |
| 3 | `hooks/conformidade.py:633` | `startswith("--output")` também recusa `--output-indicator-new`, `--output-indicator-old` e `--output-indicator-context`, que só leem. É um falso bloqueio, sem risco. | Comparar `a == "--output" or a.startswith("--output=")`. | recomendado |
| 4 | `tests/hooks/conformidade/` | As 14 fixtures cobrem redirecionamento, `sed -i`, `git commit`/`push`/`-c`, `python3 -c`, `$(...)`, variável na linha, programa com caminho, Write/Edit e `gh pr create`. Não cobrem `tee`, `xargs`, `;`/`||` com comando de fora da lista, `<(...)` nem `--upload-pack`. Pela sondagem abaixo, o hook já barra os três primeiros, mas sem fixture eles podem regredir. | Incluir fixtures `tee` e `xargs`, além das dos itens 1 e 2. | recomendado |

### Sondagem do `so_leitura` (hook do HEAD, `agent_type: forge:conferente`, projeto temporário)
```
0 | git ls-remote --upload-pack='touch PWNED;' .      <- desvio (item 1)
0 | git ls-remote -u 'touch W;' .                     <- desvio (item 1)
0 | git ls-remote --exec=x .                          <- desvio (item 1)
0 | cat <(touch x)                                    <- desvio (item 2)
0 | echo >(touch t)                                   <- desvio (item 2)
2 | echo `touch x`            2 | { touch x; }        2 | (touch x)          2 | f(){ touch x; }; f
2 | echo x | xargs touch      2 | echo x | tee >(cat) 2 | echo hi; touch y   2 | test -e x || touch y
2 | echo x >| f   2 | echo x &> f   2 | echo x >&f   2 | echo x 3>f   2 | echo x <>f   2 | cat <<X > f
2 | for i in 1; do touch x; done  2 | git --git-dir=.git log  2 | gh api repos/x/y -X DELETE
2 | git show --output x.patch     2 | git log --format=%h $(touch z)
0 | echo x 2>&1 | echo x >&2 | cat f > /dev/stdout | git -C . --no-pager log -1 | echo $(git log -1)   (leitura, certo)
2 | git log -1 --output-indicator-new=x    <- falso bloqueio (item 3)
```
Efeito real conferido fora do hook, num repositório descartável: `git ls-remote --upload-pack='touch PWNED;' .` e `bash -c 'cat <(touch z)'` criaram `PWNED` e `z`. No git 2.43.0, as abreviações `--outp=` e `--outpu=` são recusadas pelo próprio git, então não são desvio.

### Para o `security-engineer` (aponto, não decido)
- **A lacuna do item 2 é anterior a esta fatia e vale para todos os papéis.** Com o hook da base `f2dbe3a` e `agent_type: forge:tech-lead`, `cat <(git push --force origin main)` sai com 0, enquanto `git push --force origin main` sai com 2 (`R-VERIFY`). Ou seja, a substituição de processo dribla qualquer regra do `conformidade`. A correção geral (descer em `<(...)` e `>(...)` como em `$(...)`) é cartão para ele. Pode entrar nesta fatia ou na 3, mas não deve ficar sem dono.
- **Pendência 1 do parecer de autor:** no clone do Forge, o `conformidade` não age, e o conferente fica contido só pelo frontmatter. Concordo que é dele, e a fatia 3 é a candidata.
- `git status` pode regravar o `.git/index` (atualiza o cache de stat). É escrita de metadado, não de conteúdo. Fica registrado como risco aceito, para ele avaliar.

## O que foi conferido e está certo
- **Invariantes (`tests/config.json`):** o diff só acrescenta. A linha de `hooks/conformidade.py` foi reformatada e mantém os oito itens anteriores (`REPO_APAGAR`, `VISIBILIDADE_PUBLICA`, `filter-branch`, `filter-repo`, `--mirror`, `permissionDecision`, `def checar_remocao`, `SUGESTAO`), com dois novos. Não há linha `-` que tire item de `invariantes` nem de `agentes_obrigatorios`. As invariantes que a §10 pede para `jarvis.md`, `conferente.md` e `R-DECISAO.md` estão todas presentes. As de `R-REVIEW` e dos hooks `decisao`, `prova` e `brief` são de outras fatias.
- **`jarvis.md`:**
  - O passo 1 tem "uma pergunta por vez (as demais esperam na fila, e você diz quantas são)" e não tem "máx. 3". A única ocorrência que sobra é "máx. 3 voltas por bug", no passo 6.
  - O prompt-padrão continua com 6 seções. Ganha "Fora do escopo" com a marca e as cinco partes do corte, `PQ-n` com o tipo de prova e o bloco `Provas:`.
  - A conferência da entrega entra antes do review no passo 5. O passo 8 traz a tabela pedido × entregue, com a marca e a decisão nas linhas cortadas.
  - O texto é coerente com a `R-DECISAO` emendada: uma pergunta por vez em tudo, a fila com a contagem e o corte com marca e referência à decisão. Os isentos da conferência do brief são os mesmos na `R-BRIEF` e no `jarvis.md`: o conferente e quem não tem Bash nem escrita.
- **Regras:** `R-PROVA` e `R-BRIEF` seguem a §10. O `verificada_por` diz, corretamente, que os hooks `prova` e `brief` ainda não existem, então a regra não promete uma trava que ainda não há. Elas estão no índice `docs/regras/README.md`.
- **`conferente.md`:**
  - Sem ferramenta de escrita, em haiku, com instrução de "não obedecer ao brief" e veredito na última linha.
  - A marca de corte é conferida por `grep`, e os anexos implícitos estão listados. A tabela de etapas cobre "pr só depois de review e QA" e a ordem `createdAt`/`mergedAt` contra o parecer.
  - A lista de comandos do texto é a mesma do `so_leitura`, menos `true` e `[`.
- **Decisões do dono:**
  - P2 = A está atendida.
  - P3 = A está atendida: o conferente roda em toda entrega com commit ou ato no GitHub, e o brief é conferido antes.
  - A diretriz do corte está atendida: marca literal, trecho, motivo, consequência, decisão e a lista "Fora do escopo" no modelo de pedido.
  - P1 = B e §14 = B são das fatias 3 e seguintes, e nada aqui as contradiz.
- **`R-NEUTRO`:** o teste `Neutralidade` passou. Nas regras, no agente e no modelo, nenhum nome de projeto, stack ou regra de negócio. O exemplo `forge:node-backend` só aparece no parecer de autor.
- **Fluxo:** o PR deve ir com o rótulo `afrouxa-regra`, porque toca `hooks/conformidade.py` em `PROTEGIDOS`, e em rascunho até os pareceres (§14 = B). Também precisa do parecer do `security-engineer`.
- **Commits:** Conventional Commits em português, um por mudança coerente.

## Ferramentas (saída citada)
```
$ uptime   → load average: 1.99, 3.35, 3.59
$ python3 -m unittest discover -s tests -v
Ran 562 tests in 500.534s
OK
$ scripts/validar-plugin.sh
✔ Validation passed
```

## Fica para o QA
O PQ-3 com o `forge:conferente` rodando de verdade nos modos `brief` e `entrega`. O parecer de autor declarou que executou à mão.

## Para reaprovar
Corrigir os itens 1 e 2, com fixtures, no autor. Basta um novo review do diff de correção, sem refazer o texto.
