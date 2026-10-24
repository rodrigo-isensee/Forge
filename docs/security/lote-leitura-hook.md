---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 1b4b0d8b060379d6e078d5ef15c2c63676e41b87
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-leitura-hook (revalidação 13, volta pela opção A da revalidação 12)

Pedido RET-LEITURA-HOOK-F-REV, etapa E2.1. Escopo: a volta pela opção A (decisão "A" do dono, 2026-10-24, proposta `docs/propostas/lote-leitura-hook-caminho-rev12.md`). Com o marcador crítico, o lançador de `LANCADORES` só passa com as opções da tabela. O teste instável do T9b é corrigido no lote.
- A volta está em quatro commits:
  - `e8cc9e4`: a lista positiva e a recusa;
  - `f418569`: os textos da seção 4.1 em `docs/hooks.md:95`;
  - `b438b21`: os registradores do T9b montados antes do pool;
  - o merge `1b4b0d8`, que traz a `develop` (`83d5faa`, versão 0.30.0) sem tocar em `hooks/` (`git diff e8cc9e4 1b4b0d8 -- hooks/` vazio).
- O parecer anterior é a revalidação 12, sobre `e8b2af9` (commit do parecer `60c91f8`). `forge-check delta --parecer` lista o intervalo `e8b2af9..1b4b0d8`.
- Do lado dos controles do Forge, reli inteiros:
  - em `hooks/_comum.py`: `:1738-1870` (`LANCADORES`, `opcao_modelada`, `opcao_fora_da_tabela`, `separar_lancadores`), `:1880-1975` (`achado_do_lancador`, `reavaliacao_das_palavras`, `contorno_da_reavaliacao`, `motivo_da_reavaliacao`) e `:2022-2033` (`valor_do_split_string`);
  - `hooks/conformidade.py:741-746` e `:842-856` (o `segmento`, com o papel só de leitura) e `hooks/parecer.py:401-406`;
  - `docs/hooks.md:95` e o corpus `tests/fixtures/heredoc-volta-unica.json:276-317`;
  - em `tests/test_hooks.py`, o arnês do T9b e o pool de `executar_em_lote`.
- Reli também `separar_lancadores` e `valor_do_split_string` da base `d150ec8` (`hooks/conformidade.py:390-433`), para julgar o desvio declarado ("como a `develop`"). A `develop` atual (`9e9ead2`) tem os mesmos `hooks/` da base (`git diff --stat d150ec8 9e9ead2 -- hooks` vazio).
- O resto do delta vem da `develop`, que já passou pelos portões dela (`scripts/conferir-reversao.py`, regras, modelos, agentes).

**critério mudou:** sim, pela decisão do dono.
- Desde esta volta, `docs/hooks.md:95` promete que, com o marcador, "um lançador de `LANCADORES` … em qualquer posição só passa com as opções que o hook modela, escritas por extenso e uma por palavra". Promete também que "qualquer outra palavra com `-` antes do comando recusa, sem que o hook tente lê-la".
- Conferi por substring que os três textos da seção 4.1 da proposta estão em `docs/hooks.md:95` como estão na proposta.
- A emenda da ADR 0011 ficou no cartão ADR0011-EMENDA (decisão técnica do Jarvis).

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: os hooks `conformidade` e `parecer`. Eles guardam R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA e, sem o marcador, a leitura do `.env` e o apagar do `.git`.

## Achados
- A1 (bloqueante) hooks/_comum.py:1848 · classe "opção de lançador que o hook não modela" (2.ª volta seguida), regressão sem o marcador: env -iu X cat .env, env -iC d cat .env e env -iu X rm -rf .git saem 0 e saíam 2 na develop; o env real (GNU 9.7 e uutils) imprime o .env e apaga o .git
- A2 (bloqueante) hooks/_comum.py:2030 · classe "lançador que divide texto" (3.ª volta), regressão sem o marcador: env -iS'cat .env', env -vS'cat .env' e env -iS"rm -rf .git" saem 0 e saíam 2 na develop; o GNU env roda o cat nas duas primeiras, o uutils na com -i
- A3 (recomendado) hooks/parecer.py:117 · leitor de base (cartão R5A-COP): o parecer segue sem pular o lançador com opções da tabela; env gh pr merge, env -u x gh pr merge e sudo -u -s gh pr merge saem 0 no parecer, igual à develop
- A4 (recomendado) hooks/conformidade.py:58 · lançador que entrega texto ao shell (cartão N-HOOK1): flock -c, script -c, watch, su -c, runuser -c, tmux e ssh seguem como na revalidação 12
- A5 (recomendado) hooks/parecer.py:28 · marcador ofuscado (X3, cartão C8): env -S 'git\_push\_forge\_feature/x' segue sem marcador, como na revalidação 12
- A6 (recomendado) hooks/_comum.py:1905 · palavra com expansão antes da opção do lançador (Não promete, cartão N-HOOK1): env $(echo -a) x git push origin SENTINELA:main sai 0 / 0 e o env real roda o push

