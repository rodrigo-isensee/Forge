---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-forge-sempre-atual
commit: 008d66c31e331e3bd150cbb487bec5cdcf521c49
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047 FORGE-SEMPRE-ATUAL (E1.53, ADR 0017)

Head 2bcad385, base 45615e20. Sem PR: não há check-run `bateria` para citar; a suíte inteira fica com o CI do PR. Rodei só os módulos tocados, com `TMPDIR` próprio, em primeiro plano.

## Achados
- A1 (recomendado) tests/test_oraculo_sempre_atual.py:458 · no sandbox, `/proc` é de outro namespace: 9 testes de ocupação (S2/S6) não se provam aqui; confira no CI do PR que o oráculo passa inteiro (59 testes).

## Critério → teste → resultado
O critério de parada é o do desenho (RD1 a RD11, D30b, seções 2 a 5 e 8) e da ADR 0017, no oráculo `tests/test_oraculo_sempre_atual.py` (59 testes).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Oráculo RD/D30b/SEG/S (atualiza, volta, registro, estado, trampolins, aviso, nunca reabre) | `test_oraculo_sempre_atual` | prazo, `ref` igual ao alvo, versão maior que a quebrada, permissão | 50 de 59 passam com a guarda de `/proc` neutralizada em cópia; 9 só caem na pré-condição `vivo()` (ambiente) |
| Ocupação S2/S6 (claude vivo, trava, suíte, integração, dúvida) | classe `Ocupacao` e `NuncaReabre.test_nao_mata...` | leitura em dúvida adia | não provado no sandbox; falta o CI (A1) |
| Núcleo, entradas, `forge atualizar`/`voltar-versao`, doutor, forge-check | `test_sempre_atual` (68), `test_atualizar` (109, 3 pulos de ambiente), `test_doutor` (105), `test_testes_tocados` (162, 1 pulo), `test_forge` (639) | n/a | passou |
| Mutantes declarados, 1 por guarda mudada | 8 specs, 77 mutantes | n/a | todos morreram, nenhum sobrevivente, nenhum equivalente |

## Cenários e resultado real
Ambiente x defeito (o autor viu o mesmo):
- No sandbox `/proc/self` (12) difere de `os.getpid()` (5): outro namespace de pid. `proc_coerente()` devolve falso por desenho (ADR 0017 item 5: leitura em dúvida conta como ocupado), então o escopo sai `adiado:duvida:proc` e 40 testes do oráculo caem (39 falhas, 1 erro: `FileNotFoundError` em `add.pid`, consequência do add que não rodou). Todos os 40 são o mesmo sintoma (`adiado:duvida:proc`, versão que não subiu). `unshare --pid --mount-proc` é negado, então não há como reproduzir um `/proc` coerente aqui: ambiente, não defeito.
- Prova do descarte: cópia de `git archive HEAD` em `$TMPDIR` com `return True` na primeira linha de `proc_coerente` (nunca na árvore do autor): 50 passam, 9 falham, todas em `vivo()` (`'' != 'claude'`: o `comm` do filho gerado não se lê no namespace alheio). Nenhuma falha de lógica.
- Prazo sob carga: não vi falha de prazo; o oráculo levou 58 a 79 s.
- Oráculo editado depois do commit 500e04c7: só 2bcad385 (duas linhas, `remoto_sem_manutencao` no repositório bare); não afrouxa nada. O autor é o mesmo do commit do oráculo; o hook `conformidade` barra a escrita de agente, e o commit é de ambiente. Registro para o review.
- Vermelho antes do verde (`forge-testes --vermelho`) não rodei: o brief limita aos módulos tocados e às specs.

