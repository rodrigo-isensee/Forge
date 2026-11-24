---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: d4960f8e7e8e428d5eea5726f380740be9f51081
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0479-sieg-g1-gravar (E90.13)

Revalidação por delta no head 9f833cd6 (volta E90.10), desde 2d5efbe8; o parecer aprovado de d7c1a53b segue valendo para o restante. Escopo do delta: A3 (`ler` recusa fala no futuro), A4 (casa do banco de senhas), A5 (emoji e outra escrita contam fora do vocabulário), A2 do review (ponto final após o alvo), A6 (`fim deste pedido` só com o pedido aberto). Sem suíte local; a suíte inteira é o check-run `bateria` do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A3: fala no futuro nunca autoriza no `ler` | `VoltaDosPortoes.test_fala_no_futuro_escrita_na_pasta_nao_fica_ativa_no_ler` | 1 min antes da fala adultera; no instante vale | passou |
| A4: HOME e sessão do chamador não escolhem a transcrição | `TranscricaoDaSessaoEmCurso.test_home_e_sessao_do_chamador_nao_escolhem_a_transcricao` | HOME apontado para a pasta forjada recusa; casa do banco de senhas nela grava | passou |
| A5: emoji e outra escrita nascem pendentes | `VoltaDosPortoes.test_emoji_ou_negacao_em_outra_escrita_nasce_pendente` | emoji, cirílico | passou |
| A2 review: ponto final após PR ou versão | `VoltaDosPortoes.test_ponto_final_logo_depois_do_alvo_nao_deixa_pendente` | `pr 5.`, `0.47.3.` ativa; `pr 5.1` pendente | passou |
| A6: `fim deste pedido` só com o pedido aberto | `test_fim_deste_pedido_so_com_o_pedido_aberto`, `test_forge_check_confere_o_pedido_no_registro` | inexistente, sem como conferir, `F-<pedido>` gravado, aberto | passou |

## Provas
- Testes: `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao` no head: 49 testes, OK. Sem `skip` nem `expectedFailure` no delta.
- Vermelho: `python3 bin/forge-testes --vermelho 2d5efbe8 --modulos test_autorizacao_gravar` fecha `contagem: prova (API ausente)=32`; os testes novos da `VoltaDosPortoes` e o do A4 saem `H=ok · B=erro · prova`.
- Mutantes: `bin/forge-mutante --base 2d5efbe8 tests/mutantes/v0479-sieg-g1-gravar-7.json -8.json -9.json` (rc 0, `base=2d5efbe8f8ca mb=2d5efbe8f8ca rev=9f833cd6d829`): M47 a M63 todos `morreu`, com M55 a M63 (os novos); `v047-sieg-g1-autorizacao-6.json` com `--ids M44` (spec editada): `morreu`. Nenhum sobrevivente.
- `forge-mutante --cobertura --base 2d5efbe8`: toda condição mudada `coberta` (declarado, e provado pela rodada acima); sem `não coberta`.
- Lido no diff: a classe de caracteres do A5 manda também aspas curvas e travessão para pendente; falha para o lado seguro, sem bloqueio.
- `forge-check parecer delta`: intervalo d7c1a53b..9f833cd6 lido; o domínio mudou só em `bin/`, specs de mutante e `tests/test_autorizacao_gravar.py`.

## Revalidação por delta (E90.17): head 3e653044, desde 9f833cd6 (volta E90.14, decisão 3a)
O delta desfaz só o ajuste de pontuação: o regex marcado (`bin/forge_autorizacao.py:319`) volta a `(?![\w.])`, o ponto final logo depois do alvo deixa a concessão pendente, como na base. Tocados: o regex, ADR 0018, fragmento do changelog, mutantes M58/M59 (de/para invertidos) e o teste renomeado.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E90.14: `pr 5.` e `0.47.3.` pendentes | `VoltaDosPortoes.test_ponto_final_logo_depois_do_alvo_deixa_pendente` | ponto final após PR e versão pendente; `pr 5.1` segue pendente com alvo `pr:5` | passou |

- Testes: `python3 -m unittest tests.test_autorizacao_gravar` (TMPDIR próprio): 32 testes, OK. Sem `skip` nem `expectedFailure`.
- Vermelho: `forge-testes --vermelho 9f833cd6 --modulos test_autorizacao_gravar` fecha `contagem: não prova (passa na base)=31; prova (asserção)=1`; o teste mudado sai `H=ok · B=falha · prova (asserção)`.
- Mutantes: `bin/forge-mutante --base 9f833cd6 tests/mutantes/v0479-sieg-g1-gravar-8.json` (`base=9f833cd6d829 mb=9f833cd6d829 rev=3e653044fb25`): M55 a M62 todos `morreu`, M58 e M59 incluídos. Nenhum sobrevivente.
- Lido no diff: a linha de guarda mudada (319) tem M58 e M59; ADR e changelog coerentes com o comportamento.

## Revalidação por delta (E90.22): head d4960f8e, desde 3e653044 (merge da develop, E90.19)
O delta é só o merge da `origin/develop` (fc488261). `bin/forge_autorizacao.py` e `tests/test_autorizacao_gravar.py` não mudaram desde 3e653044 (`git diff 3e653044 HEAD --stat` sem eles); a decisão 3a e a prova de mutação de E90.17 seguem valendo. `forge-check parecer delta` lista no domínio do QA o que veio da base: `bin/forge-check`, `bin/forge-testes`, `docs/indice-forge.md`, `tests/pesos-d4.json`; `tests/test_testes_tocados.py` veio da base com o mapa atualizado (`test_placar_prometido`, `test_ambiente_recriacao`, `test_prepush_lote_pp1`).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E90.14 (decisão 3a) segue de pé após o merge | `VoltaDosPortoes.test_ponto_final_logo_depois_do_alvo_deixa_pendente` | `pr 5.` e `0.47.3.` pendentes; `pr 5.1` pendente | passou |
| Mapa do `forge-testes` com o merge | `tests.test_testes_tocados` | mapa de `bin/forge-mutante`, `bin/forge-placar`, renomeados | passou |

- Testes: `python3 -m unittest tests.test_testes_tocados tests.test_autorizacao_gravar` (da raiz, sem -I): `Ran 228 tests`, `OK (skipped=1)`. O skip é do sandbox (`/proc` de outro namespace de pid), em teste da base; roda no CI.
- Sem teste novo nem mudado por esta branch no delta; vermelho e mutantes não se aplicam (nenhuma linha de guarda mudada). A suíte inteira é o check-run `bateria` do PR.