## Detalhe dos achados
Há dois bloqueantes, nesta passada só, os dois no caminho sem o marcador. Com o marcador, o A1 da revalidação 12 e a classe "opção de lançador que o hook não modela" fecharam por construção nos dois hooks.

Como sondei:
- as sondas com marcador rodaram contra os hooks reais da worktree em `1b4b0d8`, com o vigia de produção (3 s), no modelo de fixture do corpus (`Fixture`, `rodar` e `modelos_montados` do próprio teste);
- as sondas sem marcador (A1 e A2) rodaram como fixture do `conformidade`, nos modelos de `tests/hooks/conformidade/env-cat-bloqueia.json` (o `.env`) e `trava-rm-projeto-bloqueia.json` (o `rm`). Rodaram na branch e na `develop` `9e9ead2`, numa cópia de `git archive` em `$TMPDIR`;
- o efeito foi provado com o `env` real (GNU 9.7 e uutils), com `git` e `gh` registradores, `env -i`, um `.env` falso e um `.git` vazio, com `HOME` e a pasta em `$TMPDIR/security-engineer-lote-leitura-hook/` e sem rede.

As células são conf / par.

### A1 e A2: o desvio declarado, sem o marcador, é regressão
- **O que o autor declarou.** Sem o marcador, `separar_lancadores` lê a opção fora da tabela como sem valor, "como a `develop`" (commit `e8cc9e4`). A proposta (seção 2, linha 47) mandava devolver "não analisável". O autor desviou para não pular as regras da linha que não dependem do marcador.
- **Julgamento: a intenção do desvio está certa, e ele é melhor que o "não analisável", mas a premissa "como a `develop`" é falsa.**
  - O "não analisável" iria a `ilegivel` (`hooks/conformidade.py:809`). Essa função só recusa o que aponta para o Forge e volta sem as outras regras. Com ela, `env --foo cat .env` e `sudo -s cat .env` deixariam de recusar. Com o desvio, as duas saem 2. Então o desvio, sozinho, não reprova.
  - A `develop` lia o grupo curto do `env` terminado em `u` ou `C` com o regex `-[a-zA-Z]*[uC]` e tomava a palavra seguinte como valor (base `hooks/conformidade.py:408`). E dividia o `-S` também no grupo curto (base `:428-432`). A decisão do dono tirou o regex e as tabelas do `env`, e nada tomou o lugar dessas duas leituras no caminho sem o marcador. A volta só segue o `-S` por extenso (`hooks/_comum.py:2026-2031`) e lê `-iu` como booleana (`:1848`).
- **Sondas sem o marcador (só `conformidade`):**

| Texto | `develop` | lote |
|---|---|---|
| `env -iu X cat .env` | 2 (ler .env) | 0 |
| `env -iC d cat .env` | 2 | 0 |
| `env -iu X rm -rf .git` | 2 | 0 |
| `env -iS'cat .env'` | 2 | 0 |
| `env -vS'cat .env'` | 2 | 0 |
| `env -iS"rm -rf .git"` | 2 | 0 |
| `env -u X cat .env`, `env -S'cat .env'`, `env -i cat .env`, `env -u X rm -rf .git` (controle) | 2 | 2 |
| `env -a x cat .env`, `env -a x rm -rf .git` | 0 | 0 |

