---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-conformidade
commit: b96cab3cbfbb3f625f6cb1732a018a8178f8c92c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E113.17, 3ª volta do hooks/conformidade.py)

Revalidação por delta (`forge-check parecer delta`, intervalo `bf57b17e..b96cab3c`, sem o que veio da develop). No domínio: `hooks/conformidade.py` (`FIM_DE_LISTA`, `PIPE`, `VOLTA_NO_TIL`, `ALVO_DO_T`, `COPIA_RECURSIVA`, `alvo_do_t`, o `conferir_partes` com as pastas do começo de cada lista, a volta de pasta como pasta desconhecida, a extração para opaco e o `rsync` no `origem_do_git_no_opaco`), as fixtures `a5-resto-*`, `a6-*`, `a7-*`, a u4 invertida e `tests/test_conformidade_seg_v0480.py`. Fora do domínio, não relidos: o fragmento do changelog, `docs/hooks-fixtures.md`, os mutantes 7 a 9 e `tests/pesos-d4.json`. A rodada anterior (parecer ec727021 sobre bf57b17e) está no git.

Gatilhos: guarda de controle (hook conformidade), R-MAIN, R-VERIFY, escrita no diretório do git.

Método: 109 sondas com o montador das fixtures (`tests/test_hooks.py`), na cabeça e na base bf57b17e, e a semântica do bash conferida num repositório descartável (`cd -- -` volta ao OLDPWD; `coproc`, `{ …; } | …` e `{ …; } &` não mudam a pasta de fora). O teste novo `tests/test_conformidade_seg_v0480.py` passa (15 testes). A suíte inteira roda só no CI do PR, que ainda não existe para esta branch: ele é o portão da suíte (`R-REVIEW`) antes do merge.

## Achados anteriores
- A6 (cd em subshell implícito): **fechado** (hooks/conformidade.py:2330). Os seis casos do parecer anterior recusam, com R-MAIN ou R-REVIEW. Também recusam `cd /tmp || true & …`, `true | cd /tmp | true; …`, `! cd … |`, `time cd … |`, `cd /tmp &` seguido de quebra de linha, `cd /tmp >/dev/null & …`, `cd /tmp 2>&1 | …`, `(cd /tmp & true); …`, `coproc cd /tmp; …` e `{ cd /tmp; }` com `|` ou `&`. As chaves recusam pela regra delas. Todas essas formas passavam na base. `cd /tmp; (cd / & true); git push` e `cd /tmp & cd /; git push` seguem livres, e está certo: o bash roda o push fora do repositório. O corpus segue livre: `cd docs & ls`, `cd /tmp && git status`, `ls | grep x; git status` e `git log … | head; git status`.
- A7 (volta de pasta): **fechado** pela alternativa que falha fechado (hooks/conformidade.py:2315, 2512 e 2521). Recusam `cd -`, `cd ~-`, `popd`, `pushd` sem pasta, `pushd +1`, `pushd -1`, `cd -- -`, `cd -P -`, `builtin cd -`, `command cd -`, `cd ~1`, `cd - >/dev/null &&`, a quebra de linha e `popd -n`, todos livres na base. `cd "$OLDPWD"` e `${OLDPWD}` com ação crítica recusam pela regra da variável, na cabeça e na base. `eval cd -` recusa pela regra do `eval`.
- A5 (resto): **fechado** (hooks/conformidade.py:1297 e 1894). Recusam `--recur`, `--arch`, `--arc`, `-rt"$X"`, `-Rvt"$X"`, `-t"$X"`, `-vt "$X"`, `--targ`, `--target-dir`, `--target-dir=`, `--target-d=`, `-t "$X" --` e `-T -r --`, todos livres na base. O corpus segue livre: `cp ev/a "$X"`, `cp -r docs "$(mktemp -d)"` e `cp -T ev "$HOME"t`.
- A8 (extração para opaco): **fechado** (hooks/conformidade.py:2604 e 2618). Recusam `tar -C "$X"`, `-C"$X"`, `--directory=`, `--direc`, `unzip -d` (separado e colado), `bsdtar`, `gtar`, `busybox tar`, `7z -o"$X"`, `git archive | tar -x -C "$X"` e `rsync -r`, `-a`, `--recursive` e `-rt`, todos livres na base. Seguem livres `tar -C "$TMPDIR/x"`, `unzip -d /tmp/x`, `rsync -a ev/ /tmp/x`, `rsync -av docs/ "$X/sub"`, `rsync -t ev/a "$X"` e `tar -cf a.tar -C "$X" .`. `tar -C "$(mktemp -d)"` e `d=$(mktemp -d); tar -C "$d"` recusam pela regra do destino calculado, como na base.

