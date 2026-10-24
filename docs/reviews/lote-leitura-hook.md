---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 6d5252db2c3799d8114fb432647d4ae0dfcb5109
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-leitura-hook (revalidação 14, volta pela opção A da rev13)

Pedido RET-LEITURA-HOOK-G-REV, E1.1. Sou revisor independente e não implementei esta volta (`R-REVIEW`). O parecer anterior (revalidação 13, `reprovado`, A1 a A3) está em `c48f097`, sobre `1b4b0d8`.

**Delta lido.** O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` deu `1b4b0d8..6d5252d`. O commit do autor é `ef78e68`. O merge `6d5252d` só traz a `develop` (`ba57c0b`, segundo pai): `git diff ef78e68 6d5252d -- hooks/ tests/test_hooks.py docs/hooks.md` sai vazio. Li inteiro:
- `hooks/_comum.py:1738-1905` (`LANCADORES`, `LancadorDemais`, `TETO_FORA_DA_TABELA`, `separar_lancadores`, `_ler_lancadores`), `1925-1932` (`achado_do_lancador`) e `2066-2081` (`texto_dividido_do_env`);
- `hooks/conformidade.py:27-34`, `346-348` (`sem_lancadores`), `840-900` (`segmento`, `leitura_do_segmento`), `1375-1407` (`rotulo_na_sessao_do_forge`) e `1699-1711` (`alvos_de_escrita`);
- `tests/test_hooks.py` do delta (`ler_dentro_do_comando` e os testes de 2885 a 3300, da propriedade ao item 7), os 17 fixtures `lancador-sem-marcador-*`, `docs/hooks.md:95` e `changelog.d/lote-leitura-hook.md:14`.

Fica como "já lido" o que vem antes de `1b4b0d8` (revalidações 1 a 13) e os arquivos que o merge traz da `develop` (`scripts/reexecutar-provas.py`, `tests/catraca.py`, o CI e o resto do `--stat`).

**Critério.** A decisão "A" do dono de 2026-10-24 sobre a rev13 (opção A da proposta `lote-leitura-hook-caminho-rev13.md`, seção 2A, itens 1 a 7, e os textos da seção 3.1), a decisão "A" da rev12, que segue inteira, a decisão "A" de 2026-10-22 (voltas por classe) e o piso da `develop`.

## Achados
- A1 (bloqueante) hooks/_comum.py:1888 · classe "lançador que divide texto" (2.ª volta seguida). A leitura a mais com texto dividido de aspas abertas apaga as outras: env -uS'"' cat .env e env --spl='"' cat .env davam 2 na develop e dão 0; env -aS'"' cat .env e env -aS'"' rm -rf .git dão 0, e o env real lê e apaga
- A2 (recomendado) tests/test_hooks.py:2962 · a propriedade do item 1 amostra as palavras (uma em 5 no env, uma em 29 nos outros, uma em 97 nas posições, dois corpos no -S em grupo); o critério pede cada palavra
- A3 (recomendado) tests/test_hooks.py:2918 · as duas exclusões da propriedade não estão escritas onde a propriedade é prometida (docs/hooks.md:95 diz "exige 2 sempre que o corpo sozinho dá 2"); a (b) muda a saída contra a develop em env -iu X cd .git; rm -rf . (2 para 0, sem efeito real)

## Parecer
**Reprovado.** A volta fecha os três achados da revalidação 13 e cumpre os itens 1 a 7 do critério de fim. Falta um caso da mesma classe: quando uma leitura a mais não se lê, o hook descarta também a leitura sem valor, e com ela a regra da linha.

**A1, explicação.** Em `_ler_lancadores` (linha 1888), a leitura possível do texto dividido chama `shlex.split` na hora, durante a leitura sem valor. Se o texto tem aspas abertas, o `ValueError` sobe por `separar_lancadores` inteiro. O `segmento` (`conformidade.py:854`) manda a linha a `ilegivel`, que só recusa o que aponta para o Forge, e a autoria (`conformidade.py:1706`) pula a parte inteira. A leitura sem valor (`cat .env`) e a com valor nunca rodam. Isso contraria o texto aprovado pelo dono em `docs/hooks.md:95`: "recusam se qualquer leitura recusa" e "a leitura a mais só soma recusa". A proposta (seção 2A) mandou o `ValueError` a `ilegivel` pensando no `-S` por extenso, em que o texto é o único comando. Para a leitura possível, ela não previu o caso.

Prova (`$TMPDIR/tech-lead-lote-leitura-hook/g/sonda.py`, que roda o `conformidade` sem o marcador; a base é `git archive d150ec8`):

| Texto (só `conformidade`, sem marcador) | develop | lote | `env` real, hooks desligados |
|---|---|---|---|
| `env -uS'"' cat .env` | 2 | 0 | GNU 9.7 e uutils 0.8.0 imprimem o `.env` |
| `env --spl='"' cat .env` | 2 | 0 | o uutils (o `/usr/bin/env` da máquina) imprime o `.env` |
| `env -aS'"' cat .env` | 0 | 0 | GNU e uutils imprimem o `.env` |
| `env -aS'"' rm -rf .git` | 0 | 0 | GNU e uutils apagam o `.git` falso |
| `env -iS'"' cat .env` | 0 | 0 | o uutils imprime o `.env` |
| `env -aS'"' tee docs/reviews/x.md` (`alvos_de_escrita`) | — | `[]` | — (com `-iu X`, o alvo aparece) |
| controle `env -S'"' cat .env` | 0 | 0 | os dois param ("no terminating quote") |

As duas primeiras linhas são regressão contra a `develop`, com efeito real. As outras ficam abaixo da promessa da volta. A causa é uma só. A correção cabe dentro da opção A, sem tabela: a leitura possível que não se divide sai do conjunto, ou vai a `ilegivel` sozinha, e as outras leituras rodam. O caminho, porém, não é meu.

**Contagem por classe** (decisão "A" de 2026-10-22). "Lançador que divide texto" foi o A2 da revalidação 13 (3.ª volta) e volta agora como A1: é a 2.ª volta seguida. O autor chamou a classe desta volta de "regra sem o marcador atrás de lançador com opção fora da tabela", que junta o A1 e o A2 da revalidação 13. Pelos dois nomes, é volta seguida. Pela decisão, **a entrega para**: o `software-architect` propõe o caminho e o dono decide (`R-DECISAO`). A proposta rev13 (seção 5) já previa que, nesse caso, sobra a opção D com o FD17. Este achado tem correção local, e cabe ao arquiteto dizer se a D é precisa.

**A2, explicação.** O critério (item 1, "Palavras") pede cada caractere, cada par de letras e cada prefixo das longas, para cada lançador. O gerador usa `passo_env=5`, `passo_outros=29` e `passo_posicoes=97`, e no `-S` em grupo só dois corpos além dos fixos (`[:2]`, linha 2999). Rodei a propriedade sem amostra (`prop_cheia.py`, `passo_*=1`): 118 corpos, 384.704 formas, **0 liberadas**, em 452,5 s. O comportamento está certo no alfabeto inteiro, e a amostra é o preço do limite de 60 s do item 1. Mesmo assim, ela deixa a propriedade mais fraca do que o texto de `docs/hooks.md:95` diz ("gera as mesmas palavras"). A sugestão é variar o deslocamento da amostra entre as rodadas, ou rodar o alfabeto inteiro num alvo lento. Nem o alfabeto inteiro pegaria o A1, porque nenhuma palavra dele tem o `S` seguido de aspas (os pares são só de letras).

**Julgamento das duas exclusões** (pedido no brief):
- **(a) palavras em que o `env` sempre divide (`-S…`, `--split-string…`), fora de `L w C` e `L w X C`: aceita.** Nelas o texto dividido é o programa, e o corpo vira argumento dele. Em `env -Sx cat .env`, o GNU e o uutils rodam `x`, e não o `cat`. O oráculo "o corpo sozinho" não vale aí. A própria seção 2A manda o `-S` por extenso ficar com a leitura única de hoje. O "sem exceção" do item 1, lido ao pé da letra, contradiz essa parte da proposta, e o autor seguiu o "O que muda". Os controles do item 2 cobrem o `-S` por extenso.
- **(b) corpos que mudam o estado do shell (`cd`, `export`…) atrás de lançador: aceita.** A decisão do dono diz que "a pasta e as variáveis que seguem são as da leitura sem valor". Atrás de `env`, o `cd` roda noutro processo (nesta máquina, `env cd` dá "No such file or directory"), então o oráculo também não vale. Há uma consequência que a proposta não viu: o piso "por construção" falha aqui. `env -iu X cd .git; rm -rf .` dava 2 na `develop`, que tomava o `X` por valor e a pasta por `.git`, e agora dá 0. Não há efeito real, porque a pasta real segue na raiz e o GNU `rm` recusa o `.`. Por isso é o A3, recomendado.

Os textos de `docs/hooks.md:95` estão literais: as duas citações da seção 3.1 aparecem inteiras, e "Sem marcador, nada muda." saiu (comparação por script). Só que o texto promete "exige 2 sempre que o corpo sozinho dá 2", sem as exceções (a) e (b). A sugestão é registrá-las na emenda do cartão ADR0011-EMENDA, sem mexer no texto literal deste lote.

### Revalidação 13: o que fechou
| Achado | Estado | Evidência (`sonda.py`, sem marcador) |
|---|---|---|
| A1 (`-iu X`, `-iC`) | fechou | `env -iu X cat .env`, `env -iC / cat .env` e `env -iu X rm -rf .git`: 2, como na `develop` |
| A2 (`-iS'…'`, `-vS'…'`) | fechou nas formas do achado | `env -iS'cat .env'` e `env -vS'cat .env'`: 2. A classe volta pelo caso das aspas abertas (A1 acima) |
| A3 (teste da dimensão, item 5 da rev12) | fechou | a propriedade sem marcador existe e passa; o item 5 da rev12 está no commit `ef78e68`, no fragmento e em `test_fixtures_libera_nao_tem_lancador_com_opcao_fora_da_tabela` |

### Critério de fim da opção A
| Item | Estado | Evidência |
|---|---|---|
| Leituras em `separar_lancadores` | certas, salvo o A1 | a sem valor primeiro; a com valor em `i + 1`; o texto dividido só no `env`; a palavra da tabela e o `-S` certo com leitura única; `test_separar_lancadores_devolve_as_leituras_possiveis` |
| Função única do `S` | certa | `texto_dividido_do_env` serve à leitura e a `achado_do_lancador`; `valor_do_split_string` saiu; `test_o_teste_do_s_do_env_e_um_so` confere o alfabeto inteiro do `env` |
| Três chamadores pela união | certos | o `segmento` copia `ambiente`, `lancador_recusado` e `ramos`, e devolve a pasta da primeira leitura; `lancador_recusado`, `reavaliacao` e `perguntas` só somam; `rotulo_na_sessao_do_forge` e `alvos_de_escrita` percorrem `sem_lancadores` |
| Teto K = 3 (`LancadorDemais`) | certo | conta por caminho, com os lançadores encadeados; acima, recusa com `CONTORNO_DO_LANCADOR`; no rótulo, cai no `except ValueError`, que exige o dono se a linha cita o rótulo; medido em milissegundos |
| Itens 1 a 7 | verdes | os 15 testes abaixo; o item 6 (corpus e T9b com o marcador) pelo pre-push da entrega (suíte completa, 1962 testes OK, histórico do pedido); o 7 no commit e no fragmento |
| O que não volta | conferido | sem `[uC]`, `ENV_COM_VALOR_CURTA`, `ENV_LONGAS_COM_VALOR`, `env_divide_texto` nem `valor_do_split_string` |
| Commits | limpos | `ef78e68` em Conventional Commits em português, com a classe e o critério; o merge da `develop` sem reescrever |

### Fora do bloco
- **Testes que rodei**, na cópia limpa (`git archive 6d5252d`, em `$TMPDIR/tech-lead-lote-leitura-hook/g/lote`): os 12 testes novos da volta, `test_propriedade_do_alfabeto_de_opcoes_do_lancador`, `test_mutacoes_do_lancador_ficam_vermelhas` e `test_propriedade_do_lancador_que_divide_texto_com_marcador`, com `Ran 15 tests in 115.486s OK`. A suíte completa não rodou, porque o brief limita a execução aos testes do lote.
- **Teto M14:** não vale para o `lote-leitura-hook` (decisão M14).
- O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar. O PA-7 (`docs/engineering/achados-recorrentes.md`) está sem linhas, e não há item a conferir. A classe "lançador que divide texto" já se repetiu e cabe lá, mas isso fica fora deste commit, que o brief limita ao parecer.
- **Segurança:** é do E2.1 e não foi refeita aqui. Vão como cartão para o `security-engineer`: o A1, que é segredo e apagar o `.git` com gatilho; e um furo anterior ao lote, fora do delta. `env cd /tmp/y; rm -rf .forge` dá 0 na `develop` e no lote, porque o hook toma o `env cd` como troca de pasta. O `env` não acha o `cd`, e o `rm` apaga o `.forge` da raiz (provado numa pasta falsa).