- **Efeito real.** Com os hooks desligados, numa pasta de `$TMPDIR` com um `.env` falso, o GNU env imprime o arquivo em `-iu X /bin/cat .env`, `-iS'/bin/cat .env'` e `-vS'/bin/cat .env'` e apaga o `.git` em `-iu X /bin/rm -rf .git`. O uutils faz o mesmo nas formas com `-i`.
- **Por que é bloqueante.**
  - Não é o caso (ii) do critério de parada do lote (`docs/propostas/lote-leitura-hook-volta-unica.md:276-282`), que mede as promessas novas da seção 2.3. É defeito de comportamento provado num controle que já existia: a volta tira uma recusa que a `develop` fazia, com efeito real (`R-REVIEW`, e `R-SEGURANCA` com gatilho). O critério do lote não dispensa regressão, e o commit `e8cc9e4` afirma o contrário ("como a `develop`").
  - É a primeira vez que o achado aparece nos meus pareceres. Não é recomendação promovida.
  - O review (`c48f097`) chegou ao mesmo resultado, por sondas próprias.
- **Caminho de ataque.** Um agente, por engano ou por injeção de prompt, escreve `env -iu X cat .env` ou `env -iS'cat .env'`. O hook libera, e o segredo do projeto entra no contexto e pode sair num commit, num PR ou numa mensagem. Ou `env -iu X rm -rf .git` apaga o histórico local.
- **Severidade:** média. O alcance já existia na `develop` por `env -a x cat .env` (sai 0 nos dois lados), então o ganho de quem ataca é pequeno. O que pesa é a recusa existente que some.
- **Correção mínima,** esforço P a M, dono `tech-lead`. O caminho é do `software-architect` com o dono (abaixo), porque a decisão "A" tirou o regex e as tabelas do `env`.
  - Sem o marcador, as regras da linha leem as duas leituras possíveis da opção fora da tabela: sem valor, e com a palavra seguinte como valor; e o resto de um grupo curto com `S` como texto dividido. Recusa se uma das leituras recusa. Uma leitura a mais só recusa mais, e o hook não volta a imitar um `env`. Isso fecha também `-a x`, `-f x` e `--adj 1`, que já saíam 0 na `develop`.
  - A outra saída: também sem o marcador, recusar o lançador com opção fora da tabela quando o resto da linha toca uma regra.
  - Nos dois caminhos, as linhas da tabela entram como fixture `-bloqueia` (ou no corpus), com a leitura sem o lançador como oráculo. Proponho a dimensão "regra sem o marcador atrás de lançador com opção fora da tabela" para a matriz da família.
- **Contagem por classe** (decisão "A" de 2026-10-22):
  - A1, "opção de lançador que o hook não modela": a 1.ª volta foi a revalidação 12 (o A2 dela, `env -a x git push`), e esta é a 2.ª seguida.
  - A2, "lançador que divide texto": revalidação 11, revalidação 12 e esta, a 3.ª.
  - Pela decisão, a entrega para: o `software-architect` propõe o caminho e o dono decide (`R-DECISAO`). As duas classes já foram registradas mais de uma vez e cabem em `docs/engineering/achados-recorrentes.md` (PA-7). O brief limita o commit a este parecer, então a linha fica para o PR do lote.

### O A1 da revalidação 12 e a classe: fechados com o marcador
- **As sondas do parecer anterior: todas recusam.**
  - As 11 formas do `-a` antes do `-S` saem 2 / 2:
    - `env -a x -S 'X=1 bash' -c …`, `-a x -S 'bash\_-c'`, `-ia x -S`, `-a x --split-string=`, `-a x -S'…'` colado e `-i -a x -S`;
    - `-a x -v -S`, o `-a` e o valor separados por tab e `-a ''`;
    - `timeout 5 env -a x -S` e `x=$(env -a x -S …)`.
  - As 4 do uutils (EU1 a EU4) saem 2 / 2: o `-S` colado depois de `X=1`, de `-`, de `-i X=1` e de `-f /dev/null`.
  - Das 12 formas do `-a` sem `-S`, 10 saem 2 / 2: `env -a x`, `--argv0 x`, `--ar x`, `-ia x`, `-a x X=1`, `-ax`, `--argv0=x`, `sudo env -a x`, `env -a x bash -c` e `x=$(env -a x …)`. As outras duas são o controle, `env` simples e `env -u x` antes da linha crítica: saem 2 no `conformidade`, pela regra específica, e 0 no `parecer`, pelo A3.
  - `env -a x git push origin SENTINELA:main` sai 2 no `conformidade`.
  - As 42 grafias da revalidação 12 que já fechavam seguem 2 / 2.