## Decisões pedidas (E113.17)
**`cd docs; cd -; git status` recusado: fica.** O A7 do parecer anterior oferecia esta alternativa, a que falha fechado, e ela pesa menos que modelar o OLDPWD e a pilha do `pushd`. O falso positivo é estreito: só o comando que vem depois da volta, na mesma linha. A volta no fim da linha e a de dentro de `( … )` seguem livres (fixtures `a7-cd-menos-no-fim-*` e `a7-cd-menos-no-subshell-libera`). A mensagem diz o que fazer (`cd` com o caminho). A frase do meu parecer anterior que dizia que esse comando "segue livre" fica revogada aqui; a decisão é minha, não do autor. O mesmo vale para `cd ~+`, que recusa sem necessidade (`~+` é a pasta corrente): o custo é aceitável e não pede correção.

**Inversão da fixture u4: fica.** `cp -rT ev "$HOME"t` recusa pelo A5: a cópia é recursiva, o valor vem de fora da linha e `ev/config` entra no destino. Isso não é regressão do A16 (E1.340), que tratava só de nome do ambiente com resto colado. A forma sem `-r` (`cp -T ev "$HOME"t`) segue livre e conserva o que o A16 protegia. As duas sondas conferem na cabeça. A decisão é minha, não do dono.

## Detalhe dos achados
Sem achado no delta.

**Cartão novo, fora do delta (pré-existente na base bf57b17e, não segura esta branch):** a cópia recursiva com destino literal grava o `.git` da raiz sem que o hook veja os nomes. Num fixture com `tp/.git/config` e `tp/.git/hooks/pre-push`, estas formas ficam livres na cabeça e na base, papel tech-lead, em `melhoria/x`: `cp -a tp/.git .`, `cp -r tp/. .`, `cp -rT tp .`, `rsync -a tp/ ./` e `cp -r tp/. docs/..`. Já `cp tp/.git/config .git/config` e `cp -r tp/.git/hooks .git/` recusam.

Caminho: um agente roda `git init tp` (ou `git clone` de um modelo) e depois `cp -r tp/. .`. O `.git/config` do projeto passa a ser o do outro repositório, sem o `core.hooksPath` (R-VERIFY), e os hooks do git são trocados. O idioma "copiar o modelo para a raiz" é comum, então o risco é realista também por acidente. Severidade: alta.

Correção mínima: no `cp`, no `rsync` e nos extratores recursivos, se a origem tem um componente `.git`, ou se a pasta de origem contém `.git` em disco, a cópia para um destino que resolve na raiz do projeto (ou num pai dela) recusa como a escrita em `.git/`. Pela matriz, a dimensão "programa que grava nomes do conteúdo" passa a valer também para destino literal, não só para opaco. Esforço: P. Dono: o dono do hook conformidade, num item novo que o Jarvis abre. Eu devia ter achado isso na varredura da família A5; registro a falha.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: o delta do `forge-check`, o montador das fixtures (cabeça e base extraída por `git archive`) e o bash num repositório descartável. Nenhuma varredura externa. As tabelas das sondas ficaram só na área de rascunho desta sessão.
