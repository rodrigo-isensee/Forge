---
tipo: qa
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 1b4b0d8b060379d6e078d5ef15c2c63676e41b87
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-24
---
# QA: lote-leitura-hook (volta pela opção A: lista positiva dos lançadores, revalidação 13)

Pedido RET-LEITURA-HOOK-F-REV, E3.1, em paralelo com o review e a segurança (decisão ACELERA-RODADA "A", item 4). Sem especificação de UX: as obrigações são as decisões do dono em `RET-LEITURA-HOOK-F` e `RET-LEITURA-HOOK-F-REV` (opção A com o marcador crítico; sem o marcador, "nada disto é regressão" contra a develop; teste instável corrigido no lote) e os pareceres da revalidação 12. O código testado é o de `1b4b0d8`: o commit seguinte da branch (`c48f097`) só muda `docs/reviews/lote-leitura-hook.md`. Tudo foi rodado em cópias por `git archive` em `$TMPDIR/qa-engineer-lote-leitura-hook/v13/` (`lote` = `1b4b0d8`, `base` = `d150ec8`, a develop do lote). Vermelho antes do verde e `forge-mutante`: não rodados por este QA (o brief não os pediu, e a branch não traz `tests/mutantes/lote-leitura-hook.json`); o review registra `test_mutacoes_do_lancador_ficam_vermelhas` verde.

## Achados
- A1 (bloqueante) hooks/_comum.py:1848 · classe "opção de lançador que o hook não modela": sem o marcador, `env -iu X cat .env`, `env -iu X rm -rf .git` e `env -iC / cat .env` davam rc 2 na develop e dão 0 no lote; o `env` real roda o comando depois do valor (regressão contra a develop; bug `lote-leitura-hook-2`)
- A2 (bloqueante) hooks/_comum.py:2030 · classe "lançador que divide texto": sem o marcador, `env -iS'cat .env'` e `env -vS'cat .env'` davam rc 2 na develop e dão 0 no lote (mesmo bug `lote-leitura-hook-2`)
- A3 (recomendado) tests/test_hooks.py:2711 · nenhum teste compara, sem o marcador, as regras de segredo e de apagar o `.git` atrás de lançador com opção fora da tabela com a leitura sem o lançador; foi o que deixou A1 e A2 passarem (confere com o A3 do review)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Opção A: com ação crítica, lançador só passa com as opções da tabela `LANCADORES`; as demais recusam, nos dois hooks | ES1 a ES17 ponta a ponta (abaixo) e `test_propriedade_do_alfabeto_de_opcoes_do_lancador` | opção por extenso e uma por palavra; opção fora da tabela | passou |
| Os três achados da rev. 12 (`env -a x -S …`, `-S` colado do uutils, `env -a x git push`) fecham | formas RV-A2a a RV-A3d (abaixo) e `test_lancador_fora_da_tabela_com_efeito_real` | `-a`/`--argv0`, `-S` depois de `NOME=valor`, de `-` e de `-f` | passou |
| Saem `env_divide_texto`, as duas tabelas do `env` e o regex da linha 1765 | `test_mutacoes_do_lancador_ficam_vermelhas` | n/a | passou |
| Falso positivo FD16 aceito, com o contorno | FD16a a FD16d ponta a ponta (abaixo) | `env` sem `-S` libera | passou |
| FD14 e o contorno de cada forma | FD14a a FD14d e a linha legítima por contorno (abaixo) | palavra entre outras | passou |
| Teste instável do T9b corrigido no lote (caminho 1) | `test_t9b_monta_os_registradores_antes_de_rodar`, `test_t9b_registrador_que_nao_roda_e_falha_do_arnes`, par `test_g1_esta_na_classe` + `test_divisao_esta_na_classe` em paralelo sob carga | rc 126 / "Text file busy" falha com a causa | passou; bug `lote-leitura-hook-1` fecha |
| Sem o marcador, "nada disto é regressão" contra a develop (piso da proposta) | sonda `s4.py`, base contra lote (abaixo) | `-iu`, `-iC`, `-iS'…'`, `-vS'…'` | **falhou** (A1, A2) |

