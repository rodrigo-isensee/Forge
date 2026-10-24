---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: e8b2af94d1e21a16899980910665d50e20404b2e
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-leitura-hook (revalidação 12, volta do A1 da revalidação 11)

Pedido RET-LEITURA-HOOK-E-REV, etapa E2.1. Escopo: a volta do A1 da revalidação 11 (classe "lançador que divide texto", `env -S`) sobre a opção C da revalidação 10 (decisão "C" do dono, 2026-10-24).
- A volta está em `414ddd3` (corpus ES1 a ES17 e FD16), `debd17d` (`env_divide_texto` e a recusa sem dividir), `ef4c030` e `e8b2af9` (textos de `docs/hooks.md:95` e do changelog).
- O parecer anterior é a revalidação 11, sobre `182f928` (commit do parecer `a143cf4`). `forge-check delta --parecer` lista o intervalo `182f928..e8b2af9`: `hooks/_comum.py:1800-1843,1858-1859,1890-1891,2258`, `docs/hooks.md:95`, o corpus (`tests/fixtures/heredoc-volta-unica.json:258-279`), as duas fixtures `tests/hooks/conformidade/contrib-remoto-nomeado-proprio-*.json:25` e `tests/test_hooks.py:1954-1956,2393-2466,2553-2625`. Reli tudo isso inteiro. Reli também `hooks/_comum.py:1736-1790` (`LANCADORES`, `opcoes_do_lancador`, `separar_lancadores`) e `:1948-1962` (`valor_do_split_string`): o delta não os toca, mas eles leem as mesmas opções do `env`.

**critério mudou:** não. Vale a frase de parada do desenho `docs/propostas/lote-leitura-hook-volta-unica.md` (linha 282, lida com a linha 276). Desde esta volta, `docs/hooks.md:95` promete também que, com o marcador, "o `env` com a opção de dividir texto (`-S`, sozinho ou num grupo curto como `-iS`, `--split-string` e toda abreviação que o GNU env aceita …) recusa como `env -S`".

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: os hooks `conformidade` e `parecer`. Eles guardam R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados
- A1 (bloqueante) hooks/_comum.py:1747 · classe "lançador que divide texto" (2.ª volta seguida): a opção curta -a ARG do GNU env (9.x) e do uutils falta em ENV_COM_VALOR_CURTA; env_divide_texto para no ARG e env -a x -S 'X=1 bash' -c '<linha>' sai 0 / 0, e o env real roda a sentinela (11 formas)
- A2 (recomendado) hooks/_comum.py:1740 · leitor de base (cartão R5A-COP): LANCADORES["env"] também não tem -a nem --argv0; env -a x git push origin X:main sai 0 / 0 e env -a x -S 'git push forge feature/x' passa o R-CONTRIB, igual à develop
- A3 (recomendado) hooks/parecer.py:117 · leitor de base (cartão R5A-COP): o parecer não pula lançador; env, sudo e nice antes de gh pr merge saem 0, igual à develop, e docs/hooks.md:95 diz que os lançadores são seguidos
- A4 (recomendado) hooks/conformidade.py:58 · lançador que entrega texto ao shell (cartão N-HOOK1, "programas que não são shell"): flock -c, script -c, watch, su -c, runuser -c, tmux e ssh saem 0 no parecer, e os cinco últimos também no conformidade
- A5 (recomendado) hooks/parecer.py:28 · marcador ofuscado (X3, cartão C8): env -S 'git\_push\_forge\_feature/x' não tem o marcador de nenhum dos dois CRITICO e passa; o GNU env roda o push

## Detalhe dos achados
Há um bloqueante, nesta passada só.

Como sondei:
- todas as sondas rodaram contra os hooks reais da worktree em `e8b2af9`, com o vigia de produção (3 s), no modelo de fixture do corpus (`Fixture`, `rodar` e `modelos_montados` do próprio teste);
- repeti as mesmas sondas contra a base `9c9014d`, numa cópia de `git archive` em `$TMPDIR`, com os testes de `e8b2af9`;
- o efeito foi provado com o `env` real (GNU `gnuenv` 9.x e uutils 0.8.0), com `git` e `gh` registradores, `env -i`, `HOME` e a pasta em `$TMPDIR/security-engineer-lote-leitura-hook/` e sem rede.

