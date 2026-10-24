---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: e8b2af94d1e21a16899980910665d50e20404b2e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-leitura-hook (revalidação 12, volta da revalidação 11: o lançador que divide texto)

Pedido RET-LEITURA-HOOK-E-REV, E1.1. Sou revisor independente: não implementei esta volta (`R-REVIEW`). O parecer anterior (revalidação 11, `aprovado`, sem achados) está em `8a88be9`.

**Delta lido.** O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` deu `182f928..e8b2af9`. Os commits são `414ddd3` (corpus vermelho ES1 a ES17 e FD16a a FD16d), `debd17d` (`env_divide_texto`, a dimensão nova do G1 e o `env` GNU no T9b), `ef4c030` e `e8b2af9` (`docs/hooks.md:95`, FD14 e FD16). O trecho `8a88be9` e `a143cf4` são os pareceres da revalidação 11. Li inteiro:
- `hooks/_comum.py:1800-1831`, `1837-1859`, `1890-1891` e `2258`;
- `tests/test_hooks.py:1954-1956`, `2393-2406`, `2425-2427`, `2465-2466` e `2553-2625`;
- `tests/fixtures/heredoc-volta-unica.json:258-279`;
- as duas fixtures `tests/hooks/conformidade/contrib-remoto-nomeado-proprio-*.json:25`;
- `docs/hooks.md:95` e `changelog.d/lote-leitura-hook.md:12`.

Fica como "já lido" o que vem antes de `182f928` (revalidações 1 a 11). Uma exceção: reli `hooks/_comum.py:1739-1747` (`LANCADORES` e `ENV_COM_VALOR_CURTA`), porque o código novo do delta usa essas tabelas.

**Critério.** A DECISÃO TÉCNICA do Jarvis no pedido RET-LEITURA-HOOK-E, que fecha o A1 da segurança (`a143cf4`). Ela pede que, com o marcador crítico, todo `env` com a opção de dividir texto recuse nos dois hooks, sem dividir o valor. Também valem a frase de `docs/hooks.md:95` ("o `env` com a opção de dividir texto … recusa"), o ADR 0011 ("o que o analisador não modela é recusado") e a decisão "A" do dono de 2026-10-22, que conta as voltas por classe.

## Achados
- A1 (bloqueante) hooks/_comum.py:1747 · classe "lançador que divide texto" (2.ª volta seguida). O `-a` (`--argv0`) leva valor no GNU env 9.7, mas falta em `ENV_COM_VALOR_CURTA`. Em `env_divide_texto`, o valor `x` passa então por comando, e o laço para antes do `-S`. A tabela nova `ENV_LONGAS_COM_VALOR` (linha 1800) já traz `argv0`, então as duas tabelas se contradizem. Prova: `env -a x -S 'bash -c "git push origin SENTINELA:main"'` dá 0 no `conformidade`, e a forma com o `gh pr merge SENTINELA --merge` dá 0 no `parecer` (`$TMPDIR/tech-lead-lote-leitura-hook/sonda_env2.py`). Com os hooks desligados, `gnuenv -a x -S 'bash -c "echo RODOU"'` imprime `RODOU`, e `gnuenv -ax -S'…'` também. A recusa que a decisão técnica pede não acontece.
- A2 (bloqueante) hooks/_comum.py:1810 · classe "lançador que divide texto" (2.ª volta seguida). O `env` desta máquina (`/usr/bin/env`, uutils coreutils 0.8.0, o padrão do Ubuntu) aceita o `-S` colado depois de `NOME=valor`, depois de `-` e depois de `-f arquivo`. O laço de `env_divide_texto` para na primeira palavra que não começa com `-`, e também em `-`. Prova, hooks ligados: `env X=1 -S'bash -c "<sentinela>"'`, `env - -S'…'`, `env -i X=1 -S'…'` e `env -f /dev/null -S'…'` dão 0 / 0 nos dois hooks (`sonda_env.py`). Hooks desligados, com o `env` do `PATH`: as quatro formas imprimem `RODOU`. O teste não vê isso porque o `env_gnu()` (`tests/test_hooks.py:2395`) escolhe o `gnuenv`, e a docstring dele diz que o uutils "não divide", mas o uutils divide o `-S` colado. O texto de `docs/hooks.md:95` promete a recusa do "`env` com a opção de dividir texto", sem limitar ao GNU.
- A3 (bloqueante) hooks/_comum.py:1740 · classe nova "opção de lançador que o hook não modela" (1.ª volta; não é regressão, porque a `develop` tem a mesma tabela em `hooks/conformidade.py:37-38`). Na tabela `LANCADORES["env"]`, faltam o `-a` e o `--argv0`. Em `separar_lancadores`, o valor do `-a` vira o comando, e a ação crítica some. Prova: `env -a x git push origin SENTINELA:main` dá 0 no `conformidade`, `env -a x gh pr merge SENTINELA --merge` dá 0 no `parecer` e `env --argv0 x git push …` dá 0, enquanto `env git push origin SENTINELA:main` dá 2. O GNU 9.7 e o uutils rodam `env -a x git --version` normalmente. É segurança com gatilho (push direto para a `main`), e vai também como cartão para o `security-engineer`.
- A4 (recomendado) tests/test_hooks.py:2435 · O defeito é do teste, não do hook. A falha esporádica de `test_divisao_esta_na_classe` e de `test_g1_esta_na_classe` vem de uma corrida `ETXTBSY`. As threads do pool (linhas 2602 e 2641) gravam os registradores executáveis enquanto outras threads fazem `fork`. O filho herda o descritor de escrita aberto até o `exec`, e o `exec` do script recém-gravado falha. Numa cópia instrumentada, que só grava o stderr do bash, saiu `FAILED (failures=4)` sem carga extra, e as 4 falhas são as 4 linhas `…/dv-78/bin/sudo: /usr/bin/bash: bad interpreter: Text file busy` (`$TMPDIR/tech-lead-lote-leitura-hook/diag0.log`). A cópia limpa passou na rodada anterior (`Ran 3 tests … OK`). A correção sugerida é montar todas as pastas e registradores antes do pool e só então rodar os textos em paralelo, ou repetir o `exec` diante de `ETXTBSY`. O stderr descartado escondia a causa.

## Parecer
**Reprovado.** Há três bloqueantes (A1 a A3), todos de comportamento provado com gatilho nos dois hooks. O resto da volta está certo, como mostram as seções abaixo.

**Contagem por classe** (decisão "A" de 2026-10-22):
- "lançador que divide texto": a 1.ª volta foi o A1 da segurança na revalidação 11 (`a143cf4`). A1 e A2 são a 2.ª volta seguida da mesma classe. Pela decisão, **a entrega para**: o `software-architect` propõe o caminho e o dono decide (`R-DECISAO`).
- "opção de lançador que o hook não modela": A3 abre a classe, na 1.ª volta.

Uma sugestão para a proposta, sem decidir por ela: aplicar ao `env` a mesma saída que a opção C deu ao `$'…'`. Com o marcador, recusaria o `env` que tem, em qualquer palavra depois dele no mesmo comando simples, uma opção fora do conjunto modelado (hoje `-i`, `-0`, `-v`, `-u`, `-C` e as longas sem valor) ou uma palavra `-S…` ou `--s…`. Isso cobre o `-a` e o `-f` e não depende de qual `env` está instalado.

### O que fecha
| Item | Estado | Evidência |
|---|---|---|
| Corpus vermelho ES1 a ES17 | verde | `test_corpus_nos_dois_hooks` `OK` na cópia limpa de `e8b2af9` |
| FD16a a FD16d | verde | FD16a e FD16b dão 2; os contornos FD16c e FD16d dão 0 |
| `env_divide_texto` contra a sua própria lista | certo | `-S`, `-iS`, `-vS`, `-uS` (é `-u S`, e não divide), `-u X -S`, `--split-string` com e sem `=`, `--split`, `--spl=` e `--s` |
| A recusa e o seu texto | certo | a recusa não divide o valor; `contorno_da_reavaliacao` devolve `CONTORNO_DO_ENV_S` |
| Dimensão nova do G1 | certa | 9 grafias × 2 separadores × 2 lados do `-c` × 3 shells × 2 "antes" × 2 moldes × 2 hooks; `test_divisao_esta_na_classe` exige pelo menos 400 textos e roda com o `gnuenv` |
| Mutação (`env_divide_texto` sempre `False`, cópia `git archive`) | vermelha | `FAILED (failures=1980)`: 1944 na propriedade (o número do autor) e 36 no corpus (ES1 a ES17 nos dois hooks e FD16a e FD16b) |
| As duas fixtures trocadas | certas | a troca de `env -S '…'` por `env X=1 …` mantém a intenção: a `-libera` libera, e a `-bash-c-bloqueia` recusa pelo `bash -c`; `Hooks.test_fixtures` `OK` |
| Linha nova do fragmento | aceita | descreve o falso positivo novo e o contorno, como pede a DECISÃO TÉCNICA |
| FD14 em `docs/hooks.md:95` | certo | tem agora o contorno do `env -S` ("o `env` sem `-S` (`env VAR=x comando`) ou o comando direto") |
| Recomendado da revalidação 11 | fecha | a mensagem do prazo vencido cita o `git` lento (`hooks/_comum.py:2258`) |

### Fora do bloco
- **Testes que rodei**, na cópia limpa (`git archive e8b2af9`, em `$TMPDIR/tech-lead-lote-leitura-hook/orig`):
  - `test_divisao_esta_na_classe`, `test_g1_esta_na_classe` e `test_propriedade_do_lancador_que_divide_texto_com_marcador`: `Ran 3 tests in 108.408s OK`;
  - `Hooks.test_fixtures` e `test_corpus_nos_dois_hooks`: `Ran 2 tests in 67.033s OK`.

  A suíte completa não rodou: o brief limita a execução aos testes do lote, e o pre-push roda a suíte.
- **Commits:** em Conventional Commits em português, um por passo (corpus, correção, textos e FD14).
- O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar. O `docs/engineering/achados-recorrentes.md` (PA-7) está sem linhas, e não há item a conferir.
- **Segurança:** é do E2.1 e não foi refeita aqui. A3 vai como cartão para o `security-engineer`, e A1 e A2 são da mesma classe do A1 dele.
