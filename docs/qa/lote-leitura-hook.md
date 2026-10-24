---
tipo: qa
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 6d5252db2c3799d8114fb432647d4ae0dfcb5109
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-leitura-hook (revalidação 14: opção A da rev13, leituras possíveis sem o marcador, teto K = 3)

Pedido RET-LEITURA-HOOK-G-REV, E3.1, em paralelo com o review e a segurança (decisão ACELERA-RODADA "A", item 4). Sem especificação de UX: as obrigações são as decisões do dono em `RET-LEITURA-HOOK-G` (opção A da proposta `lote-leitura-hook-caminho-rev13`, itens 1 a 7 do critério de fim) e a promessa de `docs/hooks.md:95`. O código testado é o de `6d5252d` (o commit `ef78e68` mais o merge da develop `ba57c0b`); os commits seguintes da branch (`c17509a`, `72a6b97`) só trazem pareceres, e `hooks/` e `tests/` são iguais nos três. Tudo foi rodado em cópias por `git archive` em `$TMPDIR/qa-engineer-lote-leitura-hook/v14/` (`lote` = `6d5252d`, `base` = `ba57c0b`, a develop, cujos `hooks/` são iguais aos da `main` `83d5faa`). O parecer anterior, da revalidação 13, é de `1b4b0d8`.

## Achados
- A1 (bloqueante) hooks/_comum.py:1888 · classe "regra sem o marcador atrás de lançador com opção fora da tabela" (2.ª volta seguida): shlex.split do texto dividido com aspa aberta derruba as outras leituras; env -uS\' cat .env sai 0 (develop: 2) e o env real o roda (bug lote-leitura-hook-3)
- A2 (recomendado) tests/test_hooks.py:3011 · classe "propriedade que amostra o que o autor pensou": o gerador sem o marcador não gera grupo com u ou C antes do S e aspa sem par no resto, e foi o que deixou o A1 passar; com a develop como oráculo são 218 regressões nesse formato e 0 nas outras 49 888 formas
- A3 (recomendado) docs/hooks.md:95 · falso positivo novo sem o marcador, sem contorno registrado: env -Z echo cat .env, sudo -i echo cat .env e xargs -p echo cat .env saem 2 (develop: 0); o contorno é o texto numa palavra só (echo "cat .env"), que sai 0
- A4 (recomendado) tests/mutantes/lote-leitura-hook.json:1 · a branch não traz a spec de mutantes para o que muda em `hooks/`; a lista deste QA (abaixo) cobre cada linha de guarda do diff e todos os mutantes morreram, e o lote guarda as mutações dentro dos testes (`test_mutacoes_das_leituras_do_lancador_ficam_vermelhas`), então o autor pode declarar a spec

## Critério → teste → resultado
| Critério (RET-LEITURA-HOOK-G, itens do critério de fim da rev13) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 1. Propriedade sem o marcador: se o corpo sozinho dá 2, a forma com lançador e opção fora da tabela dá 2 | `test_propriedade_sem_marcador_atras_de_lancador_com_opcao_fora_da_tabela`, `test_formas_do_s_do_env_sem_marcador_tem_o_texto_colado_e_separado`; e a varredura deste QA com a develop como oráculo (`varrer2.py`, 49 888 formas) | `-`+0x21..0x7E, pares de letras, prefixos longos; aspa sem par no resto do grupo | passou (0 regressão em 49 888); **falhou** na forma com aspa aberta (A1, `varrer.py`: 218 regressões em 1384) |
| 2. As formas do bug `lote-leitura-hook-2` e `-a`, `-f`, `--un` saem 2; os controles seguem 2 | `test_regressoes_sem_marcador_do_lancador_dao_2` e `f1.log` ponta a ponta (abaixo) | `-iu`, `-iC`, `-iS'…'`, `-vS'…'`, `-iS"…"`; controles `-u`, `-S`, `-i` | passou |
| 3. Sonda viva: o `env` da máquina (GNU e uutils) imprime o `.env` falso nas formas | `test_sonda_viva_do_lancador_sem_marcador` e sonda deste QA (abaixo) | rc e saída do `env` real, sem rede | passou |
| 4. Teto K: K palavras fora da tabela decide em menos de 0,5 s e libera; K+1 recusa | `test_tempo_do_teto_das_leituras_do_lancador` e sonda deste QA (abaixo) | K = 3 e K + 1 = 4, com lançadores encadeados | passou |
| 5. Mutações: sem a leitura "com valor", sem o "texto dividido", estado da leitura a mais, sem o teto | `test_mutacoes_das_leituras_do_lancador_ficam_vermelhas`, `test_estado_da_leitura_a_mais_nao_segue_adiante`, `test_lancador_recusado_na_leitura_a_mais_soma_a_recusa`, `forge-mutante` deste QA (abaixo) | pasta e variáveis da leitura sem valor; recusa do lançador só soma | passou (10 de 10 morreram) |
| 6. O caminho com o marcador não muda | `test_corpus_nos_dois_hooks`, `test_propriedade_do_alfabeto_de_opcoes_do_lancador`, `Hooks.test_fixtures` (todos os fixtures, os 17 novos `lancador-sem-marcador-*` incluídos) | `CorpusHeredocVoltaUnica`, alfabeto com marcador | passou |
| 7. Registro da busca de lançador com opção nos fixtures `-libera` | `test_fixtures_libera_nao_tem_lancador_com_opcao_fora_da_tabela` | nenhum `-libera` com opção fora da tabela | passou |
| `docs/hooks.md:95`: sem o marcador, "recusam se qualquer leitura recusa" | A1 | texto dividido com aspa aberta | **falhou** |