As células são conf / par.

### O A1 da revalidação 11: fechado em 42 grafias, aberto pela opção `-a`
- **O que fecha.** Além das ES1 a ES17 do corpus, 42 grafias saem 2 / 2, pela recusa `env -S` ou pela regra específica que fala antes dela:
  - o `-S` sozinho, colado (`-S'…'`) ou em grupo (`-vS`, `-iS`);
  - o `-S` depois de `-v`, `--debug`, `--ignore-environment`, `--null`, `-0`, `--block-signal`, `--ignore-signal`, `--default-signal=PIPE` ou `--list-signal-handling`;
  - o `-S` depois de opção com valor modelada: `-u X`, `-uX`, `--unset X`, `--un X`, `--unset=X`, `-C /`, `-C/`, `--chdir /`, `--ch=/`, `--argv0 x`, `--a x`, `--argv0=x` e `-ax`;
  - o valor que parece opção: `-C -S -S`, `--argv0 -S -S` e `-a -c -S`;
  - as abreviações `--s`, `--sp=`, `--split`, `--spl=` e `--split-s=`;
  - a opção entre aspas ou escapada: `"-S"`, `-\S` e `'--split-string'`;
  - o `env` em outra grafia ou posição: `/usr/bin/env`, `e\nv`, `"env"`, `en''v`, `coreutils env`, `true | xargs env`, `timeout 5 env`, `sudo env` e a palavra `'-v -S'`.
- **O que fica aberto (A1).**
  - O GNU env 9.x tem a opção curta `-a` ("-a, --argv0=ARG", em `gnuenv --help`), que leva a palavra seguinte. O uutils 0.8.0 também tem (`-a, --argv0 <a>`).
  - Ela não está em `ENV_COM_VALOR_CURTA` (`hooks/_comum.py:1747`, `set("uCS")`). Então `env_divide_texto` (`:1805-1830`) toma o valor do `-a` como a primeira palavra que não é opção e devolve falso antes de chegar ao `-S`.
  - A forma longa `--argv0` está em `ENV_LONGAS_COM_VALOR` e recusa. Só a curta escapa.
- **Sondas: 11 formas saem 0 / 0 nos dois hooks.**
  - As formas: `env -a x -S 'X=1 bash' -c '…'`, `env -a x -S 'bash\_-c' '…'`, `env -a x -S'bash -c' '…'`, `env -a x --split-string='bash -c' '…'`, `env -ia x -S 'bash -c' '…'`, `env -i -a x -S 'bash -c' '…'`, `env -a x -v -S …`, `env -a '' -S …`, o `-a` e o valor separados por tab, `timeout 5 env -a x -S …` e `x=$(env -a x -S …)`.
  - Com o `env` real, o bash rodou `git push origin SENTINELA:main` ou `gh pr merge SENTINELA --merge` em 9 delas.
  - Nas duas com `-i`, o `env` limpa o `PATH` e roda o `git` real. Ele falhou com "not a git repository", numa pasta de `$TMPDIR` sem rede.
  - As 11 formas saem 0 / 0 também na base `9c9014d`. Não é regressão, e o piso da M5 se mantém.
- **Por que é Promete.**
  - `docs/hooks.md:95` promete a recusa para o `-S` "sozinho" com o marcador. Aqui o `-S` está sozinho, depois de uma opção do próprio `env`.
  - A palavra que roda é `bash -c`, lançada pelo `env`, como no A1 da revalidação 11.
- **Por que o gerador não viu.** A dimensão "lançador que divide texto" (`tests/test_hooks.py:2553-2570`, `OPCOES_DE_DIVISAO`) só põe o `-u X` antes do `-S`. Falta a dimensão "opção do env com valor antes da opção de dividir": `-a`, `-C` e `-u`, nas formas separada e colada, e as longas.
- **Caminho de ataque.**
  - Um agente, por engano ou por injeção de prompt, escreve `env -a x -S 'X=1 bash' -c 'git push origin HEAD:main'` ou `env -a x -S 'bash\_-c' 'gh pr merge 12 --merge'`.
  - Os dois hooks liberam. O push vai à `main` sem o R-MAIN do hook, ou o PR é mesclado sem parecer (R-REVIEW, R-QA).
  - Restam a proteção de branch e o `pre-push`.
