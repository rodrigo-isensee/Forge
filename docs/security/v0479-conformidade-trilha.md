---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: 7a739fca7bed5df9a09bba96ce6b8fca799f906e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E63.15, revalidação da trilha do conformidade)

Volta por delta. As rodadas anteriores (heads `6c0b0f03`, `e48a2e60` e `0f4facab`, A1 a A17 e S1 a S20) ficam no git e não são recopiadas aqui.

Delta lido (`forge-check parecer delta`, `0f4facab..7a739fca`): `hooks/conformidade.py` (`CAMINHO_TROCADO_NA_LINHA` em `:3823`, `sem_copia_de_wt`, `GuardaDaProva.bash` em `:3879`), `docs/hooks.md:56` e as 11 fixtures `cpb-*` novas do domínio. Fora do domínio, nada relido.

Sem suíte local, como pede o brief. Não há PR, então não há CI para citar. Rodei o hook real pelo lançador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`) em três árvores (`git archive` da develop `d4f0b10a`, do `0f4facab` e do `7a739fca`), com TMPDIR próprio fora de `~/.forge-contrib` e de `/tmp/claude-0`. Foram 58 sondas, as 11 fixtures do delta e as 48 fixtures `libera` novas da trilha. Rodei também o bash real numa árvore falsa no mesmo TMPDIR e o teste do custo do corpus na develop e no head.

Critério desta trilha (decisão do time anotada no pedido): é bloqueante só a porta que a trilha abre frente à develop `d4f0b10a`, ou a que ela reabre depois de fechar. A porta que já existe na develop é recomendado, com cartão e limite declarado em `docs/hooks.md`.

## Gatilhos
Gatilhos: hook de conformidade (analisador de comando), R-VERIFY, R-FLUXO, pastas de controle do Jarvis (VV-2), catraca do CI (afrouxa-regra).

## Achados
- A18 (recomendado) docs/hooks.md:56 · O link criado na mesma linha por `cp -a`, `cp -P`, `cp -d`, `cp -r`, `cp --no-dereference`, `rsync -a`, `tar -x` ou `python3 -c os.symlink` passa e grava o pedido da pasta mãe (S21, bash real). O texto diz que o link criado na linha recusa. Porta que já existe na develop (S22).

## Sondas
- S18 · sessão do Forge, forge:tech-lead, link `$TMPDIR/f/.forge-contrib/wt/x` → `~/.forge-contrib`, Bash `HOME=$TMPDIR/f; echo x >> ~/.forge-contrib/wt/x/docs/pedidos/v1.md` · espera: rc 2 · obtido: rc 2 (0f4facab: rc 0)
- S19 · o mesmo, Bash `HOME=$TMPDIR/f; echo x >> $HOME/.forge-contrib/wt/x/docs/pedidos/v1.md` · espera: rc 2 · obtido: rc 2 (0f4facab: rc 0)
- S20 · sessão do Forge, forge:tech-lead, Bash `ln -s ~/.forge-contrib ~/.forge-contrib/wt/q && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` · espera: rc 2 · obtido: rc 2 (0f4facab: rc 0)
- S21 · sessão do Forge, forge:tech-lead, link `$TMPDIR/l` → `~/.forge-contrib` plantado antes, Bash `cp -a $TMPDIR/l ~/.forge-contrib/wt/q && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` · espera: rc 2 · obtido: rc 0 (0f4facab e d4f0b10a: rc 0; bash real: grava o pedido da pasta mãe)
- S22 · develop d4f0b10a, sessão do Forge, forge:tech-lead, Bash `echo x >> ~/.forge-contrib/docs/pedidos/v1.md` · espera: rc 0 (a develop não tem a trava) · obtido: rc 0 (head: rc 2)

## Detalhe dos achados

### Achados anteriores: estado no head 7a739fca
A1 a A15 seguem como na rodada `0f4facab`: o delta não toca o código deles.

| Achado | Estado | Prova |
|---|---|---|
| A16 | fechado | S18 e S19 recusam. Recusam também `export HOME`, `read HOME`, `declare HOME`, `printf -v HOME`, `env HOME=`, `HOME+=`, `unset HOME`, `typeset -n r=HOME`, `n=HOME; declare $n=`, `H"O"ME=`, `H\OME=`, `HO\` + quebra, `HOME=…; cd ~/…/wt/x && … docs/briefs/`, `HOME=… bash -c '…'`, a forma sem `$` (`HOME=~/.forge-contrib/wt/g; …`), `source`, o ponto e `BASH_ENV=`. No `0f4facab`, desta lista só recusavam as formas partidas por aspas, barra ou continuação e a do `$n`. |
| A17 | fechado nas formas da lista | S20 recusa, como `ln -s …/docs …/wt/q`, `/bin/ln`, `mv` de link plantado, `cp -s` e `cp -as`. O que segue aberto da mesma dimensão é o A18. |

### A18: o link criado na linha por programa fora da lista
**Evidência.** `CAMINHO_TROCADO_NA_LINHA` (`hooks/conformidade.py:3823`) só conhece `ln`, `link`, `mv`, `install`, `rename` e o `cp` com `s` ou `l` nas flags. Outros programas criam a entrada como link, copiando um link plantado antes em `$TMPDIR` (que não cita `pedidos`). Rodei no hook do head e no bash real (árvore falsa no meu TMPDIR). Nos dois, as formas abaixo dão rc 0 e gravam o pedido da pasta mãe:
- `cp -a`, `cp -P`, `cp -d`, `cp -r` e `cp --no-dereference` de `$TMPDIR/l`;
- `rsync -a $TMPDIR/l ~/.forge-contrib/wt/q`;
- `tar -C ~/.forge-contrib/wt -xf $TMPDIR/l.tar`;
- `python3 -c 'import os;os.symlink(…)'`.

`git -C $TMPDIR/r worktree add ~/.forge-contrib/wt/q` também passa no hook, mas não o provei no bash real.

**Classificação pelo critério da trilha.** É recomendado. A porta já existe, mais larga, na develop. Ali o tech-lead grava o pedido da pasta mãe direto (S22, rc 0 no hook da `d4f0b10a`; o mesmo vale para `docs/briefs/b1.md`). A trilha também não a reabre: as oito formas já davam rc 0 no `0f4facab`. O defeito novo do head está no texto: `docs/hooks.md:56` diz que o link criado na mesma linha recusa (A17), o que vale só para os programas da lista.

**Ataque.** Quem ataca é o subagente que não é o jarvis e quer gravar no pedido uma linha `entrega conferida` ou `DECISÃO DO DONO` (VV-2). São dois comandos, e o sandbox não cobre o caminho (A14). Severidade média, igual à do A16. Na develop, porém, basta um comando (S22).

**Correção mínima (cartão, dono: tech-lead, esforço P).** Há duas saídas, à escolha do dono:
- declarar o limite em `docs/hooks.md:56`. Trocar "o link criado na mesma linha recusa (A17)" por "recusa o link criado na mesma linha por `ln`, `link`, `mv`, `install`, `rename`, `cp -s`, `cp -l`, `cp --symbolic-link` e `cp --link`; segue aberto o link copiado ou extraído na mesma linha (`cp -a`, `-P`, `-d`, `-r`, `-R`, `--no-dereference`, `--preserve=links`, `rsync`, `tar -x`, `cpio`, `unzip`, `git worktree add`, `os.symlink` no interpretador)";
- ou somar essas formas a `CAMINHO_TROCADO_NA_LINHA`, com fixtures `cpb-*-bloqueia`, e medir de novo o custo do corpus.

### Confirmações pedidas (head 7a739fca)
**(1) A mudança só aperta frente à develop (`d4f0b10a`)?** Sim, confirmo por escrito.
- **Sondas.** Nas 58 sondas, nenhuma foi de rc 2 na develop para rc 0 no head. Nenhuma foi de 2 no `0f4facab` para 0 no head.
- **Fixtures.** Das 3196 fixtures de `tests/hooks/` da develop, nenhuma mudou de código esperado no head. A única que sumiu é a `oraculo-limite-python-c-libera`, renomeada para `-bloqueia` (de 0 para 2), como já registrado.
- **Fixtures `libera` novas.** As 48 (`cpb-*`, `idx-*`, `sub-*`) dão rc 0 também no hook da develop, então nenhuma exige afrouxar.
- **Delta de código.** Só soma recusa:
  - `sem_copia_de_wt` ganha dois `return texto`, que tiram a exceção;
  - a conferência de `$` passa a ler o texto antes da troca, o que estreita;
  - `GuardaDaProva.bash` só chama `barrar` e depois o `bash` de antes.
- **Fixtures do delta.** As 9 `-bloqueia` dão rc 0 no `0f4facab` e rc 2 no head. As 2 `-libera` dão rc 0 nas três árvores.
- **Custo de uso, sem porta.** A trava nova recusa, para quem não é o jarvis, a leitura do pedido do clone quando a linha traz uma das palavras da lista: `cd ~/.forge-contrib/wt/x && grep -n link docs/pedidos/v1.md` dá rc 2 (na develop, rc 0). Isso é fechar na dúvida, como `docs/hooks.md:56` já declara para a mensagem de commit. Não é achado: aperta, sem caminho de ataque. A leitura pelo Read segue livre.

**(2) Custo do corpus abaixo de 0,1% e vindo de trava nova que só aperta?** Sim, confirmo. Rodei `test_corpus_nos_dois_hooks`, instrumentado só para imprimir a contagem, na mesma máquina, com Python 3.12.3, 557 execuções e 233 variáveis.

| Árvore | `interpretador` |
|---|---|
| develop `d4f0b10a` | 5887565 |
| head `7a739fca` | 5893043 |

A diferença é +5478 passos, a mesma do autor e a da rodada `0f4facab`. Os absolutos mudam com o tamanho do TMPDIR. A conta dá 5478 / 5887565 = 0,0930% aqui e 0,093% nos números do autor, abaixo de 0,1% nos dois. O delta `0f4facab..7a739fca` soma +0 ao corpus: `CAMINHO_TROCADO_NA_LINHA` só roda em `sem_copia_de_wt` e na `GuardaDaProva`, que o corpus não alcança. Os +5478 vêm das travas da `e48a2e60`, que só recusam frente à develop (item 1). O teste passou (OK) nas duas árvores.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas, todas locais:
- o lançador de fixtures de `tests/test_hooks.py`, nas três árvores;
- `test_corpus_nos_dois_hooks`, na develop e no head;
- o bash real numa árvore falsa no TMPDIR próprio, para S21 e as variantes do A18. Nenhuma pasta de controle real foi tocada.

Lacunas: gitleaks, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow, dependência nem segredo.
