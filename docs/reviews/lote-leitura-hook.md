---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 1b4b0d8b060379d6e078d5ef15c2c63676e41b87
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-leitura-hook (revalidação 13, volta pela opção A da revalidação 12)

Pedido RET-LEITURA-HOOK-F-REV, E1.1. Sou revisor independente: não implementei esta volta (`R-REVIEW`). O parecer anterior (revalidação 12, `reprovado`, A1 a A4) está em `8e9fc07`, sobre `e8b2af9`.

**Delta lido.** O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` deu `e8b2af9..1b4b0d8`. Os commits do autor são `b438b21` (caminho 1 do teste instável), `e8cc9e4` (opção A) e `f418569` (textos de `docs/hooks.md:95`). O merge `1b4b0d8` só traz a `develop` (`83d5faa`, segundo pai): nenhum arquivo de `hooks/` muda nele, e de `tests/` só `test_conferir_reversao.py` e `test_forge.py`, que vêm da `develop`. Li inteiro:
- `hooks/_comum.py:1738-1888` (`LANCADORES`, `opcao_modelada`, `opcao_fora_da_tabela`, `separar_lancadores`, `achado_do_lancador`), `1897-1925` (`reavaliacao_das_palavras`), `1952-1966` e `2022-2033` (`valor_do_split_string`);
- `hooks/conformidade.py:31` e `741-746`, `hooks/parecer.py:21-25` e `401-406`;
- `tests/test_hooks.py` do delta: `executar_em_lote` (564-605), `montar_registradores_do_t9b`, `rodar_no_bash_do_t9b`, `rodar_em_paralelo_no_t9b`, `test_propriedade_do_alfabeto_de_opcoes_do_lancador`, `FORMAS_DO_LANCADOR`, `test_lancador_fora_da_tabela_com_efeito_real`, `test_env_nao_le_opcao_depois_do_comando`, `test_mutacoes_do_lancador_ficam_vermelhas`, `test_t9b_monta_os_registradores_antes_de_rodar` e `test_t9b_registrador_que_nao_roda_e_falha_do_arnes`;
- `tests/fixtures/heredoc-volta-unica.json` (o corpus do T9b, `CORPUS_VOLTA_UNICA`), `docs/hooks.md:95` e `changelog.d/lote-leitura-hook.md:13`.

Fica como "já lido" o que vem antes de `e8b2af9` (revalidações 1 a 12) e os arquivos que o merge traz da `develop`. Uma exceção: reli `separar_lancadores` e `valor_do_split_string` da base `d150ec8` (`hooks/conformidade.py:390-433`), para julgar o desvio declarado pelo autor ("como a develop").

**Critério.** A decisão "A" do dono de 2026-10-24 (opção A da proposta `lote-leitura-hook-caminho-rev12.md`, seção 2A, e caminho 1 da seção 3), os textos da seção 4.1, a decisão "A" de 2026-10-22 (voltas por classe) e o piso da M5 que a proposta registra: "nada disto é regressão" contra a `develop`.

## Achados
- A1 (bloqueante) hooks/_comum.py:1848 · classe "opção de lançador que o hook não modela" (2.ª volta seguida). Regressão contra a develop, sem marcador: `env -iu X cat .env` e `env -iu X rm -rf .git` davam 2 e agora dão 0; o env real lê e apaga
- A2 (bloqueante) hooks/_comum.py:2030 · classe "lançador que divide texto" (3.ª volta). Regressão contra a develop, sem marcador: `env -iS'cat .env'` e `env -vS'cat .env'` davam 2 (a develop dividia o grupo) e agora dão 0; o GNU e o uutils rodam o cat
- A3 (recomendado) tests/test_hooks.py:2711 · nenhum teste cobre as regras sem marcador (segredo, apagar o .git) atrás de lançador com opção fora da tabela, o que deixou A1 e A2 passarem; falta também o registro do item 5 do critério (fixtures -libera)

## Parecer
**Reprovado.** A opção A está certa onde o marcador crítico está na chamada: os três achados da revalidação 12 fecham, e o critério de fim passa. A falha está no caminho sem o marcador, que o desvio do autor quis proteger. Ali, a volta perdeu leituras que a `develop` fazia, e duas regras que não dependem do marcador deixaram de ver o comando.

**A1, explicação.** A base (`d150ec8`, `hooks/conformidade.py:408`) lia o grupo curto do `env` terminado em `u` ou `C` com o regex `-[a-zA-Z]*[uC]`, e tomava a palavra seguinte como valor. A decisão do dono tirou esse regex. Agora `separar_lancadores` (linha 1848) lê `-iu` como opção sem valor, então o `X` vira o comando. A recusa da linha cobre isso só com o marcador. Prova (`$TMPDIR/tech-lead-lote-leitura-hook/f/sonda_f2.py`, que roda os hooks sem o filtro do marcador; a base é `git archive d150ec8` com os testes do lote):

| Texto (só `conformidade`, sem marcador) | develop | lote |
|---|---|---|
| `env -iu X cat .env` | 2 (ler .env) | 0 |
| `env -iu X rm -rf .git` | 2 (o .git da raiz) | 0 |
| `env -iC / cat .env` | 2 | 0 |
| `env -u X cat .env` (controle) | 2 | 2 |

Com os hooks desligados, o `/usr/bin/env` (uutils 0.8.0) e o `gnuenv` (GNU 9.7) rodam `env -iu X cat .env` e imprimem o conteúdo (`$TMPDIR/tech-lead-lote-leitura-hook/f/efeito`). O `-a`, o `-f` e o `--un` sem marcador saem 0 nos dois lados. Esses não são regressão, e ficam como estavam.

**A2, explicação.** A base dividia o `-S` também no grupo curto (`valor_do_split_string`, base `:428-432`). Agora ela só segue o `-S` por extenso (linha 2030), como a proposta pede para a recusa. Sem o marcador, porém, o texto do `-iS'…'` não é dividido, e as regras não o leem. `env -iS'cat .env'` e `env -vS'cat .env'` davam 2 e agora dão 0. O GNU e o uutils rodam o `cat` nas duas formas. A classe é a mesma da revalidação 11 e da 12: o texto que o `env` divide some das regras.

**Julgamento do desvio declarado** (DECISÃO TÉCNICA do Jarvis). A intenção está certa: sem o marcador, as regras da linha precisam continuar rodando. A premissa "como a develop", porém, é falsa para o grupo curto do `env`. A `develop` lia o `-iu X` e dividia o `-iS…`, e a volta lê os dois como opção sem valor. A alternativa da proposta, "não analisável", também não protege. Sem o marcador, o texto não analisável sai 0 nos dois lados (`env -S'cat .env "'` dá 0 na `develop` e no lote). Nenhuma das duas leituras guarda as regras sem marcador. Por isso o desvio, sozinho, não reprova, mas A1 e A2 reprovam.

**Uma sugestão para a proposta, sem decidir por ela.** Sem o marcador, a opção fora da tabela poderia levar as regras a ler as duas leituras possíveis: a palavra seguinte como valor e como comando, e o resto do grupo com `S` como texto dividido. Uma leitura extra não liberaria nada, só recusaria mais, e o hook continuaria sem imitar nenhum `env`. A outra saída é recusar, também sem o marcador, o lançador com opção fora da tabela quando o resto da linha toca uma regra. O caminho é do `software-architect` com o dono.

**Contagem por classe** (decisão "A" de 2026-10-22):
- "opção de lançador que o hook não modela": a 1.ª volta foi o A3 da revalidação 12, e A1 é a 2.ª volta seguida.
- "lançador que divide texto": a revalidação 11 e a 12 foram a 1.ª e a 2.ª volta, e A2 é a 3.ª.

Pela decisão, **a entrega para**: o `software-architect` propõe o caminho e o dono decide (`R-DECISAO`). As duas classes já foram registradas mais de uma vez, então cabem em `docs/engineering/achados-recorrentes.md` (PA-7). Isso não entra aqui, porque o brief limita o commit a este parecer.

**A3, explicação.** O critério de fim da opção A só mede o caminho com o marcador. Um teste do mesmo alfabeto, sem o marcador e com uma regra que não depende dele (`cat .env`, `rm -rf .git`), comparado com a leitura sem o lançador, teria ficado vermelho em A1 e A2. Sobre o item 5 do critério: há dois fixtures `-libera` com lançador e opção (`lancador-sudo-u-npm-test-libera.json`, `lancador-nice-git-status-libera.json`), os dois sem marcador e sem mudança. O resultado não está registrado no commit nem no fragmento.

### Revalidação 12: o que fechou
| Achado | Estado | Evidência (`sonda_f1.py`, hooks ligados) |
|---|---|---|
| A1 (`env -a x -S …`) | fechou | `env -a x -S'bash -c …'`, `env -i -a x …`, `env -u X -a x …`, `env -C / -a x …`, `nice -5 env -a x …` e `timeout -v 5 env -a x …`: 2 / 2 |
| A2 (o `-S` colado do uutils) | fechou | `env X=1 -S'…'`, `env - -S'…'` e `env -iS'…'`: 2 / 2 |
| A3 (`env -a x git push`) | fechou | `env -a x`, `env -a cat`, `env --argv0 cat`, `env -f /dev/null`, `sudo -s`, `sudo -i` e `exec -a cat` com o `git push`: 2 no `conformidade` |
| A4 (o `ETXTBSY`) | fechou no código | caminho 1 aplicado; os itens 2 e 3 do critério são testes verdes (abaixo). O item 1 (5 rodadas sob carga) é a reprodução do QA e não foi refeito aqui |

As formas `env -- -a x git push` e `env -u -a x git push` saem 0 / 0. Elas não são achado: o `env` real roda o programa `-a` ou o `x`, e não o `git`. `env gh pr merge …` e `exec -a cat gh pr merge …` saem 0 no `parecer`, que é o A3 da segurança (cartão R5A-COP, fora desta volta).

### O que está certo na volta
| Item | Estado | Evidência |
|---|---|---|
| `LANCADORES` como fonte positiva | certo | booleanas, com valor e coladas; `separar_lancadores` e `opcao_fora_da_tabela` leem a mesma tabela; o comentário "as demais são booleanas" saiu |
| Recusa com o marcador nos dois hooks | certa | `motivo_da_reavaliacao` e `CONTORNO_DO_LANCADOR` nas duas mensagens; `achado_do_lancador` dá `env -S` para o `-S` em qualquer grafia |
| Saídas exigidas | certas | `ENV_COM_VALOR_CURTA`, `ENV_LONGAS_COM_VALOR`, `env_divide_texto` e `opcoes_do_lancador` não existem mais no código, e `test_mutacoes_do_lancador_ficam_vermelhas` confere |
| `memoria` de `opcao_fora_da_tabela` | certa | o resultado a partir de um índice só depende do índice e do lançador, então guardar cada passo do caminho é exato |
| Itens 1 a 4 do critério de fim de A | verdes | os testes da tabela abaixo |
| Textos da seção 4.1 | literais | as três citações da proposta estão inteiras em `docs/hooks.md:95`, e as frases antigas saíram (comparação por script) |
| Caminho 1 | certo | montagem na thread principal antes do pool, rc 126 ou "Text file busy" falham com a causa, e o pool de `executar_em_lote` também foi corrigido |
| Commits | limpos | Conventional Commits em português, um por item, e o merge da `develop` sem reescrever |

### Fora do bloco
- **Testes que rodei**, na cópia limpa (`git archive 1b4b0d8`, em `$TMPDIR/tech-lead-lote-leitura-hook/f/lote`): os quatro testes do critério de fim de A, os dois do caminho 1, `test_divisao_esta_na_classe`, `test_g1_esta_na_classe`, `test_corpus_nos_dois_hooks`, `test_propriedade_do_lancador_que_divide_texto_com_marcador` e os `test_fixtures`, com `Ran 12 tests in 169.830s OK`. A suíte completa não rodou: o brief limita a execução aos testes do lote.
- O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar. O `docs/engineering/achados-recorrentes.md` (PA-7) está sem linhas, e não há item a conferir.
- **Segurança:** é do E2.1 e não foi refeita aqui. A1 e A2 vão como cartão para o `security-engineer`, porque são segredo e apagar o `.git` com gatilho.