## Provas
- Módulos: oráculo 59 testes, 19 ok no sandbox sem neutralizar e 40 por `/proc`; `test_sempre_atual` Ran 68 OK; `test_atualizar` Ran 109 OK (skipped=3); `test_doutor` Ran 105 OK; `test_testes_tocados` Ran 162 OK (skipped=1); `test_forge` Ran 639 OK.
- Mutantes (rc 0 em todas): v047-sempre-atual-1 16 mortos, -2 10, -3 15, -4 8, -5 8, -6 2, `fixacao-do-dono` 7, `v047-atualizar-hook-local` 11. Mortos com `(erro) o teste declarado deu erro sob o mutante e passa sem ele`: M25 (spec 2, `forge_sempre_atual.py:303`), A12 a A14 (spec 5, `forge-check:9365,9376,9382`), M4 e M6 da fixação (`forge_sempre_atual.py:929,916`); morrem por erro do teste, não por asserção: ver A1 só se o CI divergir.
- `python3 -m unittest tests.test_forge_mutante.ConferirTodas`: Ran 4 tests, OK.

## Revalidação por delta (E1.60, head b89aa7ed, base do delta 2bcad385)
`forge-check parecer delta` listou o domínio: forge-testes, forge-upgrade, forge_sempre_atual.py, conformidade.py, 21 fixtures `tagv-*`, specs v0432-integracao-2/3 e v047-sempre-atual-7 a 10, test_hooks, oráculo e test_sempre_atual. Sem PR: sem check-run `bateria`; a suíte inteira fica com o CI do PR. Com `TMPDIR` próprio, em primeiro plano.
- Mutantes novos, uma chamada por spec, todas rc 0 e todos mortos: spec 7 (V1 a V8), spec 8 (V9, V10, U1 a U3), spec 9 (H1 a H7), spec 10 (V11, V12, H8 a H13); 26 mutantes, nenhum sobrevivente, nenhum erro de carga.
- `tests.test_forge_mutante.ConferirTodas tests.test_sempre_atual tests.test_ambiente_git` (sem -I): Ran 105 OK.
- Oráculo em cópia de `git archive HEAD` com `proc_coerente` neutralizado: Ran 59, 50 passam, 9 falham (classe `Ocupacao` e `NuncaReabre`, só `vivo()` no `comm` de outro namespace), igual à rodada anterior; os 9 só no CI. O oráculo não mudou desde 2bcad385 além do ajuste da volta E1.55 (conferido pelo delta, sem afrouxar).
- Fixtures `tagv-*` (21, em `tests/hooks/conformidade/`): `tests.test_hooks.Hooks.test_fixtures` (a suíte de fixtures inteira, 350 s): 1 falha, `pesado/mesma-sessao-libera`, `PrazoEstourado` de 120 s numa fixture de trava de outro hook, que não toca o delta; nenhuma fixture `tagv` ou `conformidade` caiu. Ambiente (sessão e `/proc` do sandbox); confira no CI do PR.
- A1 segue valendo: o CI do PR precisa passar o oráculo inteiro (59) e `test_hooks`.

## Revalidação por delta (E3.91, head 008d66c3, base do delta b89aa7ed)
`forge-check parecer delta` listou o domínio: forge-check (H1, tamanho do PR), forge-testes, conformidade.py, docs/adr/README.md, docs/hooks-fixtures.md, specs `v047-sempre-atual-11` a `-35` e os testes test_atualizar, test_forge, test_hooks, test_sempre_atual, test_testes_tocados. Aviso do delta: o merge de c7e03a9 não está na origin/develop local; o que ele trouxe contou inteiro. Sem PR, sem check-run `bateria`; a suíte inteira fica com o CI do PR.
- Specs declaram 200 mutantes novos (287 no conjunto `v047-sempre-atual-*`). Amostra rodada com `--processos 4`: specs 11, 12, 13 (24 mutantes, S1 a S24) e 20, 27, 31, 35 (32 mutantes), todos `morreu`, rc 0, `rev=008d66c31e33`, nenhum sobrevivente; 3 morrem por erro do teste declarado (S3, S20 e semelhante), mesma classe já registrada.
- Módulos tocados (`python3 -I -m unittest discover`, TMPDIR próprio): test_sempre_atual Ran 139 OK; test_atualizar Ran 111 OK (skipped=3, ambiente); test_testes_tocados Ran 162 OK (skipped=1). test_forge e test_hooks ficam com o CI (suítes longas, A1 segue valendo).
- Sem achado novo.
