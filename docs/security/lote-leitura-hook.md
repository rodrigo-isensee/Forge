---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: d67f31fdeb1b66b85771a7687b2f2a88e2a63c9a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-26
---
# Review de segurança: lote-leitura-hook (revalidação 16, volta I: só testes e specs)

Pedido RET-LEITURA-HOOK-H-REV, etapa E2.1. Escopo: a volta I, que responde ao A1 do QA `7f378b0` (mutantes X5 e X6 de `hooks/conformidade.py:1714` sobreviviam). São dois commits, `bb21376` e `d67f31f`:
- `tests/test_hooks.py:3432-3446`: o teste novo `test_alvos_do_tee_atras_do_texto_dividido_aberto` (mais de um alvo depois do `tee`, e `-a`, `--append` e `-i` fora dos alvos);
- `tests/test_hooks.py:3448-3465`: `test_spec_de_mutantes_do_lote_e_valida` passa a validar as duas specs;
- `tests/mutantes/lote-leitura-hook-volta.json`: a segunda spec, com X1, X3, X5 e X6, pelo teto de 8 do `forge-mutante`.

## Revalidação 16 por delta
- `forge-check delta --parecer docs/security/lote-leitura-hook.md` lista o intervalo `0e8776d..d67f31f`: só `tests/mutantes/lote-leitura-hook-volta.json` (+46) e `tests/test_hooks.py` (+27 -8). O resto do intervalo são pareceres (`docs/reviews/`, `docs/security/`, `docs/qa/`).
- **`hooks/` não mudou.** `git diff --name-only` de `7f378b0..d67f31f` e de `0e8776d..d67f31f` sobre `hooks/`, `docs/hooks.md`, `bin/` e `.github/` sai vazio. O código dos controles é o mesmo do parecer `941a0dc`; por isso não rodei sondas novas, e os números de linha dos achados A2 a A7 valem como estão.
- **Nenhuma asserção afrouxa.** O teste da spec aplica a cada uma das duas specs as mesmas seis asserções de antes (chaves, de 1 a 8 mutantes, ids únicos, chaves do mutante, `arquivo` em `hooks/`, `de` diferente de `para`, `de` uma vez só no arquivo de hoje). A asserção de inclusão das trocas de `MUTACOES_DO_TEXTO_ABERTO` segue sobre a primeira spec, como antes. Nenhuma outra linha de teste sai.
- **As âncoras da segunda spec existem uma vez no código de hoje:** X1 em `hooks/_comum.py:1899`, X3 em `hooks/conformidade.py:859`, X5 e X6 em `hooks/conformidade.py:1714`.
- **Os testes do lote:** `test_alvos_do_tee_atras_do_texto_dividido_aberto`, `test_spec_de_mutantes_do_lote_e_valida` e `test_texto_dividido_aberto_com_mais_de_uma_leitura_recusa`: `Ran 3 tests in 0.704s`, `OK`. A morte dos mutantes fica com o QA (`forge-mutante`).
- **A8, por leitura, recomendado.** A regra do `tee` em `hooks/conformidade.py:1714` descarta toda palavra que começa por `-`, também depois de `--`. Então, atrás de lançador com mais de uma leitura e texto dividido aberto (o único caminho que chega a essa linha), `tee -- -x.md` esconde o alvo `-x.md`. Não tem efeito hoje: essa linha já recusa no `PreToolUse` (revalidação 15, "O resto do delta"), e o `PostToolUse` da autoria não roda para ela. É da mesma família do A1 do review `96cf447` (alvo perdido sem efeito hoje). Correção mínima, esforço P, dono `tech-lead`: parar de descartar opções depois de `--`. Fica para o cartão TEE-TETO-ALVO.
- **PA-7.** Conferi `docs/engineering/achados-recorrentes.md`: a lista segue vazia. A linha das classes recorrentes do lote fica para o PR do lote, como na revalidação 15 (o brief limita o commit a este parecer).

Veredito: **aprovado**. Nenhum bloqueante; A2 a A7 seguem como recomendação, iguais à revalidação 15, e o A8 entra como recomendação.

**Revalidação 15 (histórico, sobre `0e8776d`).** O que segue é o parecer anterior; os achados abaixo valem para o head novo.

