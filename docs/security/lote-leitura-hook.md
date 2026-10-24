---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 6d5252db2c3799d8114fb432647d4ae0dfcb5109
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-leitura-hook (revalidação 14, volta pela opção A da revalidação 13)

Pedido RET-LEITURA-HOOK-G-REV, etapa E2.1. Escopo: a volta pela opção A da proposta `docs/propostas/lote-leitura-hook-caminho-rev13.md` (decisão "A" do dono, 2026-10-24). Sem o marcador, as regras leem todas as leituras possíveis de cada palavra com `-` que `LANCADORES` não modela e recusam pela união. Acima do teto K = 3, o comando recusa.
- A volta está em dois commits:
  - `ef78e68`: as leituras possíveis, o teto, os textos da seção 3.1 em `docs/hooks.md:95` e os testes;
  - o merge `6d5252d`, que traz a `develop` (`ba57c0b`, versão 0.30.2) sem tocar em `hooks/` nem em `docs/hooks.md` (`git diff ef78e68 6d5252d -- hooks docs/hooks.md` vazio).
- O parecer anterior é a revalidação 13, sobre `1b4b0d8` (commit do parecer `35a5d15`). `forge-check delta --parecer` lista o intervalo `1b4b0d8..6d5252d`.
- Do lado dos controles do Forge, reli inteiros:
  - em `hooks/_comum.py`: `:1738-1903` (`LANCADORES`, `LancadorDemais`, `TETO_FORA_DA_TABELA`, `separar_lancadores`, `_ler_lancadores`), `:1925-1931` (`achado_do_lancador`) e `:2066-2081` (`texto_dividido_do_env`);
  - em `hooks/conformidade.py`: `:346-348` (`sem_lancadores`), `:841-872` (`segmento` e `leitura_do_segmento`), `:1370-1404` (`rotulo_na_sessao_do_forge`), `:1695-1711` (`alvos_de_escrita`) e o tratamento de erro de `principal` (`:1755-1792`);
  - `docs/hooks.md:95` e, em `tests/test_hooks.py`, os testes novos da classe `CorpusHeredocVoltaUnica`: a propriedade sem o marcador, as regressões, a sonda viva, o teto, o estado, as mutações e os alvos de escrita.
