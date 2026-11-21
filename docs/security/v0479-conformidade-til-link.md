---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 481d2855dbf0acc7c9fc9ec09d35ad8bf5d87e24
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-conformidade-til-link (v0478 E80.3)

Delta revisado: `adc52def..481d2855` (hooks/conformidade.py, corpus `tilsubst-*` e `linkcopia-*`, mutantes T1-T5, L1-L6 e W8, `tests/test_conformidade_verde.py`).

## Gatilhos
Gatilhos: controle do Forge (hook `conformidade`), escrita em arquivo em vigor e na pasta de controle

## Resultado
A mudança **só aperta**. Cerca de 130 sondas rodaram no hook da base (`adc52def`) e no do head, com o mesmo fixture: nenhuma passou de recusa (2) para liberação (0). Todas as diferenças vão de 0 para 2. As duas linhas `tar -x` que saíram da lista de liberação de `EstadoDoAgentesNoClone` agora recusam em `test_tar_x_na_linha_que_cita_o_estado_recusa`, o que aperta, sem afrouxar nada. O mutante W8 está alinhado: o `de` aparece uma vez no head, continua tirando só o ponto como programa, e o teste `test_fixtures_do_controle_so_jarvis` falha com ele aplicado (rodado numa cópia em `$TMPDIR`). Os testes novos (`test_fixtures_do_til_em_substituicao`, `test_fixtures_do_link_por_copia` e `EstadoDoAgentesNoClone`) passam no head.

Os dois buracos ainda não estão fechados na família deles. Os casos das sondas zy-1 e A18 recusam, mas variantes vizinhas do mesmo mecanismo ainda gravam o arquivo protegido (A1, A2). Por isso o parecer é `reprovado`. Ainda não há PR nem CI para este head, e a suíte inteira não rodou aqui.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1694 · o valor calculado só cobre a atribuição única com `~`: `$HOME`, `$PWD` e `$CLAUDE_PROJECT_DIR` na atribuição viram SEM_VALOR e são descartados; reatribuição, `for` e `read` dão None (linhas 775 e 778) e liberam. Ver S1 a S5.
- A2 (bloqueante) hooks/conformidade.py:3834 · o link criado por cópia escapa da lista: opção longa abreviada (`tar --ext`, `cp --arch`, `--recur`, `--no-deref`, `--sym`), barra invertida (`cp -\a`, `ta\r`, `tar -\xf`, linha 3898) e extrator ou interpretador fora dela (unzip, cpio, 7z, pax, bsdtar, gtar, `symlink` sem parêntese). Ver S6 a S12.
- A3 (recomendado) hooks/conformidade.py:1693 · a variável com `~` usada dentro do texto de `-c` do interpretador (`d=~/.claude; <interp> -c "open('$d/settings.json','a')"`) libera, e o caminho literal no mesmo lugar recusa. Isso é uma dimensão nova da matriz: a posição dentro do argumento do interpretador.

## Sondas
- S1 · tech-lead, fixture tilsubst-variavel-bloqueia: `d=$HOME/.claude; echo x >> "$d/settings.json"` · espera: código 2 · obtido: código 0 (na base e no head)
- S2 · mesmo fixture: `d=$PWD/.claude; echo x >> "$d/settings.json"` (e `d=$CLAUDE_PROJECT_DIR/.claude; …`) · espera: código 2 · obtido: código 0 (na base e no head)
- S3 · mesmo fixture: `d=~; d=$d/.claude; echo x >> "$d/settings.json"` (e `d=~/.claude; d=$d; …`, `d=~/.cla; d=${d}ude; …`) · espera: código 2 · obtido: código 0
- S4 · mesmo fixture: `for d in ~/.claude; do echo x >> "$d/settings.json"; done` · espera: código 2 · obtido: código 0
- S5 · mesmo fixture: `read d <<< ~/.claude; echo x >> "$d/settings.json"` · espera: código 2 · obtido: código 0
- S6 · tech-lead, fixture linkcopia-tar-x-bloqueia: `tar --ext -f ~/l.tar -C ~/.forge-contrib/wt && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` · espera: código 2 · obtido: código 0
- S7 · mesmo fixture, mesmo `&& echo x >> …/wt/q/docs/pedidos/v1.md`: `cp --arch ~/q ~/.forge-contrib/wt/` (e `--recur`, `--no-deref`, `--sym`) · espera: código 2 · obtido: código 0
- S8 · mesmo fixture e sufixo: `cp -\a ~/q ~/.forge-contrib/wt/` (e `c\p -a`, `ta\r -xf ~/l.tar`, `tar -\xf ~/l.tar`) · espera: código 2 · obtido: código 0
- S9 · mesmo fixture e sufixo: `unzip ~/l.zip -d ~/.forge-contrib/wt` (e `cpio -idm < ~/l.cpio`, `7z x ~/l.7z`, `pax -r < ~/l.pax`, `bsdtar -xf ~/l.tar`, `gtar -xf ~/l.tar`) · espera: código 2 · obtido: código 0
- S10 · mesmo fixture e sufixo: `python3 -c "from os import symlink as s; s('/a','b')"` (e `os.link(`, `.hardlink_to(`, `shutil.copytree(..., symlinks=True)`) · espera: código 2 · obtido: código 0
- S11 · mesmo fixture e sufixo: `perl -e 'symlink "/a","b"'` (e `-e "require('fs').symlinkSync('/a','b')"`) · espera: código 2 · obtido: código 0
- S12 · laboratório em $TMPDIR (pasta própria): `tar --ext -f l.tar -C t1`, `cp --arch src c1`, `cp --recur src c2`, `cp --no-deref src/lk c3` e `cp -\a ../src c4` · espera: link criado (a sonda é real) · obtido: `lk -> /etc/hostname` em todos

