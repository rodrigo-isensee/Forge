---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: e48a2e60a11d97a36ab936fedacb1e93477ff940
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E63.7, revalidação da trilha do conformidade)

Volta por delta. A rodada anterior (head `6c0b0f03`, A1 a A11 e S1 a S12) fica no git e não é recopiada aqui.

Delta lido (`forge-check parecer delta`, `6c0b0f03..e48a2e60`): `hooks/conformidade.py` (+82 −14: `INDICE_NO_GIT`, `caminho_com_curinga_no_texto`, `checar_texto`, a `TRAVA` do envio, `CONTROLE_NO_TEXTO`, `na_pasta_do_controle`, `envio_com_substituicao`, `shell_que_le_a_entrada`, `GIT_GLOBAIS_COM_VALOR`), `docs/hooks.md:56-58` e as 36 fixtures novas ou renomeadas do domínio. Fora do domínio, li só o que tira dúvida: a medida em `tests/apoio_volta_unica.py:202-205` e a seção E63.5 de `tests/provas/v0479-corpus-custo.md`.

Sem suíte local, como pede o brief. Sem PR, então sem CI para citar. Rodei o hook real pelo lançador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), com HOME e pastas temporários: 316 sondas no head e 34 também na base `d4f0b10a` e no head anterior `6c0b0f03`. Também rodei o teste do custo do corpus nas três árvores e o git real num repositório descartável em `$TMPDIR`.

## Gatilhos
Gatilhos: hook de conformidade (analisador de comando), R-VERIFY, R-FLUXO, pastas de controle do Jarvis (VV-2), catraca do CI (afrouxa-regra).

## Achados
- A12 (bloqueante) hooks/conformidade.py:4038 · A exceção da entrada de arquivo trata `/dev/stdin` como arquivo. `echo 'git push --no-verify …' | bash < /dev/stdin` passa no projeto e na sessão do Forge, e também com `0<`, `/dev/fd/0` e `/proc/self/fd/0`. No 6c0b0f03 recusava (S13, S14). Reabre o A4.
- A13 (bloqueante) hooks/conformidade.py:2801 · `help.autocorrect` troca o subcomando como o alias. `git -c help.autocorrect=immediate stge .githooks/pre-push` grava o índice (S15), também por `git config` e depois `git stge` (S16), e `… puhs origin develop` envia (S17). Reabre o A2.
- A14 (recomendado) docs/hooks.md:56 · Os limites A10 (:56) e A11 (:58) dizem "cobre a trava do sandbox (A3, E29)". O `denyWrite` (templates/projeto/.claude/settings.json:37-42) não cobre `~/.forge-contrib/docs/pedidos/`, `briefs/` nem o envio. Tire a frase ou cite o que de fato cobre.
- A15 (recomendado) hooks/conformidade.py:1975 · O A9 fechou só o caminho literal. O interpretador que monta o home passa para o tech-lead, nos dois alvos (com e sem `*`): `python3 -c "…open(os.path.expanduser('~/.forge-contrib/docs/pedidos/v1.md'),'w')"` e `os.environ['HOME']+…`. Na base também passava.

## Sondas
- S13 · projeto, branch feature/x, agent_type forge:dev, Bash `echo 'git push --no-verify origin feature/x' | bash < /dev/stdin` · espera: rc 2 · obtido: rc 0 (6c0b0f03: rc 2)
- S14 · sessão do Forge, branch melhoria/x, agent_type forge:dev, Bash `echo 'git push --no-verify origin develop' | bash < /dev/stdin` · espera: rc 2 · obtido: rc 0
- S15 · projeto, agent_type forge:dev, Bash `git -c help.autocorrect=immediate stge .githooks/pre-push` · espera: rc 2 · obtido: rc 0 (git real: "you meant 'stage'", índice `A .githooks/pre-push`)
- S16 · projeto, agent_type forge:dev, Bash `git config help.autocorrect immediate` e depois `git stge .githooks/pre-push` · espera: rc 2 em uma das duas · obtido: rc 0 e rc 0
- S17 · sessão do Forge, branch melhoria/x, agent_type forge:dev, Bash `git -c help.autocorrect=immediate puhs origin develop` · espera: rc 2 · obtido: rc 0 (projeto: rc 0; git real: "you meant 'push'")

## Detalhe dos achados

### Achados anteriores: estado no head e48a2e60
Refiz S1 a S12 da rodada anterior: as doze recusam (rc 2).