- O `parecer` não chama `separar_lancadores` (`grep` nos hooks). Então o caminho sem o marcador só existe no `conformidade`.
- O resto do delta vem da `develop` (`ci.yml`, `R-PROVA`, `tech-lead`, a release), que já passou pelos portões dela (PRs #313, #315 e #316).

**critério mudou:** sim, pela decisão do dono. Desde esta volta, `docs/hooks.md:95` promete que, sem o marcador, as regras "leem o comando atrás do lançador em todas as leituras possíveis de cada palavra com `-` que `LANCADORES` não modela, e recusam se qualquer leitura recusa". Conferi por substring que os textos da seção 3.1 da proposta estão em `docs/hooks.md:95`.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: os hooks `conformidade` e `parecer`. Eles guardam R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA e, sem o marcador, a leitura do `.env` e o apagar do `.git`.

## Achados
- A1 (bloqueante) hooks/_comum.py:1888 · classe "regra sem o marcador atrás de lançador com opção fora da tabela" (2.ª volta seguida): o texto dividido com aspas abertas derruba as outras leituras; env -uS\' cat .env e env -uS\' rm -rf .git saem 0 (develop: 2), e o env real os roda
- A2 (recomendado) hooks/_comum.py:1893 · lançador que divide texto: a opção dentro do texto dividido não é relida; env -S'-u X cat .env' e env -iS'-u X cat .env' saem 0, como na develop, e o GNU env roda o cat
- A3 (recomendado) hooks/parecer.py:108 · leitor de base (cartão R5A-COP): o parecer segue sem pular o lançador com opções da tabela, como na revalidação 13
- A4 (recomendado) hooks/conformidade.py:59 · lançador que entrega texto ao shell (cartão N-HOOK1): flock -c, script -c, watch, su -c, runuser -c, tmux e ssh seguem como na revalidação 13
- A5 (recomendado) hooks/parecer.py:28 · marcador ofuscado (X3, cartão C8): env -S 'git\_push\_forge\_feature/x' segue sem marcador, como na revalidação 13
- A6 (recomendado) hooks/_comum.py:1949 · palavra com expansão antes da opção do lançador (Não promete, cartão N-HOOK1): env $(echo -a) x git push origin SENTINELA:main segue 0 / 0; env -[a] x passou a 2 no conformidade

## Detalhe dos achados
Há um bloqueante, nesta passada só, no caminho sem o marcador. O A1 e o A2 da revalidação 13 fecharam em todas as formas que eu tinha sondado. Com o marcador, nenhuma decisão mudou, salvo uma recusa a mais (abaixo).

Como sondei:
- as sondas sem o marcador rodaram como fixture do `conformidade`, nos modelos de `tests/hooks/conformidade/env-cat-bloqueia.json` (o `.env`) e `trava-rm-projeto-bloqueia.json` (o `rm` e o `git`). Rodaram na branch e na `develop` `ba57c0b`, numa cópia de `git archive` em `$TMPDIR`;
- as sondas com o marcador rodaram contra os hooks reais da worktree em `6d5252d`, com o vigia de produção (3 s), no modelo de fixture do corpus (`Fixture`, `rodar` e `modelos_montados` do próprio teste);
- o efeito foi provado com o `env` real (GNU 9.7 e uutils 0.8.0), com um `.env` falso e um `.git` vazio numa pasta de `$TMPDIR/security-engineer-lote-leitura-hook/`, sem rede.

### A1: uma leitura que não se lê derruba as outras
- **Causa.**
  - Em `_ler_lancadores`, a leitura do texto dividido de uma palavra fora da tabela é montada na hora (`hooks/_comum.py:1887-1888`, `shlex.split(texto[0])`), mesmo sendo só uma leitura possível.
  - Se o resto da palavra depois do `S` tem aspas abertas, o `ValueError` sai de `separar_lancadores` inteiro.
  - `segmento` manda o erro a `ilegivel` (`hooks/conformidade.py:854-856`), que só recusa o que aponta para o Forge e volta sem as outras regras. A leitura sem valor, que recusaria, nunca roda.
- **Por que é a dimensão da volta.**
  - A decisão do dono diz "recusam se qualquer leitura recusa". Aqui, uma leitura que o `env` nem consegue fazer (ele falharia ao dividir) anula a que ele faz de fato.
  - O `-u`, o `-C` e o `-a` levam valor no `env` real. Então `-uS'` quer dizer "tire a variável `S'`", e o comando roda.
- **Sondas sem o marcador (só `conformidade`):**

| Texto | `develop` | lote |
|---|---|---|
| `env -uS\' cat .env` | 2 (ler .env) | 0 |
| `env -uS\" cat .env`, `env -iuS\" cat .env` | 2 | 0 |
| `env -uS"'" cat .env`, `env -uS'"' cat .env` | 2 | 0 |
| `env -uS\' rm -rf .git` | 2 (o .git) | 0 |
| `env -aS\' cat .env` | 0 | 0 |
| `env -S'cat .env "'` (o `-S` por extenso, controle) | 0 | 0 |

- **Efeito real.**
  - Com os hooks desligados, o GNU env e o uutils imprimem o `.env` falso nestas formas: `-uS\' /bin/cat .env`, `-uS\" …`, `-iuS\" …` e `-aS\' …`.
  - O GNU env apaga o `.git` em `-uS\' /bin/rm -rf .git`.
- **Com o marcador, a forma recusa.** `env -uS\' git push origin SENTINELA:main` e as variantes saem 2 / 2, como `env -S`. O defeito é só do caminho sem o marcador.
- **Por que os testes não pegam.**
  - A propriedade só gera o texto colado ao `S` com corpos que o shell lê (`SO_PALAVRAS`) e com palavras de até duas letras. Nunca gera um resto com aspas abertas.
  - `test_regressoes_sem_marcador_do_lancador_dao_2` fixa `env -S'cat .env "'` em 0, "como na develop". Isso vale para o `-S` por extenso, em que o `env` sempre divide e falha. Não vale para o grupo, em que dividir é só uma das leituras.
  - Rodei os 8 testes novos do lote: `Ran 8 tests in 23.091s`, `OK`.
- **Caminho de ataque.**
  - Um agente, por engano ou por injeção de prompt, escreve `env -uS\' cat .env`. O hook libera, e o segredo do projeto entra no contexto. De lá, pode sair num commit, num PR ou numa mensagem.
  - Ou o agente escreve `env -uS\' rm -rf .git`, que apaga o histórico local.
- **Severidade:** média, como o A1 da revalidação 13. A `develop` fazia essa recusa, ela some, e o efeito é real. O alcance de ler o `.env` sem o marcador já existia por outras grafias.
- **Correção mínima,** esforço P, dono `tech-lead`:
  - Em `_ler_lancadores`, o `ValueError` da leitura do texto dividido de uma palavra fora da tabela descarta só essa leitura. É o que o `env` faz: com aspas abertas, ele falha e não roda nada. O `ValueError` do `-S` por extenso (`:1878`) segue indo a `ilegivel`, como hoje.
  - Na propriedade, gerar o resto com aspas abertas depois do `S`, com uma letra antes dele (`-uS'`, `-aS"`, `-iuS'`), com o mesmo oráculo (a leitura sem o lançador). Pôr `env -uS\' cat .env` e `env -uS\' rm -rf .git` como fixtures `-bloqueia`.
  - Em `test_regressoes_sem_marcador_do_lancador_dao_2`, deixar claro que o 0 do texto com aspas abertas vale só para o `-S` por extenso.
- **Dimensão nova para a matriz da família:** "leitura possível que não se lê". Uma leitura que falha não pode anular as outras.
- **Contagem por classe** (decisão "A" de 2026-10-22):
  - O autor nomeou a classe da volta "regra sem o marcador atrás de lançador com opção fora da tabela" (commit `ef78e68`). Ela abriu na revalidação 13 (A1 e A2), e esta é a 2.ª volta seguida. Na contagem antiga, é também a 4.ª volta da classe "lançador que divide texto".
  - Pela decisão, a entrega para: o `software-architect` propõe o caminho e o dono decide (`R-DECISAO`), ainda que a correção seja pequena.
  - As classes já foram registradas mais de uma vez e cabem em `docs/engineering/achados-recorrentes.md` (PA-7, hoje vazio). O brief limita o commit a este parecer, então a linha fica para o PR do lote.

### O A1 e o A2 da revalidação 13: fechados nas formas sondadas
- **As 22 linhas sem o marcador da revalidação 13 recusam.**
  - Entre elas: `env -iu X cat .env`, `env -iC d cat .env`, `env -iu X rm -rf .git`, `env -iS'cat .env'`, `env -vS'cat .env'` e `env -iS"rm -rf .git"`.
  - Os controles seguem 2.
  - `env -a x cat .env` e `env -a x rm -rf .git`, que saíam 0 nos dois lados, passaram a 2.
- **Variantes novas sem o marcador: 98 formas do `.env` e 20 do `rm` e do `git`, na branch e na `develop`.** Resultado: 81 saem 2 nos dois lados, 25 saem 2 na branch e 0 na `develop`, 6 são o A1 (2 na `develop`, 0 na branch) e 6 saem 0 nos dois lados. As famílias:
  - abreviações de `--split-string`: `--sp`, `--split`, `--split-s=` e `--s=`;
  - grupos com `S`: `-0S'…'`, `-i0vS'…'`, `-iSx`, `-iS ''`, `-iS` com o corpo na palavra seguinte, `-iS` depois de `-iu X`, de `-a x` e de `-uX`;
  - texto dividido com `NOME=valor`, com outro `env -iS` dentro e com `nice -n5`; `bash -c` e `eval` atrás do lançador;
  - lançadores encadeados: `env -iu X env -iS'…'`; `env -iu X` antes de `nice`, `timeout`, `nohup`, `stdbuf`, `sudo -u root`, `command`, `exec`, `time -p`, `xargs -a f` e `setsid -w`; `env -a x sudo -s`;
  - `flock`, `ionice` e `script` atrás de `env` com opção (`env -a x flock -n x`, `env -iu X ionice -c3`, `env -iu X script -qc`): recusam como `LANCADORES_RECUSADOS`;
  - posição: `$(…)`, crase (que a `develop` liberava), `;`, `&&`, `( … )`, `{ …; }`, `if`, `|` e `<(…)`;
  - grafias do `env`: `/usr/bin/env`, `e""nv` e `\env`; o `--`; `NOME=valor` antes e depois;
  - pasta: `env -iC sub cat ../.env`, `env -iC .. cat .env` e `cd sub && env -iC .. cat .env`;
  - do lado do `rm` e do `git`: o `.forge` pelo `rm`, `git push --force`, `git push origin HEAD:main` e `git commit --no-verify`, atrás de `env -iu X` e de `env -iS'…'`.
- **O teto K = 3.**
  - Com três palavras fora da tabela (`env -a x -a y -a z cat .env`), recusa pela regra.
  - Com quatro, recusa pelo teto, também com quatro `env -iu` encadeados.
  - Todas as sondas decidiram entre 0,06 s e 0,18 s.
- **As 6 formas que saem 0 nos dois lados.**
  - Duas são do lançador: `env -aS\' cat .env` é o A1, e `env -iS'-u X cat .env` é o A2.
  - As outras quatro não recusam nem sem o lançador, porque nenhuma regra as pega: `env -iu X sed -n p .env`, `env -iu X cp .env /tmp/x`, `env -iu X find . -delete` e `env -iS'find .git -delete'`.

### As duas exclusões da propriedade: aceitas
- **Corpos que mudam o estado do shell** (`MUDA_O_ESTADO_DO_SHELL`: `cd`, `export`, `set` e afins).
  - Atrás de um lançador, o `cd` e o `export` rodam noutro processo, ou não existem como programa, e não mudam o shell. Por isso o oráculo "o corpo sozinho dá 2" não vale para eles.
  - O estado tem teste à parte, `test_estado_da_leitura_a_mais_nao_segue_adiante`. A regra "a pasta e as variáveis são as da leitura sem valor" vem da decisão.
- **Palavras em que o `env` sempre divide** (`-S…` e `--split-string…`, `divide_sempre`).
  - Nelas, a palavra seguinte é o texto, e não um valor ou o comando. Então `L w C` e `L w X C` não são leituras delas.
  - O `-S` por extenso tem os controles do item 2 e as sondas acima.
- **O corte do gerador.** O gerador das formas com `S` também se limita aos corpos que o shell lê como palavras (`SO_PALAVRAS`), porque o `env -S` não roda `;` nem `|`. O corte é correto, mas é por ele que o A1 escapou: falta a linha do resto que não se lê.

### O caminho com o marcador: igual
- **O teste do `S`.** `achado_do_lancador` passou a usar `texto_dividido_do_env`. Conferi que o teste novo é equivalente ao anterior: a longa precisa de um prefixo não vazio de `split-string`, e a curta, de um `S` depois do `-`. `--=x`, `--S` e `--sig=S` seguem fora.
- **As sondas antigas.**
  - Rodei de novo, em `6d5252d`, as 81 formas da revalidação 12 e as 131 da revalidação 13, nos dois hooks.
  - As 424 decisões batem com as da revalidação 13, salvo uma: `env -[a] x git push origin SENTINELA:main` (A6) passou de 0 a 2 no `conformidade`, pelas leituras possíveis.
- **As formas novas.** 22 formas novas com o marcador saem 2 / 2:
  - o A1: `-uS\'`, `-uS\"`, `-iuS\"` e `-aS\'`;
  - o teto: três e quatro palavras, e quatro `env` encadeados;
  - as abreviações e os grupos com `S`;
  - `flock`, `ionice` e `script` atrás de `env` com opção;
  - `env -S'-u X …'`.
- **Os legítimos.** Com o marcador, saem 0 / 0: `env -i -u X`, `env X=1`, `nice -n 1`, `timeout 5` e `env -C / -i X=1`. Rodei cada um antes de `git push origin feature/x` e de `gh pr create --draft …`.
- **O teto sem o marcador.**
  - Ele recusa linhas legítimas raras com quatro opções fora da tabela, como `xargs -o -p -l -i echo` e `sudo --preserve-env=PATH -A -S -B ls`. É o que a decisão do dono manda, e a mensagem dá o contorno.
  - As formas comuns saem 0: `xargs -0 -n1 -P4`, `timeout --kill-after=5 --signal=KILL 10`, `env --unset=X --chdir=/`, `stdbuf -oL -eL` e `time -v -a -q -o f`.

### O resto do caminho sem o marcador
- **`alvos_de_escrita`** (`hooks/conformidade.py:1702-1710`) soma os alvos das leituras e pula a linha com `ValueError`. Com o A1, `env -uS\' tee docs/reviews/x.md` não dá o alvo. Só a autoria do parecer escrito pelo Bash fica sem registro, e a mesma correção do A1 fecha isso.
- **`rotulo_na_sessao_do_forge`** não pega o `LancadorDemais`. Ele sobe a `principal`, que barra se a linha cita o rótulo. Se não cita, cai em `falhar_fechado`, que só libera sem o marcador. É o comportamento de antes para o `ValueError` do `-S`.
- **O `LancadorDemais` em `segmento`** chama `barrar`, que sai com 2 (`bloquear`). Então o código seguinte não roda com `leituras_do_lancador` indefinida.

### A2: opção dentro do texto dividido
- **O defeito.** O GNU env relê como opção o que vem no começo do texto dividido: `env -S'-u X /bin/cat .env'` imprime o `.env` (o uutils, só na forma por extenso). O hook toma `-u` como o comando (`hooks/_comum.py:1893`) e libera, na branch e na `develop`.
- **Por que é recomendação.** Não é regressão, e a decisão manda ler o texto dividido "como comando", que é o que o hook faz. Com o marcador, a forma recusa como `env -S`.
- **Correção barata, para o cartão:** depois de dividir, continuar lendo as opções do mesmo `env` sobre as palavras divididas, com as mesmas leituras possíveis.

### A3 a A6: recomendações, iguais à revalidação 13
- A3, A4 e A5: sem mudança no delta. As formas da revalidação 13 saem igual.
- A6: `env $(echo -a) x …` segue 0 / 0. A linha passou de `:1905` a `:1949` porque o código acima cresceu. `env -[a] x …` agora sai 2 no `conformidade` e segue 0 no `parecer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas:
- `forge-check delta --parecer docs/security/lote-leitura-hook.md`;
- os 8 testes novos do lote em `tests.test_hooks.CorpusHeredocVoltaUnica`: `Ran 8 tests in 23.091s`, `OK`. Eles passam e não pegam o A1;
- as sondas, por scripts próprios sobre `Fixture`, `rodar` e `modelos_montados` do próprio teste:
  - sem o marcador, 129 linhas (98 do `.env`, 20 do `rm` e do `git`, 11 legítimas), na branch e na `develop`;
  - com o marcador, 81 formas da revalidação 12, 131 da revalidação 13 e 27 novas, nos dois hooks;
- o `env` real (GNU 9.7 e uutils 0.8.0), com `HOME` e a pasta em `$TMPDIR/security-engineer-lote-leitura-hook/`, sem rede e sem custo (`R-CUSTO`).

Lacunas:
- O `sudo` da máquina não roda, por causa do "no new privileges" do sandbox. Não há BSD env nem macOS. Para essas formas, provei só a decisão do hook.
- A suíte inteira não rodou fora do pre-push (decisão ACELERA-RODADA, corte 1).
- `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH. O `ci.yml` do delta veio da `develop` (PR #313) e já foi revisado lá.

Nada foi instalado e nada saiu da máquina. Além deste parecer, só gravei em `$TMPDIR`.