- **Severidade:** alta, a mesma do A1 da revalidação 11.
- **Correção mínima,** esforço P.
  - Mínima: uma fonte única das opções do `env` com valor, usada por `env_divide_texto`, `LANCADORES["env"]` e `valor_do_split_string`. Ela põe o `a` entre as curtas e o `--argv0` entre as longas (o optstring do GNU é `a:C:iS:u:v0`).
  - Mais robusta, na lógica da opção C: com o marcador, recusar o `env` que tenha a opção de dividir em qualquer palavra até o `--`, sem andar pelas opções. O falso positivo novo seria `env cmd … -S …` com o marcador, que é raro.
  - Nos dois caminhos, a dimensão nova acima entra no gerador e as 11 formas entram no corpus.
- **Dono:** `tech-lead`. O caminho é do `software-architect` com o dono (abaixo).
- **Contagem de voltas.** É a mesma classe do A1 da revalidação 11, na volta seguinte. Pela decisão "A" do dono (2026-10-22), a entrega para: o `software-architect` propõe o caminho e o dono decide (R-DECISAO).

### As duas fixtures trocadas
As fixtures `contrib-remoto-nomeado-proprio-libera.json:25` e `-bash-c-bloqueia.json:25` trocaram `env -S 'git push origin feature/x'` por `env X=1 git push origin feature/x`. Rodei as duas linhas antigas na mesma montagem, um projeto com o remoto `forge`.
- **A troca era necessária.** As duas linhas antigas saem 2 pela recusa `env -S`, que é o FD16 e o comportamento prometido. Na `-bash-c-bloqueia`, o `env -S` à esquerda tomaria a mensagem do `bash -c` que a fixture confere.
- **A troca não esconde um caso que deveria recusar.** Saem 2:
  - `env -S 'git push forge feature/x'`, pelo R-CONTRIB;
  - `env -S 'git push forge HEAD:main'`, pelo R-MAIN;
  - `env -S 'GH_REPO=rodrigo-isensee/Forge gh pr merge 3'`, pelo R-CONTRIB.
- **A exceção é o `-a` do A1 e do A2.** `env -a x -S 'git push forge feature/x'` e `env -a x -S 'GH_REPO=… gh pr merge 3'` saem 0, e o GNU env roda o push.

### A2 a A5: recomendações, iguais na base `9c9014d`
- **A2 (leitor de base).**
  - `LANCADORES["env"]` (`hooks/_comum.py:1740`) não tem `-a` nem `--argv0`. Por isso `separar_lancadores` toma o `x` de `env -a x git push origin SENTINELA:main` por comando, e a linha sai 0 / 0.
  - O GNU env roda o push com o `git` real (`gnuenv -a x git --version` funciona).
  - Sem reavaliação, é do leitor de base: cartão R5A-COP, linha 282 do desenho. A correção é a mesma do A1.
- **A3 (leitor de base).**
  - O `analisar` do `parecer` (`hooks/parecer.py:117`) só reconhece o `gh` na primeira palavra, sem `separar_lancadores`.
  - `env gh pr merge SENTINELA --merge`, `env X=1 …`, `env -u x …`, `sudo …` e `nice …` saem 0 no `parecer`. A linha direta sai 2.
  - `docs/hooks.md:95` diz que os "lançadores (`env`, `sudo`, …) são seguidos". Isso vale para o `conformidade`, não para o `parecer`.
  - Proponho ao `software-architect` levar isso ao cartão R5A-COP e corrigir a frase no PR que tratar o cartão.