- **Variantes novas: 117 formas, fora as de expansão (A6) e os legítimos.** Todas recusam nos dois hooks, salvo sete que não rodam o comando crítico (abaixo). Rodei de novo nesta retomada, e o resultado bateu linha a linha com a primeira rodada. As famílias:
  - Opção agrupada: `env -iu X`, `-i0`, `-vi`, `-0i`, `-ia x`, `-iS`, `nice -n5`, `sudo -En`, `exec -cl`, `timeout -vk 1 5`, `time -pv`, `xargs -0r`, `command -pv`.
  - Abreviação longa:
    - do `env`: `--ig`, `--ignore`, `--nu`, `--deb`, `--ch /`, `--uns X`, `--arg x`, `--ignore-environment=x` e `--debug=1`;
    - dos outros lançadores: `sudo --us root`, `sudo --use=root`, `timeout --sig KILL 5`, `timeout --preserve 5`, `xargs --max-a 1`, `stdbuf --out=L` e `nice --adj 1`.
  - `sudo -s` e `-i`:
    - as formas: `sudo -s`, `-i`, `-is`, `-u root -s`, `-E -s`, `--shell`, `--login`, `--sh`, `-su root`, `-uroot -s`, `X=1 -s`, `nice -n 1 sudo -s` e `sudo -l`;
    - o `sudo` em outra grafia: `/usr/bin/sudo`, `\sudo`, `"sudo"` e `su''do`.
  - Opção de outro `env`:
    - GNU: `--default-signal`, `--block-signal=INT`, `--list-signal-handling`, `--ignore-signal`, `-a` e `--argv0`;
    - uutils: `-f /dev/null` e `--file /dev/null`;
    - BSD: `-P /usr/bin`, `-L 0` e `-U 0`;
    - e `--help`.
  - Os outros lançadores: `nohup --x`, `nohup -`, `setsid -c`, `setsid -f`, `command -x`, `builtin -x`, `exec -x`, `time -a`, `time -v`, `nice --10`, `nice -+1`, `nice -20`, `timeout -p 5`, `timeout -f 5`, `xargs -i`, `xargs -p`, `stdbuf -x` e `timeout --signal=KILL 5 env -a x`.
  - A opção entre aspas ou escapada: `"-a"`, `'-a'`, `-\a` e `-'a'`.
  - O `env` em outra grafia: `e""nv`, `/usr/bin/env`, o tab e a barra com quebra de linha.
  - O `env` em outra posição: `true;`, `!`, `{ …; }`, `( … )`, `if`, `while`, `coproc`, `time`, `|`, `&`, `command env`, `sudo env`, `exec env`, `env -i env`, `env env`, crase, `<(…)`, `busybox env` e `coreutils env`.
  - `NOME=valor` misturado: `env X=1 -a x`, `-i X=1 Y=2 -a x`, `sudo X=1 env -a x`, `'X=1' -a x`, `X=1 -iu Y` e `-u Y X=1 --un Z`.
- **As sete que saem 0 não rodam o comando crítico.** Provei com o `env` real ou pelo argv:
  - `sudo -- -s …`: o `sudo` roda o programa `-s`. `env '' -a x …`: o `env` roda o programa vazio.
  - O valor que parece opção: `env -u -a x …`, `env -C -a x …` e `env -u -S 'bash -c' '…'`.
    - O GNU env toma o `-a` e o `-S` como valor, como a tabela. Ele roda `x` ou `bash -c` como nome de programa e falha.
    - O uutils recusa com "a value is required".
  - `xargs -n -a x` falha com "invalid number".
  - No `parecer`, `sudo -u -s gh pr merge …` sai 0 pelo A3, não pela tabela (no `conformidade`, a forma equivalente sai 2).
