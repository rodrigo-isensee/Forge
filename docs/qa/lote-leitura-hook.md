---
tipo: qa
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: e8b2af94d1e21a16899980910665d50e20404b2e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
aceite_usuario: sim
data: 2026-10-24
---
# QA: lote-leitura-hook (opção C da rev. 10, bloco T, classe "lançador que divide texto", rev. 11)

Paralelo ao review e à segurança (decisão ACELERA-RODADA "A", item 4). Sem especificação de UX: as obrigações são as decisões do dono em `RET-LEITURA-HOOK-E` (opção C, blocos T e X) e a volta rev. 11 (A1 da segurança, `env` que divide texto); cada uma vira uma linha da tabela. Vermelho antes do verde e mutação: não rodados por este QA (o brief não os pediu); o review registra 5 mutações vermelhas no pedido. A conferência do diff contra as obrigações não revelou escopo fora delas.

## Achados
- A1 (recomendado) tests/test_hooks.py:2435 · o oráculo do bash (`rodar_no_bash_do_t9b`) ignora rc e stderr e falha de forma esporádica sob carga por ETXTBSY (rc 126, "Text file busy"); veja docs/qa/bugs/lote-leitura-hook-1-oraculo-do-bash-instavel-sob-carga.md

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Opção C: com marcador, palavra com `$'…'`/`$"…"` fora de aspas recusa nos dois hooks | corpus AN34 a AN34f, `$"…"` (`test_corpus_nos_dois_hooks`) e propriedade sobre o alfabeto | qualquer escape do alfabeto | passou |
| `reduzida` compara como o bash, `_ansi_c` e `ESCAPES_ANSI` fora | `test_reducao_da_palavra_como_o_bash` | todo par de `\` + caractere | passou |
| Bloco T: teto de 5 mil palavras e 150 mil caracteres, vigia de 3 s, reconhecimento linear | testes de tempo, de linearidade e do vigia (filtros `tempo`, `prazo`, `linear`) | máximo, prazo vencido | passou |
| FD15 aceito com contorno | corpus FD15 | `$'…'` no `parecer` | passou |
| Classe "lançador que divide texto": `env` com a opção de dividir recusa com marcador | ES1 a ES17 ponta a ponta (abaixo) e `test_propriedade_do_lancador_que_divide_texto_com_marcador` | `-S` colado, `--split`, `--spl=`, `\_` | passou |
| Falso positivo FD16 e o contorno | FD16a a FD16d ponta a ponta (abaixo) | `env` sem `-S` libera | passou |
| FD14 e o contorno de cada forma | FD14a a FD14d e uma linha legítima por contorno (abaixo) | palavra entre outras | passou |
| O oráculo do bash prova a classe | `test_divisao_esta_na_classe`, `test_g1_esta_na_classe` | sentinela roda no bash | passou sozinho; instável em paralelo (A1) |

## Cenários e resultado real
Ponta a ponta, nos dois hooks (`python3 hooks/<hook>.py` com a entrada JSON do Claude Code, repositório temporário montado pelo `Fixture` do corpus, `HOME` em `$TMPDIR/qa-engineer-lote-leitura-hook/home`; sonda `sonda-qa-1.py` na mesma pasta): 0 falhas em 49 execuções.
- ES1 a ES17: rc 2 nos dois hooks (34 execuções). `conformidade`: "R-CONFORMIDADE: `env -S` na chamada com ação crítica: o hook não modela o texto que o shell reavalia. Corrigir…"; `parecer`: "R-REVIEW: `env -S` na chamada com gh pr, gh api, merge ou pull: o hook não modela o texto que o shell reavalia".
- FD16a (`env -S 'echo x'; git push origin feature/x`): `conformidade` rc 2, mesma mensagem de R-CONFORMIDADE (falso positivo aceito). FD16b (a mesma forma com `gh pr create`): `parecer` rc 2, mesma mensagem de R-REVIEW. Contornos FD16c (`env X=1 git push origin feature/x`, `conformidade`) e FD16d (`env X=1 gh pr create --draft …`, `parecer`): rc 0, sem mensagem.
- FD14, uma linha legítima por contorno, todas rc 0 e sem mensagem: `git push origin feature/x` (FD14a, a busca noutra chamada); `gh pr create --draft … --title "trocar eval" --body x` (FD14b); `git pull` (FD14c); `grep -rn 'bash -c' hooks/ && git push origin feature/x` (FD14d, texto numa palavra só); `env VAR=x make test && git push origin feature/x` e a variante com `gh pr create --draft` (o `env` sem `-S` no lugar do `docker exec … bash -lc`).
- `test_g1_esta_na_classe` e `test_divisao_esta_na_classe`, 5 execuções seguidas (os dois testes por rodada): as 5 rodadas passaram (10 de 10 execuções de teste), com carga ~9. Em paralelo (4 cópias ao mesmo tempo), 3 de 4 cópias falharam, por ETXTBSY (A1); uma execução exploratória isolada, antes das cinco, também falhou 1 vez e passou na repetição.
- Testes do lote em `CorpusHeredocVoltaUnica` (corpus nos dois hooks, tempo, prazo, linearidade, alfabeto, redução, propriedades): 7 testes, OK em 568 s. Suíte completa não rodada por este QA (o pre-push a roda uma vez, decisão ACELERA-RODADA "A", item 1).

## Riscos
- A1: o par de testes de oráculo pode reprovar o pre-push sem defeito do hook; passa sozinho e na repetição. Médio aberto, exige `aceite_usuario: sim` (aceite do dono) para o parecer aprovado valer.
