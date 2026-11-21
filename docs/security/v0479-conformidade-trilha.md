---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: 0f4facab2db2b2aa60107dfdfac9cad6f9814560
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E63.11, revalidação da trilha do conformidade)

Volta por delta. As rodadas anteriores (heads `6c0b0f03` e `e48a2e60`, A1 a A15 e S1 a S17) ficam no git e não são recopiadas aqui.

Delta lido (`forge-check parecer delta`, `e48a2e60..0f4facab`): `hooks/conformidade.py` (`CONFIG_PROTEGIDA`, `config_da_linha`, `git_config`, `COPIA_DE_WT`, `SUBIDA_NO_TEXTO`, `sem_copia_de_wt`, `controle_no_texto`, `literal_atribuido`, `entrada_de_arquivo`, `shell_que_le_a_entrada`), `docs/hooks.md:56-58` e as 30 fixtures do domínio. Fora do domínio, li só a seção E63.9 de `tests/provas/v0479-corpus-custo.md`.

Sem suíte local, como pede o brief. Sem PR, então sem CI para citar. Rodei o hook real pelo lançador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), com HOME e TMPDIR próprios em `~/.forge-contrib/wt/sec-e6311/`: 91 sondas em três árvores (`git archive` da base `d4f0b10a`, do `e48a2e60` e do `0f4facab`). Rodei também o bash real numa árvore falsa dentro do mesmo TMPDIR e o teste do custo do corpus nas três árvores.

## Gatilhos
Gatilhos: hook de conformidade (analisador de comando), R-VERIFY, R-FLUXO, pastas de controle do Jarvis (VV-2), catraca do CI (afrouxa-regra).

## Achados
- A16 (bloqueante) hooks/conformidade.py:3835 · `sem_copia_de_wt` confia no `~` e no `$HOME` com o HOME trocado na linha. `HOME=$TMPDIR/f; echo x >> ~/.forge-contrib/wt/x/docs/pedidos/v1.md` grava o pedido da pasta mãe (S18, bash real). Também com `$HOME` (S19), que o `docs/hooks.md:56` diz desfazer a exceção.
- A17 (recomendado) docs/hooks.md:56 · O link criado na mesma linha dentro de `wt/` passa: `ln -s ~/.forge-contrib ~/.forge-contrib/wt/q && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` (S20, bash real). Já passava no e48a2e60. Recuse ou declare no limite.

## Sondas
- S18 · sessão do Forge, forge:tech-lead, com o link `$TMPDIR/f/.forge-contrib/wt/x` → `~/.forge-contrib`, Bash `HOME=$TMPDIR/f; echo x >> ~/.forge-contrib/wt/x/docs/pedidos/v1.md` · espera: rc 2 · obtido: rc 0 (e48a2e60: rc 2; bash real grava a pasta mãe)
- S19 · o mesmo, Bash `HOME=$TMPDIR/f; echo x >> $HOME/.forge-contrib/wt/x/docs/pedidos/v1.md` · espera: rc 2 · obtido: rc 0 (e48a2e60: rc 2)
- S20 · sessão do Forge, agent_type forge:tech-lead, Bash `ln -s ~/.forge-contrib ~/.forge-contrib/wt/q && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` · espera: rc 2 · obtido: rc 0 (e48a2e60: rc 0; bash real: grava a pasta mãe)

## Detalhe dos achados

### Achados anteriores: estado no head 0f4facab
A1 a A11 seguem como na rodada `e48a2e60` (o delta não toca o código deles).

| Achado | Estado | Prova |
|---|---|---|
| A12 | fechado | S13 e S14 recusam. Recusam também 26 variantes: `0</dev/stdin`, `/dev/fd/0`, `/proc/self/fd/0`, `/dev/./stdin`, `//dev//stdin`, aspas, `/d""ev`, `cd /dev && … < stdin`, `cd /proc/self/fd && … < 0`, `fd/0`, `dev/stdin` relativo, `0< x.sh 0< /dev/stdin`, `< /dev/stdin 3< x.sh`, `0<&3 3</dev/stdin`, `<&0`, `/dev/tty`, `/sys/../dev/stdin`, `~/stdin`, `/dev/std*`, `$'…'` e `$B`. Os legítimos `bash < scripts/x.sh`, `bash 0< scripts/x.sh`, `printf 'git status' \| bash` e `git log $(…)..HEAD` passam. `B=x; bash < "scripts/$B.sh"` recusa nas três árvores: é custo antigo, não deste delta. |
| A13 | fechado | S15 a S17 recusam. Recusam também `help.autoCorrect=1`, `HELP.AUTOCORRECT`, `-c help.autocorrect` sem valor, `git config` com `--worktree`, `--global`, `set`, `--add`, `-f .git/config` e `--file=`. `git config --get help.autocorrect` passa. |
| A14 | fechado | `docs/hooks.md:56` e `:58` dizem agora que o `denyWrite` não cobre o pedido, o brief nem o envio. |
| A15 | limite declarado, aceito | `docs/hooks.md:56`. O `os.chdir` para a pasta mãe no `python3 -c` também passa, como declarado. |