## Detalhe dos achados
**A1.** Evidência: hooks/conformidade.py:1693-1695 (`valores_da_palavra` só sobre o `caminho` expandido; o valor com SEM_VALOR é descartado), :775 (`for` e `read` dão None), :778 (mais de uma atribuição dá None). Caminho de ataque: um papel que não é o dono (dev, tech-lead, injetado por conteúdo lido) grava `~/.claude/settings.json` ou o `.claude/settings.json` do projeto, que são arquivos em vigor, e dá a si permissões ou hooks. Basta trocar `~` por `$HOME` ou `$PWD`, ou montar o valor em duas atribuições. A sonda zy-1 é a mesma família. Severidade: alta. Correção mínima: antes de calcular os valores, aplicar `self.expandir` também à linha (ou a cada atribuição), para que `$HOME`, `${HOME}`, `$PWD`, `${PWD}`, `$CLAUDE_PROJECT_DIR`, `${CLAUDE_PROJECT_DIR}` e `DIR_DO_GIT` entrem com o valor real. Quando o destino tem `$` ou crase, `valores_da_palavra` dá None e a linha cita um caminho de `caminhos` (o nome do alvo protegido, como `.claude`), o resultado deve falhar fechado: recusa, como no `.git` (U4). Fixtures novos: S1 a S5 e o corpus legítimo já usado (`d=~/tmp`, `$(pwd)/a.txt`, `~/.claude-notas`, `$(echo ~/.claude)-bak`, `d=~/.claude; cat …`), que tem de continuar liberando. Esforço: M. Dono: o autor do hook (forge:devops-engineer ou quem a etapa E80.1 indicar).

**A2.** Evidência: hooks/conformidade.py:3834-3838 (a regex) e :3898 (o texto só perde as aspas, não a barra invertida). Caminho de ataque: o papel que não é o jarvis cria na própria linha um link dentro de `wt/` que aponta para `~/.forge-contrib/docs`, e grava em seguida pelo link no pedido ou no brief (as linhas `DECISÃO DO DONO`). O hook resolve o caminho antes de o link existir. As ferramentas GNU aceitam a abreviação única de opção longa, e o bash tira a barra invertida (S12). Severidade: alta. Correção mínima: (1) tirar `\` junto com as aspas em `plano` e em `GuardaDaProva.bash`; (2) casar a opção longa por prefixo de 3 letras ou mais, de cada nome: `--archive`, `--recursive`, `--no-dereference`, `--link`, `--symbolic-link`, `--links` e `--extract`; (3) acrescentar os programas que restauram link: `bsdtar`, `gtar`, `cpio` com `-i` ou `--extract`, `unzip`, `7z`, `7za` e `7zr` com `x` ou `e`, `pax` com `-r`, `busybox` com `tar`, `cpio`, `unzip` ou `ln`, e `git clone`, `git checkout`, `git switch`, `git restore`, `git worktree add` e `git stash` numa linha que cite o controle; (4) no texto de interpretador (`-c` ou `-e`), recusar `symlink` e `link` como palavra, em qualquer forma (`symlink(`, `symlinkSync(`, `symlink "`, `import symlink`, `hardlink_to(`, `os.link(`, `copytree(`, `move(`), ou falhar fechado com todo interpretador numa linha que cite o controle. Fixtures novos: S6 a S11. A matriz das dimensões ganha as dimensões "forma da opção" (curta, longa, abreviada, escapada) e "programa que cria link". Esforço: M. Dono: o mesmo da A1.

**A3.** Evidência: hooks/conformidade.py:1693 (só o destino de redirecionamento ou de comando conhecido entra no cálculo). Na base e no head, a sonda `d=~/.claude; python3 -c "open('$d/settings.json','a')"` dá 0, e o mesmo texto com o caminho literal dá 2. Severidade: média. Correção mínima: na linha com interpretador e `-c` ou `-e`, expandir as variáveis que a linha atribui dentro do argumento entre aspas duplas e passar o texto pela mesma busca do caminho literal. Esforço: P. Dono: o mesmo da A1.

Falso positivo novo, aceitável e sem achado: `cp -a`, `cp -r`, `rsync -a` e `tar -x` numa linha que cita o estado (`.git/forge`), uma pasta de parecer ou o controle passam a recusar para quem não é o jarvis. `d="~/.claude"` (o `~` entre aspas, que o bash não expande) e `~usuario_inexistente` também recusam e falham fechado, como a nota do código prevê.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas: as sondas pelo `Fixture` e pelo `rodar` de `tests/test_hooks.py` sobre a base e o head, o mutante W8 aplicado numa cópia e um laboratório local em `$TMPDIR`. Lacuna: não há CI para o head (sem PR), e a suíte inteira não rodou.