- **Legítimos: saem 0 / 0.** As formas: `env -i -u X`, `env X=1`, `sudo -u x`, `nice -n 1`, `timeout 5`, `stdbuf -oL`, `env -C / -i X=1` e `env --chdir=/ --unset=X`. Rodei cada uma antes de `git push origin feature/x` e de `gh pr create --draft …`.
- **A tabela contra os programas.**
  - Conferi cada lançador contra o optstring do getopt dele. Nenhuma opção marcada como booleana leva valor no programa real. Se levasse, o hook leria o valor como comando.
  - O `sudo -h` é o único caso divergente. A tabela o lê com valor, e o `sudo` só aceita o valor colado. O erro fica do lado seguro: `sudo -h git push …` mostra a ajuda, e nada roda.
- **A memória de `opcao_fora_da_tabela`.**
  - A chave (lançador, índice) só guarda posições em que a passada começa uma palavra de opção. Então o resultado guardado é o mesmo de uma passada nova dali.
  - Todas as sondas decidiram entre 0,06 s e 0,22 s.

### A3 a A5: recomendações, iguais à revalidação 12
- **A3 (leitor de base, R5A-COP).**
  - `analisar` (`hooks/parecer.py:117`) só reconhece o `gh` na primeira palavra.
  - Com o marcador e só opções da tabela, saem 0 no `parecer`: `env gh pr merge SENTINELA --merge`, `env -u x …` e `sudo -u -s …`.
  - Com opção fora da tabela, a recusa nova pega: EB1 a EB10 saem 2 no `parecer`.
- **A4 (N-HOOK1).** `flock`, `script`, `watch`, `su`, `runuser`, `tmux` e `ssh` não estão em `LANCADORES`. As 10 formas saem como na revalidação 12. A promessa nova fala só dos lançadores da tabela, então eles seguem no cartão.
- **A5 (X3, C8).** Sem mudança no delta.

### A6: expansão antes da opção do lançador
- `reavaliacao_das_palavras` lê vazia a palavra que não se reduz (`hooks/_comum.py:1905`), e `opcao_fora_da_tabela` a toma pelo comando.
- `env $(echo -a) x git push origin SENTINELA:main` sai 0 / 0, e o env real (GNU e uutils) roda o registrador.
- `env -i $X -a x …` sai 2 / 0. Com `X` vazio, o env roda o `git` real.
- `env ${X:--a} x`, `env {-a,x}`, `env -i ~ -a x` e `env -[a] x` também saem 0 em ao menos um hook.
- É a palavra com expansão, que o critério do lote põe no Não promete (cartão N-HOOK1).
- A correção mais barata, para o cartão: com o marcador, a palavra que não se reduz logo depois de um lançador, antes do comando, recusa como opção não modelada.

### O teste instável (T9b) e o resto do delta
- `b438b21` monta os registradores na thread principal antes do pool. Quando o bash sai 126 ou diz "Text file busy", o teste falha com "falha do arnês, não do gerador".
- A falha fica do lado seguro: o teste fica vermelho e nenhum hook libera. Não há repetição automática que esconda um 0.
- `motivo_da_reavaliacao` e `contorno_da_reavaliacao` só mudam texto. A recusa segue depois das regras específicas, nos dois hooks.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas:
- `forge-check delta --parecer docs/security/lote-leitura-hook.md`;
- `python3 -m unittest tests.test_hooks.CorpusHeredocVoltaUnica -v`: `Ran 23 tests in 338.704s`, `OK`. O corpus passa e não pega o A1 nem o A2, porque mede só o caminho com o marcador;
- as sondas, por um script próprio sobre `Fixture`, `rodar` e `modelos_montados` do próprio teste:
  - 81 formas do parecer anterior e 131 novas, nos dois hooks;
  - 22 linhas sem o marcador como fixture, na branch e na `develop`;
- o `env` real (GNU 9.7 e uutils) com registradores e o bash, com `HOME` em `$TMPDIR/security-engineer-lote-leitura-hook/`, sem rede e sem custo (`R-CUSTO`).

Lacunas:
- O `sudo` da máquina não roda, por causa do "no new privileges" do sandbox. Não há BSD env nem macOS. Para as formas do `sudo` e do BSD, provei só a decisão do hook, que recusa sem depender do programa.
- A suíte inteira não rodou fora do pre-push (`R-TETO`).
- `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH. Também não se aplicam ao delta, que não tem segredo, workflow nem dependência.

Nada foi instalado e nada saiu da máquina. Além deste parecer, só gravei em `$TMPDIR`.