### A16: o `~` e o `$HOME` depois de `HOME=` na linha
**Evidência.** `sem_copia_de_wt` resolve a cópia com o `Path.home()` do hook (`:3829`). Ela troca o caminho da cópia por NUL (`:3834`) e só depois confere os `$` (`:3835`), e confere no texto já trocado. Por isso:
- o `$HOME` que era o começo da cópia some antes da conferência;
- o `~` nunca é conferido;
- o `HOME=…`, `export HOME=…` e `read HOME` da mesma linha não desfazem a exceção.

O bash expande o `~` e o `$HOME` com o HOME novo. Basta plantar antes, numa linha que não cita `pedidos`, um link `<dir>/.forge-contrib/wt/x` para a pasta mãe. Provei no bash real, numa árvore falsa no meu TMPDIR: S18 gravou no pedido da pasta mãe.

**Comparação entre árvores.**

| Forma | d4f0b10a | e48a2e60 | 0f4facab |
|---|---|---|---|
| `HOME=$TMPDIR/f; … >> ~/.forge-contrib/wt/x/docs/pedidos/v1.md` (S18) | 0 | 2 | 0 |
| `HOME=$TMPDIR/f; … >> $HOME/.forge-contrib/wt/x/…` (S19) | 0 | 2 | 0 |
| `export HOME=$TMPDIR/f; …`, `read HOME < $TMPDIR/h; …` | 0 | 2 | 0 |
| `HOME=$TMPDIR/f; cd ~/.forge-contrib/wt/x && echo x >> docs/briefs/b1.md` | 0 | 2 | 0 |
| `HOME=$TMPDIR/f bash -c '… ~/.forge-contrib/wt/x/docs/pedidos/v1.md'` | 0 | 2 | 0 |
| `HOME=~/.forge-contrib/wt/g; … >> ~/.forge-contrib/wt/x/docs/pedidos/v1.md` (sem `$`) | 0 | 0 | 0 |

A base não tem a trava do controle, então os zeros dela não contam. A forma sem `$` já passava no `e48a2e60`: o furo da dimensão é anterior. O delta o alarga a toda linha com `$TMPDIR` ou `$HOME`.

**Ataque.** Quem ataca é o subagente que não é o jarvis e quer gravar no pedido uma linha `entrega conferida` ou `DECISÃO DO DONO` (VV-2). São dois comandos, e o sandbox não cobre o caminho (A14). Severidade média, igual à do A1 da E63.3.

**Correção mínima.** Esta é uma dimensão nova da matriz: o nome que o bash usa para expandir o caminho, trocado na própria linha.
- Em `sem_copia_de_wt`, conferir os `$` no texto original, antes da troca.
- Na mesma função, voltar o texto intacto quando o nome `HOME` aparece fora do `$HOME`, em qualquer forma: `HOME=`, `HOME+=`, `export`, `declare`, `local`, `readonly`, `read`, `printf -v`, `env HOME=`, `unset HOME`.
- Para fechar também a forma sem `$`: contar como construção que o hook não modela a linha que atribui `HOME` e cita `forge-contrib`. Isso vale para quem não é o jarvis, em `controle_no_texto`.
- Fixtures `cpb-*-bloqueia`: S18, S19, `export HOME`, `read HOME` e `HOME=~/.forge-contrib/wt/g; …`. A `cpb-tech-lead-wt-cd-le-pedido-tmpdir-libera` fica mantida.

Esforço P. Dono: tech-lead.

### A17: o link criado na mesma linha
`os.path.realpath` (`:3833`) e a conferência de caminho resolvem o alvo antes do comando rodar. A pasta `wt/q` ainda não existe, então os dois a leem como cópia, e o `ln -s` da mesma linha a cria apontando para a pasta mãe. `ln -s ~/.forge-contrib/docs ~/.forge-contrib/wt/q; echo x >> ~/.forge-contrib/wt/q/pedidos/v1.md` também passa. O mesmo vale para `mv` de um link plantado antes para o nome usado na linha. O link já existente recusa: `wt/up/…` e `cd ~/.forge-contrib/wt/up` dão rc 2.