## Cenários e resultado real
- **Formas do bug `lote-leitura-hook-2` e do item 2, ponta a ponta** (`python3 hooks/conformidade.py` com a entrada JSON do Claude Code, repositório temporário do `Fixture` do corpus, `HOME` limpo; `v14/sonda.py`, `f1.log`; rc develop / lote). Todas dão 2 no lote: `env -iu X cat .env` (2/2), `env -iu X rm -rf .git` (2/2), `env -iC / cat .env` (2/2), `env -iS'cat .env'` (2/2), `env -vS'cat .env'` (2/2), `env -iS"rm -rf .git"` (2/2), `env -iS 'cat .env'` e `env -iS"cat .env"` (2/2), `env -iu X env -iu Y env -iu Z env -iu W cat .env` (2/2). `env -a x cat .env`, `env -f /dev/null cat .env`, `env --un X cat .env`, `env --spl 'cat .env'`, `env --split=cat\ .env`, `env X=1 -iu Y cat .env` e `env - -iu Y cat .env` passam de 0 para 2 (endurecimento). Controles `env -u X cat .env`, `env -S'cat .env'`, `env -i cat .env`, `env -i -S 'cat .env'`, `env cat .env`, `cat .env`, `rm -rf .git`: 2/2. `sudo -Z`, `sudo -E -Z`, `nice -Z`, `timeout -Z 5` e `xargs -Z` com `cat .env` e `rm -rf .git`: 2/2. `env -iu X cd /tmp/y; rm -rf .git` e `env -Z X cd /tmp/y; rm -rf .forge`: 2/2 (a pasta é a da leitura sem valor). `env -S'cat .env "'` segue 0/0, como na develop (documentado).
- **Os dois hooks.** O `parecer` não chama `separar_lancadores` (confere com a segurança) e as regras dele dependem do marcador; sem o marcador não há regra a recusar nele. Com o marcador (`gh pr merge`, que é o marcador dos dois hooks), as 12 formas com opção fora da tabela (`-iu X`, `-iC /`, `-iS'…'`, `-vS'…'`, `-a x`, `-f /dev/null`, `--un X`, `-uS'"'`, `-vuS"'"`, `-Z`, quatro encadeados e `-S'…'`) saem 2 no `parecer` e no `conformidade` (a develop dava 0 em todas), e o controle `env -u X gh pr merge 5` segue 0/0, o que a decisão do dono manda (lançador com a opção da tabela passa). O rótulo `afrouxa-regra` atrás de `env -iS'…'`, `env -iu X`, `env -Z`, `env -iu X sh -c "…"` e do corpo em `$(…)`: 2/2 (modelo `lancador-sem-marcador-rotulo-env-is`, `f3.txt`, `f7.txt`). A escrita `tee .forge/versao` atrás de `env -iu X`, `-iS'…'`, `-vuS"'"` e `-uS'"'`: 2/2 (`f4.txt`).
- **Regressão contra a develop, formas sem aspa aberta** (`varrer2.py`, no mesmo processo, `decidir_na_guarda` de cada árvore): 49 888 formas (`env`, `sudo`, `command`, `nohup`, `time`, `exec`, `builtin`, `nice`, `setsid`, `stdbuf`, `timeout`, `xargs`; palavra `-`+0x21..0x7E, pares e trios de letras, abreviações longas; `L w C`, `L w X C`, `L A=1 w C`, `L w Y w C`, `L w -- cat .env` e encadeados com 2 lançadores), corpos `cat .env`, `rm -rf .git`, `echo x; cat .env`: **0 regressões**, 20 580 endurecimentos, 0 rc fora de 0 e 2, 62 s.
- **A1, regressão com aspa aberta** (`varrer.py`, 1384 formas de grupo com `S` e fragmento de aspa aberta; `sonda.py`): 218 regressões, todas com `u` ou `C` antes do `S` (`-uS`, `-CS`, `-iuS`, `-vuS`, `-iCS`, `-uiS`, `-uvS`, `-ivuS`, `-uCS`) e a forma `--spl='"'`; as 96 formas que a develop liberava saem 2. Exemplos (develop / lote): `env -uS\' cat .env` 2 / 0, `env -uS\' rm -rf .git` 2 / 0, `env -uS'"' cat .env` 2 / 0, `env -vuS"'" cat .env` 2 / 0, `env -iu X env -uS\' cat .env` 2 / 0. A mesma causa em `env -S'-u X cat .env'` (0 / 0) é o A2 da segurança, igual à develop: não é regressão e fica com ela.
- **Sonda viva do item 3** (hooks desligados, `.env` falso `SEGREDO_FALSO=abc123` no `$TMPDIR`, `HOME` no `$TMPDIR`, sem rede, `v14/viva/`): uutils 0.8.0 (`/usr/bin/env`) imprime o `.env` em `env -iu X cat .env`, `-iC <pasta> cat .env`, `-vScat .env`, `-uS\' cat .env` e `-uS'"' cat .env` (o `-iScat .env` não divide no uutils, como o teste do lote já registra); GNU 9.7 (`/usr/bin/gnuenv`) imprime nas seis, `-iScat .env` incluído. As formas do item 2 e as do A1 rodam de verdade.
- **O bug `lote-leitura-hook-2` fecha?** As formas relatadas (`-iu`, `-iC`, `-iS'…'`, `-vS'…'`) fecham: rc 2, e a varredura sem aspa aberta tem 0 regressões. A classe não fecha: o texto dividido com aspa aberta reabre a mesma regressão sem o marcador, no bug novo `docs/qa/bugs/lote-leitura-hook-3-texto-dividido-com-aspa-aberta-derruba-as-leituras.md` (alta). O estado do bug 2 foi atualizado.
- **Teto K** (`f5.txt`, `f6.txt`, `tempo.py`): `env -Z -Y -X ls`, `sudo -Z -Y -X ls`, `env -Z sudo -Z nice -Z ls` e `env -i -Z -Y -X ls` saem 0 (K = 3 palavras, ou menos); `env -a -b -c -d ls`, `env -Z -Y -X -W ls`, `sudo -Z -Y -X -W ls` e `env -Z sudo -Z nice -Z timeout -Z 5 ls` saem 2 (K + 1; a develop liberava); `env -i -u X -C /tmp -0 ls` (opções da tabela) sai 0. Tempo na `Guarda`, 800 segmentos `env -a -b -c ls;` (13,6 mil caracteres): 0,04 s na develop, 0,06 s no lote; os demais tamanhos, de 10 a 800, ficam abaixo de 0,06 s. Sem estouro do vigia.
- **Falsos positivos novos sem o marcador** (`f5.txt`, `f6.txt`): `env -Z echo cat .env`, `env -Z echo rm -rf .git`, `sudo -Z echo cat .env`, `sudo -S echo cat .env`, `sudo -i echo cat .env`, `xargs -p echo cat .env`, `timeout -Z 5 echo cat .env`, `stdbuf -Z echo cat .env` e `nice -Z echo cat .env` saem 2 (develop: 0); o contorno (o texto numa palavra só, `echo "cat .env"`, ou o lançador sem a opção) sai 0, e `env -a x echo ok`, `env -Z git commit -m "doc: cat .env"` e `env -Z grep -rn "cat .env" docs` saem 0 (A3). O falso positivo acima do teto tem o contorno do hook (opções da lista, uma por palavra), que sai 0.
- **Vermelho antes do verde** (forma manual: `hooks/_comum.py`, `conformidade.py` e `parecer.py` de `0242d70`, o head anterior à volta, sobre os testes de `6d5252d`; `forge-testes --vermelho` não serve aqui porque o merge da develop põe arquivos alheios ao lote no diff): 9 testes novos, `FAILED (failures=8, errors=2)` na base e `OK` no head (`Ran 9 tests`): caem `test_regressoes_sem_marcador_do_lancador_dao_2`, `test_tempo_do_teto_das_leituras_do_lancador`, `test_lancador_recusado_na_leitura_a_mais_soma_a_recusa`, `test_separar_lancadores_devolve_as_leituras_possiveis`, `test_o_teste_do_s_do_env_e_um_so`, `test_alvos_de_escrita_leem_a_uniao_das_leituras_do_lancador` (3 subtestes) e `test_propriedade_sem_marcador_atras_de_lancador_com_opcao_fora_da_tabela`; `test_estado_da_leitura_a_mais_nao_segue_adiante` e `test_formas_do_s_do_env_sem_marcador_tem_o_texto_colado_e_separado` passam na base (o estado só existe com a leitura a mais; o primeiro morre no mutante M4).
- **`forge-mutante`** (lista deste QA, `v14/mut.json`, `v14/mut3.json`, `v14/mut4.json`, contra `6d5252d` e `72a6b97`, um mutante por linha de guarda do diff: leitura "com valor", leitura "texto dividido", teto, o handler do teto, a leitura sem valor, a pasta da primeira leitura, a soma da recusa do lançador, a união nos alvos de escrita, a união no rótulo, o `certo` do `S`):
```
forge-mutante: pedido=lote-leitura-hook-g-qa rev=6d5252db2c37 spec=e7779fcd39ef…
M1 · morreu · hooks/_comum.py:1885      (sem a leitura "com valor")
M2 · morreu · hooks/_comum.py:1886      (sem o "texto dividido")
M3 · morreu · hooks/_comum.py:1882      (sem o teto)
M4 · morreu · hooks/conformidade.py:858 (pasta da última leitura)
M5 · morreu · hooks/conformidade.py:865 (recusa do lançador não soma)
M6 · morreu · hooks/conformidade.py:1708 (alvos só da primeira leitura)
M7 · morreu · hooks/conformidade.py:1389 (rótulo só da primeira leitura)
M8 · morreu · hooks/_comum.py:1876      (`certo` ignorado)
rc=0
--- rev=72a6b97 (hooks iguais), spec mut3.json
M9  · morreu · hooks/conformidade.py:850 (handler de LancadorDemais)
M10 · sobreviveu · hooks/_comum.py:1889 (só com o teste das regressões)   rc=1
--- spec mut4.json (M10 com a propriedade e o teste das leituras)
M10 · morreu · hooks/_comum.py:1889 (a leitura sem valor consome a próxima palavra)   rc=0
```
  M10 sobrevive só quando o teste das regressões o enfrenta sozinho (as formas dele têm a leitura "com valor" como a verdadeira); com a propriedade e o teste das leituras ele morre, então não é achado. A primeira rodada de M1 a M8 saiu descartada (`a árvore de trabalho mudou durante a rodada`, porque eu gravei o relatório do bug na worktree); refeita com a árvore limpa, saída acima. Nenhum mutante cobre a aspa aberta, porque nenhum teste do lote a gera (A1, A2).