| Achado | Estado | Prova |
|---|---|---|
| A1 | fechado | S1, S2 (7 papéis × clone e `wt/x`) e S3 recusam. Também recusam: a pasta corrente em `docs/pedidos/` (`f=v1.md; echo x >> $f`), `$HOME` na mãe e `${D,,}`. |
| A2 | fechado | `git stage` com os 6 caminhos `quem: []`, `-f`, `-c filter`, `--git-dir` e `-C` recusam. `-c alias.s=stage` recusa (R-REVIEW). O autocorrect reabre a família (A13). |
| A3 | fechado | `--git-dir`, `--git-dir=`, `--work-tree`, `--namespace`, `-C` duplo, `--no-pager`, `-P`, `--bare`, `--exec-path=` e `-c` recusam. `--super-prefix` passa, mas o git atual o rejeita (rc 129), então não há achado. |
| A4 | fechado, reaberto pelo A12 | 54 formas do shell que lê a entrada recusam: envolvedores, caminho, aspas, escape, outros shells, opções com valor, `/dev/fd/0`, `{ bash; }`, `(bash)`, `<<<`, `bash < <(…)` e `exec 3< <(…); bash <&3`. A exceção nova da redireção `<` reabriu o A4 (A12). |
| A5 | fechado | 16 de 17 formas do `xargs` recusam. `parallel git` passa, mas o programa não está na máquina e não tem caminho realista, então não há achado. |
| A6 | fechado | Na sessão do Forge, a pipe com `env bash`, `. <(…)`, `--git-dir`, `xargs git`, `$(echo push)` e o destino por substituição recusam. |
| A7 | fechado | `git reset` com pathspec, `-q`, `-p`, a pasta, `:(top)`, curinga e `--pathspec-from-file` recusam. 12 legítimos passam, entre eles `--hard origin/x`, `--soft`, `--merge`, `--keep`, `src/app.js`, `.` e `docs/qa/q.md`. |
| A8 | limite declarado, aceito | `docs/hooks.md:57` lista tudo o que o A8 pedia. `git read-tree HEAD` passa, como declarado. |
| A9 | fechado em parte | O texto com o home real e o `*` recusa no python, no perl e no node. O home calculado no interpretador segue aberto (A15). |
| A10 | limite declarado, aceito | `docs/hooks.md:56`. Conferi que `docs/ped*/`, `${p}dos`, `$(echo pedidos)` e `git -C ~/.forge-contrib apply` passam, como declarado. A frase da trava do sandbox está errada (A14). |
| A11 | limite declarado, aceito | `docs/hooks.md:58`. O `printf` partido passa, como declarado. |

### A12: a exceção `bash < arquivo` aceita a própria entrada padrão
**Evidência.** `shell_que_le_a_entrada` (`hooks/conformidade.py:4038`) sai com `False` quando há qualquer redireção `<` com alvo literal. Sai assim também quando o alvo é `/dev/stdin`, `/dev/fd/0` ou `/proc/self/fd/0`: os nomes que o próprio `ENTRADA_DO_SHELL` (`:4028`) trata como a entrada, ou seja, a pipe. Testei no bash real: `echo 'echo X' | bash < /dev/stdin` imprime X.

**Comparação entre árvores.** Rodei as mesmas formas na base, no head anterior e no head novo:

| Forma | d4f0b10a | 6c0b0f03 | e48a2e60 |
|---|---|---|---|
| `\| bash < /dev/stdin` | 0 | 2 | 0 |
| `0< /dev/stdin` e `0</dev/stdin` | 0 | 2 | 0 |
| `< /dev/fd/0` e `< /proc/self/fd/0` | 0 | 2 | 0 |
| `sh < /dev/stdin` e `bash -s < /dev/stdin` | 0 | 2 | 0 |
| `bash 3< x 0< /dev/stdin` | 0 | 2 | 0 |
| `bash <> /dev/stdin` | 0 | 2 | 2 |

**Ataque.** Quem ataca é o agente que contorna R-VERIFY ou R-FLUXO. É a mesma forma do A4 com uma redireção a mais. O `docs/hooks.md:58` promete `| bash /dev/stdin` como recusado. Severidade média, igual à do A4.

**Correção mínima.** Na exceção, só conta como arquivo a redireção da entrada padrão (sem número ou com `0`) cujo alvo não está em `ENTRADA_DO_SHELL` nem começa com `/dev/fd/` ou `/proc/`. Testes: S13 e S14 como fixtures `sub-*-bloqueia`, mais a `sub-shell-entrada-de-arquivo-libera` mantida. Esforço P. Dono: tech-lead.

### A13: `help.autocorrect` é um alias com outro nome
**Evidência.** `config_da_linha` (`:2801`) recusa `-c alias.*` porque o alias troca o subcomando que o hook leu. Com `help.autocorrect`, o git também roda outro subcomando: o que tem o nome mais próximo do digitado. Provas no git real, num repositório descartável:
- `stge` virou `stage` e gravou `.githooks/pre-push` no índice;
- `puhs` e `psh` viraram `push`;
- `updat-index` virou `update-index`.

O hook lê `stge` e `puhs` como subcomandos desconhecidos e libera:
- S15 a S17;
- `-c help.autoCorrect=1`;
- `git config help.autocorrect immediate` (`git_config`, `:2943`, não barra a chave).

O `--no-verify` escrito por extenso segue recusado (`git … psh --no-verify` dá rc 2). A forma por ambiente (`GIT_CONFIG_COUNT`, `GIT_CONFIG_PARAMETERS`) já recusa.

**Ataque.** O agente grava no índice um caminho `quem: []` (o que o A2 fechou) e envia para a integração sem o subcomando `push` no texto. Hoje, para o envio à develop, sobra o pre-push local. Severidade média, igual à do A2.