## Cenários e resultado real
Ponta a ponta, nos dois hooks (`python3 hooks/<hook>.py` com a entrada JSON do Claude Code, repositório temporário montado pelo `Fixture` do corpus, `HOME` limpo; sondas `v13/s1.py`, `s3.py` e `s4.py`):
- **Formas dos pareceres de revalidação 12** (`s3.py`): 86 de 86 como o esperado, 0 falhas. ES1 a ES17, EA1 a EA11 e FD16a a FD16l ponta a ponta, mais as formas da rev. 12 com o marcador: `env X=1 -S'bash -c "…"'`, `env - -S'…'`, `env -i X=1 -S'…'`, `env -f /dev/null -S'…'` (RV-A2a a RV-A2d, rc 2 nos dois hooks) e `env -a x`/`env --argv0 x` antes de `git push` (`conformidade`) e de `gh pr merge` (`parecer`) (RV-A3a a RV-A3d, rc 2). A mensagem recusa por `env -S` (conformidade: "R-CONFORMIDADE: `env -S` na chamada com ação crítica…"; parecer: "R-REVIEW: `env -S` na chamada com gh pr, gh api, merge ou pull…").
- **Falsos positivos novos do FD16 e contornos** (`s1.py`, 44 de 44, 0 falhas): FD16a (`env -S 'echo x'; git push origin feature/x`, `conformidade`) e FD16b (a mesma forma com `gh pr create`, `parecer`) recusam com rc 2 (falso positivo aceito pela decisão do dono); os contornos FD16c (`env X=1 git push origin feature/x`) e FD16d (`env X=1 gh pr create --draft …`) saem rc 0, sem mensagem. FD14, uma linha legítima por contorno, todas rc 0: `git push origin feature/x`, `gh pr create --draft … --title "trocar eval"`, `git pull`, `grep -rn 'bash -c' hooks/ && git push origin feature/x`, `env VAR=x make test && git push origin feature/x` e a variante com `gh pr create --draft`.
- **Sem o marcador, base contra lote** (`s4.py`, `conformidade`, rc develop / lote):

| Comando | develop | lote |
|---|---|---|
| `env -iu X cat .env` | 2 | 0 (regressão) |
| `env -iu X rm -rf .git` | 2 | 0 (regressão) |
| `env -iC / cat .env` | 2 | 0 (regressão) |
| `env -iS'cat .env'` | 2 | 0 (regressão) |
| `env -vS'cat .env'` | 2 | 0 (regressão) |
| `env -u X cat .env`, `env -S'cat .env'`, `env -i -S 'cat .env'`, `env cat .env`, `cat .env`, `rm -rf .git` | 2 | 2 |
| `env -a x cat .env`, `env -f /dev/null cat .env`, `env --un X cat .env`, `env -S'cat .env "'` | 0 | 0 (igual) |

  Sem os hooks, `env -iu X echo OK` imprime `OK` nesta máquina (uutils 0.8.0): o `env` real roda o comando depois do valor, então o rc 0 do lote deixa passar a leitura do `.env` e o `rm -rf .git`. Confirma o A1 e o A2 do review, e abre o bug `docs/qa/bugs/lote-leitura-hook-2-regressao-sem-marcador-lancador-opcao.md` (alta).
- **Reprodução do bug `lote-leitura-hook-1`** (quatro cópias em paralelo de `python3 -m unittest discover -s tests -p test_hooks.py -k test_g1_esta_na_classe -k test_divisao_esta_na_classe`, cinco rodadas, mais quatro laços de CPU ocupada; carga 14,7 em 8 CPUs, por `uptime` ao fim): 20 de 20 cópias `Ran 2 tests … OK`, rc 0 (20,6 a 22,4 s cada); antes do caminho 1, no `e8b2af9`, 3 de 4 cópias falhavam por ETXTBSY. **O bug fecha.** Uma tentativa anterior desta rodada, lançada com `setsid` em segundo plano, morreu com o comando e não produziu logs; foi refeita com o processo em segundo plano da própria ferramenta.
- **Testes do lote** (`CorpusHeredocVoltaUnica`, filtros `lancador`, `t9b`, `test_corpus_nos_dois_hooks`, `mutacoes`): `Ran 8 tests in 179.214s OK`. Suíte completa não rodada por este QA (o pre-push a roda uma vez, decisão ACELERA-RODADA "A", item 1).
- PA-7 (`docs/engineering/achados-recorrentes.md`): sem linhas ("nenhum ainda"); nada a conferir.

## Riscos
- Os dois bloqueantes são a regressão sem o marcador que o review já provou; a classe repete a 2.ª e a 3.ª volta seguidas, e a decisão de 2026-10-22 manda a entrega parar para o `software-architect` propor o caminho e o dono decidir (`R-DECISAO`). A3 do review (a leitura sem marcador) e o desvio declarado pelo autor são desse mesmo caminho.
- Com o marcador a volta está certa e o teste instável fechou; o parecer volta a `aprovado` quando A1 e A2 fecharem, sem outra pendência deste QA.