- **A4 (lançador que entrega texto ao shell).**
  - Saem 0 no `parecer`: `flock f -c '…'`, `flock --command`, `flock f --co`, `script -qc '…'`, `watch`, `su -c`, `runuser -c`, `tmux new -d '…'` e `ssh localhost '…'`.
  - No `conformidade`, o `flock` e o `script` recusam pela lista `LANCADORES_RECUSADOS` (`hooks/conformidade.py:58`), mas só na sessão de projeto. Os outros saem 0.
  - Com o programa real e registradores, `flock f -c 'gh pr merge SENTINELA --merge'` e `script -qc '…' /dev/null` rodaram a sentinela.
  - A linha 282 do desenho põe "os programas que não são shell" no "Não promete". É cartão N-HOOK1, e proponho a dimensão "lançador que entrega texto ao shell" para a matriz.
- **A5 (marcador ofuscado).**
  - No `-S`, o `\_` separa palavras. O `\b` dos dois `CRITICO` (`hooks/conformidade.py:42`, `hooks/parecer.py:28`) não casa `git\_push` nem `pr\_merge`.
  - `env -S 'git\_push\_forge\_feature/x'` sai 0, e o GNU env roda `git push forge feature/x`.
  - É o X3 (cartão C8), igual à `develop`. A correção do A1 por recusa sem andar pelas opções não o fecha, porque aqui não há marcador.

### O resto do delta
- `contorno_da_reavaliacao` (`hooks/_comum.py:1890-1891`) e a mensagem do vigia (`:2258`) só mudam texto. O vigia de 3 s segue em falha fechada.
- `reavaliacao_das_palavras` não divide mais o `-S`. O `separar_lancadores` ainda divide o valor com `shlex`, para as regras específicas (o R-MAIN e o R-CONTRIB acima), e a recusa `env -S` vem depois delas. Não achei caminho em que a divisão do `shlex` libere o que a recusa pegaria, porque a recusa não depende dela.
- Tempo: todas as sondas decidiram entre 0,11 s e 0,27 s.

### Os riscos que o autor declarou
- O FD16 (`env -S 'echo x'; git push origin feature/x` recusa) é o falso positivo esperado da recusa, com o contorno no corpus (FD16c e FD16d dão 0).
- O teste `test_divisao_esta_na_classe` depende de um GNU env na máquina e pula sem ele. Aqui o `gnuenv` existe, e o teste roda.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas:
- `forge-check delta --parecer docs/security/lote-leitura-hook.md`;
- `python3 -m unittest tests.test_hooks.CorpusHeredocVoltaUnica -v`: `Ran 17 tests in 514.042s`, `FAILED (failures=3)`, as três em `test_g1_esta_na_classe` (o oráculo do oráculo, com os hooks desligados: o registro do bash veio vazio em `! "ksh" "-c" …`, `command bash -c …` e `exec $'\x72'bash $'\x2d'c …`), com a máquina em carga 9; o mesmo teste sozinho deu `Ran 1 test in 15.004s`, `OK`. A falha é do lado seguro (o teste fica vermelho, nenhum hook libera) e não muda o veredito; as outras 16 passaram, entre elas as duas propriedades do lote e `test_divisao_esta_na_classe`;
- as sondas, por um script próprio sobre `Fixture`, `rodar` e `modelos_montados` do próprio teste: 64 formas × 2 hooks na branch e na base, mais 12 formas do `-a` sem `-S` e 10 linhas nas fixtures trocadas;
- o `env` real (GNU `gnuenv` e uutils 0.8.0), o `flock` e o `script` com registradores, e o bash 5.3.9, com `HOME` em `$TMPDIR/security-engineer-lote-leitura-hook/`, sem rede e sem custo (`R-CUSTO`).

Lacunas:
- Não há BSD env, macOS nem `sudo` na máquina.
- `su`, `runuser`, `watch` (sem terminal), `tmux` e `ssh` não rodaram de verdade. O A4 só cita o efeito provado no `flock` e no `script`.
- A suíte inteira não rodou fora do pre-push (`R-TETO`).
- `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH e não se aplicam ao delta, que não tem segredo, workflow nem dependência.

Nada foi instalado e nada saiu da máquina. Além deste parecer, só gravei em `$TMPDIR`.