Pedido RET-LEITURA-HOOK-H-REV, etapa E2.1. Escopo: a volta pela opção B da proposta `docs/propostas/lote-leitura-hook-caminho-rev14.md` (decisão "B" do dono, 2026-10-24). Sem o marcador, com mais de uma leitura (uma palavra fora da tabela já vista), o texto dividido que não fecha aspas recusa com `barrar`. Com uma leitura só, segue a `ilegivel`, como antes.
- A volta está em quatro commits:
  - `73aa3c4`: `TextoAbertoComLeituras`, `TextoDivididoAberto` e `_dividir` em `hooks/_comum.py:1824-1925`, o `except` de `segmento` (`hooks/conformidade.py:851-861`), a regra do `tee` em `alvos_de_escrita` (`hooks/conformidade.py:1712-1715`), o texto da seção 3.2 em `docs/hooks.md:95` com o FD18, os fixtures e os testes;
  - `f3ff1ef` e `0e8776d`: a spec de mutantes `tests/mutantes/lote-leitura-hook.json` e o teste dela;
  - o merge `fa3a35c`, que traz a `develop` (`bin/forge-changelog`, `bin/forge-fechar`, PRs #319 e #320, cada um com o seu parecer de segurança) sem tocar em `hooks/` nem em `docs/hooks.md`.
- O parecer anterior é a revalidação 14, sobre `6d5252d` (commit do parecer `c17509a`). `forge-check delta --parecer` lista o intervalo `6d5252d..0e8776d`. Do lado dos hooks, o delta é `hooks/_comum.py` (+28 -5) e `hooks/conformidade.py` (+13 -5); `hooks/parecer.py` não muda.
- Reli inteiros, do lado dos controles do Forge:
  - `hooks/_comum.py:1819-1925` (as duas exceções, `separar_lancadores`, `_ler_lancadores`, `_dividir`) e `:2089-2104` (`texto_dividido_do_env`);
  - `hooks/conformidade.py:841-872` (`segmento`) e `:1677-1720` (`autoria`, `alvos_de_escrita`);
  - `docs/hooks.md:95` e os cinco testes novos de `CorpusHeredocVoltaUnica`.

**critério mudou:** sim, pela decisão do dono. `docs/hooks.md:95` passa a prometer que, "quando há mais de uma leitura e o texto dividido de alguma não fecha aspas, o comando não é analisável e recusa, qualquer que seja o resto", e registra o FD18.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: o hook `conformidade` (o `parecer` não chama `separar_lancadores`). Sem o marcador, ele guarda a leitura do `.env` e o apagar do `.git`.

## Achados
- A2 (recomendado) hooks/_comum.py:1905 · lançador que divide texto: a opção dentro do texto dividido não é relida; env -S'-u X cat .env' e env -iS'-u X cat .env' seguem 0, como na develop
- A3 (recomendado) hooks/parecer.py:108 · leitor de base (cartão R5A-COP): sem mudança no delta
- A4 (recomendado) hooks/conformidade.py:59 · lançador que entrega texto ao shell (cartão N-HOOK1): sem mudança no delta
- A5 (recomendado) hooks/parecer.py:28 · marcador ofuscado (X3, cartão C8): sem mudança no delta
- A6 (recomendado) hooks/_comum.py:1972 · palavra com expansão antes da opção do lançador (cartão N-HOOK1): env $(echo -a) x git push origin SENTINELA:main segue 0 / 0
- A7 (recomendado) docs/hooks.md:95 · texto do FD18 mais estreito que o código: a palavra fora da tabela pode ser de outro lançador da cadeia (sudo -s env -S\' ls e nice -Z env --split-string=\' make recusam), e o FD18 fala só do env com opção fora da tabela
- A8 (recomendado) hooks/conformidade.py:1714 · alvo do tee depois de -- atrás do texto dividido aberto com mais de uma leitura: env -aS'"' tee -- -x.md esconde o alvo -x.md; sem efeito hoje, a linha já recusa no PreToolUse (cartão TEE-TETO-ALVO)

## Detalhe dos achados
Nenhum bloqueante. O A1 da revalidação 14 fechou em todas as formas sondadas. Não há regressão contra a `develop`, e nenhuma decisão mudou nas formas sem aspa aberta nem no caminho com o marcador.

Como sondei:
- as sondas rodaram contra os hooks reais de três árvores (`git archive` em `$TMPDIR`):
  - o head `0e8776d`;
  - o head anterior `b3118d9`, com os mesmos hooks de `6d5252d`;
  - a `develop` atual `f142001`, com os mesmos hooks de `ba57c0b`;
- rodaram com o vigia de produção (3 s), no modelo de fixture do corpus (`Fixture`, `LANCADOR` e `ambiente_limpo` do próprio teste), com um `.env` falso no projeto;
- o efeito real foi provado com o `env` real (GNU 9.7 e uutils 0.8.0), com `HOME` e a pasta em `$TMPDIR/security-engineer-lote-leitura-hook/viva16/`, sem rede.

### A1 da revalidação 14: fechado
- **A causa sai por construção.** Antes, o `ValueError` de uma leitura a mais derrubava as outras e ia a `ilegivel`.
  - Agora, `_dividir` (`hooks/_comum.py:1916-1925`) levanta `TextoAbertoComLeituras` sempre que `gasto > 0`.
  - Na palavra do grupo (`-uS'`) e na abreviação (`--spl='`), o `gasto` sobe antes de dividir (`:1895`). Então a palavra que traz o texto já conta como a leitura a mais.
  - O `segmento` pega a exceção antes de `LancadorDemais` e chama `barrar` (código 2), com o `CONTORNO_DO_LANCADOR`.
- **As sondas do brief, no head:**

| Texto | `develop` | `6d5252d` | `0e8776d` |
|---|---|---|---|
| `env -uS\' cat .env`, `env -uS\" cat .env`, `env -iuS\" cat .env` | 2 | 0 | 2 |
| `env -uS"'" cat .env`, `env -uS'"' cat .env` | 2 | 0 | 2 |
| `env -uS\' rm -rf .git`, `env -iuS\' rm -rf .git` | 2 | 0 | 2 |
| `env -iu -S\' cat .env`, `env -iu -S\" cat .env` | 2 | 0 | 2 |
| `env --spl=\' cat .env`, `env --spl='"' cat .env`, `env --split=\' …`, `env --s=\' …` | 2 | 0 | 2 |
| `env --spl=\' rm -rf .git`, `env -iu --spl=\' cat .env` | 2 | 0 | 2 |
| `env -aS\' cat .env`, `env -a x -S\' cat .env`, `env --spl \' cat .env` | 0 | 0 | 2 |
| `nice -n5 env -uS\' …`, `sudo -s env -uS\' …`, `env -iu X env -uS\' …`, `timeout 5 env -uS\' …` | 2 | 0 | 2 |
| `echo ok; env -uS\' cat .env`, `(…)`, `x=$(…)`, `env -uS\' bash -c 'cat .env'` | 2 | 0 | 2 |
| `env -S\' cat .env`, `env --split-string=\' cat .env`, `env -S'cat .env "'` (controle, uma leitura) | 0 | 0 | 0 |

- **A sonda viva.**
  - Com os hooks desligados, o uutils imprime o `.env` falso em `-uS'`, `--spl='` e `-aS'`. O GNU o imprime em `-uS'`, `-aS'` e `-iu -S'` (o `-u` toma `-S'` por nome de variável). Todas essas formas recusam no head.
  - 30 formas de uma leitura só seguem 0: `env -S\'`, `env -S \'` e `env --split-string=\'`, sozinhas ou depois de `-i`, `-u X`, `-C .`, `-i -u X` e de `sudo -u root`. Nelas, os dois `env` falham sem rodar o comando. Conferi `-u X -S'`, `-C . -S '`, `-i --split-string='` e `-i -u X -S '`.
  - O teste `test_sonda_viva_do_texto_dividido_aberto` prova o mesmo para as duas formas de referência.
- **A varredura com a `develop` como oráculo, com e sem aspa aberta.** São 5 390 formas sem o marcador, nas três árvores. As dimensões: 7 lançadores antes, 7 grupos de opções do `env`, 16 palavras com aspa aberta e 6 com o texto fechado, e 5 corpos (`cat .env`, `rm -rf .git`, `ls`, `make`, `echo hi`). Resultado:
  - nenhuma forma sai 0 no head e 2 na `develop`: não há regressão;
  - com o texto fechado (1 470 formas), o head decide igual a `6d5252d` em todas;
  - com a aspa aberta e corpo nocivo, 1 444 formas saem 2 no head e 0 em `6d5252d`. Destas, 483 a `develop` já recusava (o A1). As outras 961 são recusa a mais: o `env` real falha nelas ou as roda, e a recusa é a decisão B;
  - as 150 formas com aspa aberta que seguem 0 são todas de uma leitura só (`-S` por extenso ou `--split-string` inteiro, sem palavra fora da tabela antes), que o `env` não roda.
- **O caminho com o marcador não muda.** 11 formas dão a mesma decisão no head e em `6d5252d`, nos dois hooks:
  - as do A1 com `git push origin SENTINELA:main` e com `gh pr merge`;
  - o A6;
  - os legítimos `env -i -u X`, `env X=1`, `env -C / -i X=1` e `timeout 5`.
- **Os testes do lote.** Rodei os cinco testes novos: `Ran 5 tests in 31.314s`, `OK`. São eles:
  - a propriedade do texto aberto, com 49 559 formas em 29,9 s;
  - o A1 e o controle;
  - a sonda viva;
  - as mutações;
  - a spec de mutantes.

  A propriedade agora gera o resto com aspa sem par depois do `S` e depois de uma palavra fora da tabela. Era a linha que faltava na revalidação 14.

### O FD18 é o único falso positivo novo? Sim, salvo o texto (A7)
- A varredura tem 2 262 falsos positivos novos: aspa aberta, corpo inofensivo, 2 no head e 0 em `6d5252d` e na `develop`.
  - Todos saem pelo mesmo motivo, "texto dividido que não fecha aspas".
  - Todos têm uma palavra fora da tabela antes do texto.
  - É o que a decisão B manda e o que o FD18 registra (`env -uS'"' make`, contorno `env -u X make`).
- Nada mais mudou de decisão: o texto fechado e o caminho com o marcador batem com `6d5252d`.
- **A7: o texto do FD18 é mais estreito que o código.**
  - A palavra fora da tabela pode ser de outro lançador da cadeia. Recusam, por exemplo, `sudo -s env -S\' ls`, `nice -Z env -S\' make`, `xargs -p env --split-string=\' ls` e `env -a x env -i -S\' ls`.
  - O código segue a decisão: "palavra fora da tabela já vista", contando a cadeia, como o teto.
  - Mas o FD18, em `docs/hooks.md:95` e em `changelog.d/lote-leitura-hook.md:15`, fala só do "`env` com uma opção fora da tabela".
  - **Correção mínima,** esforço P, dono `tech-lead`: escrever "um lançador da cadeia com opção fora da tabela antes do texto dividido com aspa sem par", e o contorno: as opções da lista, uma por palavra, em cada lançador.
  - É recomendação: o falso positivo é raro, não tem efeito de segurança, e a mensagem já dá o contorno.

### O resto do delta
- **`alvos_de_escrita`** (`hooks/conformidade.py:1712-1715`). Com `TextoAbertoComLeituras`, toma como alvo cada palavra depois do primeiro `tee`, e ler a mais não esconde alvo. O `PreToolUse` barra essa linha, então o `PostToolUse` da autoria não roda para ela. A regra só pesa se um dia o caminho deixar de barrar. Sem achado.
- **Outros chamadores de `separar_lancadores`** (`sem_lancadores`, `rotulo_na_sessao_do_forge`, `principal`). As duas exceções novas são `ValueError`, como o erro do `shlex` de antes, e `TextoAbertoComLeituras` é um `LancadorDemais`. Quem já tratava esses dois segue tratando igual.
- **`bin/forge-changelog` e `bin/forge-fechar`** vêm da `develop` (PRs #319 e #320). Têm pareceres próprios em `docs/security/changelog-json-link.md` e `docs/security/lote-fechar-031.md` e ficam fora do escopo deste parecer.
- **PA-7** (`docs/engineering/achados-recorrentes.md`). Conferi o arquivo: a lista segue vazia. As classes deste lote já foram registradas mais de uma vez e cabem lá: "lançador que divide texto" e "regra sem o marcador atrás de lançador com opção fora da tabela". O brief limita o commit a este parecer, então a linha fica para o PR do lote.

### A2 a A6: recomendações, iguais à revalidação 14
- A2: `env -S'-u X cat .env'` e `env -iS'-u X cat .env'` seguem 0 no head e na `develop`. A linha passou de `:1893` a `:1905` (`base, i = dividido + …`).
- A3, A4 e A5: o código não muda no delta.
- A6: `env $(echo -a) x git push origin SENTINELA:main` segue 0 / 0. `env -[a] x …` segue 2 no `conformidade` e 0 no `parecer`. A linha passou de `:1949` a `:1972`.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas:
- `forge-check delta --parecer docs/security/lote-leitura-hook.md` (intervalo `6d5252d..0e8776d` na revalidação 15 e `0e8776d..d67f31f` na 16);
- na revalidação 16, três testes do lote: `Ran 3 tests in 0.704s`, `OK`;
- os cinco testes novos do lote em `tests.test_hooks.CorpusHeredocVoltaUnica`: `Ran 5 tests in 31.314s`, `OK`;
- as sondas, por um script próprio sobre `Fixture`, `LANCADOR` e `ambiente_limpo` do próprio teste. Sem o marcador: 56 formas do A1 e controles e 5 390 da varredura. Com o marcador: 11 formas, nos dois hooks. Cada uma rodou nas três árvores;
- o `env` real (GNU 9.7 e uutils 0.8.0), com `HOME` e a pasta em `$TMPDIR`, sem rede e sem custo (`R-CUSTO`).

Lacunas:
- O `sudo` da máquina não roda, por causa do "no new privileges" do sandbox. Não há BSD env nem macOS. Para essas formas, provei só a decisão do hook.
- A suíte inteira não rodou fora do pre-push (decisão ACELERA-RODADA, corte 1). Os fixtures novos do lote rodam nela e no CI.
- `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH. O delta não toca workflow.

Nada foi instalado e nada saiu da máquina. Além deste parecer, só gravei em `$TMPDIR`.