**Correção mínima.**
- Em `config_da_linha`, tratar `help.autocorrect` (sem caixa) como o `alias.`.
- Em `git_config`, recusar gravar `help.autocorrect` como já recusa o alias.
- Fixtures: S15 a S17 com rc 2, mais `git config --get help.autocorrect` livre.

Esforço P. Dono: tech-lead. Este achado vem de uma dimensão nova da matriz, o subcomando trocado por configuração. A base já tinha o furo, mas os cartões A2 e A3 o tocam.

### A14 e A15
**A14.** A frase dá ao limite uma cobertura que não existe. O dono pode ler o limite como mitigado.

**A15.** O A15 vem da mesma família do A9. Hoje nada impede o tech-lead de gravar o pedido por `expanduser`. Há duas saídas, à escolha do dono do código:
- recusar, na `GuardaDaProva` e para quem não é o jarvis, o texto de interpretador (`-c` ou `-e`) que casa `CONTROLE_NO_TEXTO` e grava;
- declarar o limite em `docs/hooks.md:56`.

Esforço P. Dono: tech-lead.

### Custo para o legítimo, sem achado
Os 44 legítimos do envio e do shell passam nos dois contextos (projeto e sessão do Forge), entre eles:
- `bash < scripts/x.sh && git push`;
- `env FOO=1 bash x.sh`;
- `. ./env.sh`;
- `source .venv/bin/activate`;
- `printf 'git status' | bash`;
- `git log $(git merge-base …)..HEAD`;
- `git ls-files -m | xargs git add`;
- `git -C . push`;
- `git commit -m "$(…)"`.

No controle, a leitura literal passa nas três pastas correntes. Duas formas recusam, como já recusavam no 6c0b0f03: a saída para variável e o laço com `$f`. Com a pasta corrente em `~/.forge-contrib`, recusa também a linha com `$TMPDIR` que cita `briefs` em qualquer lugar (`echo x > $TMPDIR/briefs.txt`). Esse custo é novo, vem do `na_pasta_do_controle` e só aperta. O contorno é rodar fora daquela pasta.

### Confirmações pedidas (head e48a2e60)
**(1) A mudança só aperta, frente à develop (`d4f0b10a`)?** Sim, confirmo por escrito, quanto ao comportamento do hook.
- Cada trecho do delta só soma recusas:
  - `stage` e `reset` em `INDICE_NO_GIT`;
  - o `*` da política no texto;
  - `CONTROLE_NO_TEXTO`, mais largo;
  - `na_pasta_do_controle`;
  - a `TRAVA` no lugar da `TRAVA_OPACA`;
  - o filtro `xargs` e `stdin`;
  - `shell_que_le_a_entrada`;
  - `GIT_GLOBAIS_COM_VALOR`.
- Uso do `INDICE_NO_GIT`: o `reset` passa por `git_indice` (`:2621`), que só barra o caminho de categoria `instalacao`.
- Fixtures frente à develop: nenhuma foi de 2 para 0. A ST1, a ST2 e o oráculo `python -c` (renomeado para `oraculo-python-c-tech-lead-bloqueia`) foram de 0 para 2. A `rverify-fp-…-libera` passou a rodar como jarvis.
- Sondas nas três árvores: das 34, as 2 que a base recusa seguem recusadas no head, e nenhuma foi de 2 para 0 frente à base.
- A única folga está dentro da própria volta. A exceção da redireção estreitou a trava nova do A4, que não existe na develop: 11 das 34 sondas foram de 2 para 0 frente ao 6c0b0f03 (entre elas o legítimo `bash < scripts/x.sh && git push`). Isso não afrouxa regra da develop, mas é o A12.
- O único afrouxamento do diff segue sendo o teto do custo, tratado em (2).
- A correção do A12 e do A13 também só aperta, mas muda o código. A confirmação deve ser renovada no head corrigido.

**(2) Custo do corpus.** Medi com `test_corpus_nos_dois_hooks`, instrumentado só para imprimir a contagem, nas três árvores (`git archive`) e na mesma máquina. Condições: Python 3.12.3, tmp a 2 níveis, 234 variáveis, 557 execuções e 4631 subprocessos nas três.

| Árvore | `interpretador` |
|---|---|
| base `d4f0b10a` | 5897219 |
| head anterior `6c0b0f03` | 5902634 |
| head `e48a2e60` | 5902697 |

A diferença do head para a base é +5478 passos. 5478 / 5897219 = 0,0929%, abaixo de 0,1%. Os três números batem com a seção E63.5 de `tests/provas/v0479-corpus-custo.md`. O aumento vem só do código das travas novas, que só recusam frente à develop (item 1). Os +63 sobre o 6c0b0f03 incluem a exceção do A12. Confirmo para este head. A correção do A12 e do A13 pede medida nova.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas, todas locais:
- o lançador de fixtures de `tests/test_hooks.py`, com 316 sondas no head e 34 também na base e no 6c0b0f03;
- `test_corpus_nos_dois_hooks`, nas três árvores;
- o git e o bash reais, num repositório descartável em `$TMPDIR`: o autocorrect, o `--super-prefix` e o `bash < /dev/stdin`.

Lacunas: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow, dependência nem segredo.