O furo já existia no `e48a2e60`, e o limite declarado só cita o link usado depois da variável. Há duas saídas, à escolha do dono do código:
- recusar, para quem não é o jarvis, a linha que cita `pedidos` ou `briefs` e também cria ou move uma entrada em `wt/` (`ln`, `mv`, `cp -s`, `cp -l`, `cp --symbolic-link`, `install`, `rename`);
- declarar o limite em `docs/hooks.md:56`.

Esforço P. Dono: tech-lead.

### Ataques à lista positiva que recusam
No `0f4facab`, a porta reaberta segura estas formas:
- a subida: `..`, `.''.`, `dirname`, `${d%…}`, `$p$p`, `~-`, `cd "$OLDPWD"`;
- a reatribuição de nome: `f=…; f=~/.forge-contrib`, `f+=/.`, `unset f`, `read d`, `printf -v`;
- os nomes parecidos com TMPDIR: `$TMPDIR_NADA`, `$TMPDIRX` e `TMPDIR=~/.forge-contrib`;
- o laço `for d in`;
- o `cd` e o `cd ~` de volta para `.forge-contrib/docs/pedidos`.

O link plantado antes dentro de `wt/` e usado por `cd` ou pelo caminho literal também recusa. O `$f/up/docs/pedidos/` passa, como o limite declarado. A rotina legítima passa: `cd ~/.forge-contrib/wt/x && sed … > $TMPDIR/e.txt`, `f=~/.forge-contrib/wt/r.txt; grep … > $f` e `cd $HOME/.forge-contrib/wt/x && grep … > $TMPDIR/g.txt`.

### Confirmações pedidas (head 0f4facab)
**(1) A mudança só aperta, frente à develop (`d4f0b10a`)?** Sim, confirmo por escrito, quanto ao comportamento do hook.
- Nas 91 sondas, nenhuma foi de 2 na base para 0 no head.
- Nas fixtures, nenhuma de `tests/hooks/` mudou de código esperado da base para o head. A única que sumiu é a `oraculo-limite-python-c-libera`, renomeada para `-bloqueia` (de 0 para 2), já registrada na rodada anterior.
- O que o delta soma à develop:
  - `help.autocorrect` em `CONFIG_PROTEGIDA`, `config_da_linha` e `git_config`: só recusa;
  - `entrada_de_arquivo`: estreita a exceção de uma trava que a develop não tem;
  - `sem_copia_de_wt`: afrouxa só a trava do controle, que também não existe na develop.
- Dentro da volta, o `sem_copia_de_wt` afrouxa frente ao `e48a2e60` mais do que a rotina pedia. Isso é o A16 e não muda a resposta frente à develop.
- A correção do A16 muda o código. A confirmação deve ser renovada no head corrigido.

**(2) Custo do corpus abaixo de 0,1% e vindo de trava que só aperta?** Sim, confirmo. Medi com `test_corpus_nos_dois_hooks`, instrumentado só para imprimir a contagem, nas três árvores e na mesma máquina. Condições: Python 3.12.3, 557 execuções e 234 variáveis. Os absolutos daqui diferem dos do autor (4637 subprocessos, TMPDIR mais fundo).

| Árvore | `interpretador` |
|---|---|
| base `d4f0b10a` | 5927953 |
| `e48a2e60` | 5933431 |
| head `0f4facab` | 5933431 |

A diferença do head para a base é +5478 passos, a mesma do autor. 5478 / 5927953 = 0,0924% aqui, e 5478 / 5897219 = 0,0929% nos números dele: abaixo de 0,1% nos dois.

O delta `e48a2e60..0f4facab` soma +0. O custo inteiro vem das travas do `e48a2e60`, que só recusam frente à develop (item 1). O `sem_copia_de_wt` só roda na `GuardaDaProva`, e o corpus não chega lá. A correção do A16 cai na mesma função e não deve mudar a conta, mas pede medida nova.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas, todas locais:
- o lançador de fixtures de `tests/test_hooks.py`, com 91 sondas em três árvores;
- `test_corpus_nos_dois_hooks`, nas três árvores;
- o bash real, numa árvore falsa no TMPDIR próprio (S18 e S20). Nenhuma pasta de controle real foi tocada.

Lacunas: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow, dependência nem segredo.