- **Testes do lote, rodados por este QA** (cópia `v14/lote`, só os do lote; a suíte completa roda uma vez no pre-push, decisão ACELERA-RODADA "A", item 1): 13 testes do item (regressões, sonda viva, teto, estado, recusa do lançador, mutações das leituras e da rev12, alvos de escrita, fixtures `-libera`, leituras possíveis, teste do `S`, formas do `S`, propriedade): `Ran 13 tests in 19.948s OK`; `test_corpus_nos_dois_hooks`, `Hooks.test_fixtures` e o alfabeto com marcador: `Ran 3 tests in 92.838s OK`. `scripts/validar-plugin.sh` sobre a branch: `Validation passed`.
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem linhas ("nenhum ainda"); nada a conferir.

## Riscos
- O A1 é a 2.ª volta seguida da classe "regra sem o marcador atrás de lançador com opção fora da tabela" (a 1.ª foi o bug `lote-leitura-hook-2`, revalidação 13); pela decisão do dono de 2026-10-22 a entrega para e o `software-architect` propõe o caminho. A causa é uma só e estreita (uma falha de `shlex.split` numa leitura a mais não pode derrubar as outras), e o resto da volta está certo: 0 regressões em 49 888 formas, os critérios 1 a 7 verdes fora o A1, 10 mutantes mortos.
- O teste de propriedade confere o que o autor gerou: a develop como oráculo achou o que o oráculo do lote não achou. A varredura com a develop como oráculo vale como teste de regressão do lote (A2).
- O teste instável do T9b (bug `lote-leitura-hook-1`) segue fechado: nenhum teste do lote falhou por carga nesta rodada.
