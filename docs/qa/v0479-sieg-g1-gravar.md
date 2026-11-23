---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: 9f833cd6d8290f0d0aeeb2306ef1f16fa56f9b67
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
