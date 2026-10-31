---
tipo: qa
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c4
commit: 6336b6b442e5760a0dfa8532ac30beb833ea3d4a
parecer: aprovado
revisor: forge:qa-engineer
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-fechar-c (branch c4)

Etapa E1.4, `R-QA`. Diff lido: `234dbe0..6336b6b` (`bin/forge-fechar` 15+3, `tests/test_fechar_corrida_rotulo.py` novo, `tests/test_fechar_espera_catraca.py` 2+2, `docs/fechamento-integrador.md`, fragmento; mais os pareceres).

## Item entregue e M14
Item E4 do pedido (FECHAR-B-REC-REVIEW 3), pela opção B' do modelo de ameaças (SEC-FECHARC-1): a execução da Catraca vista antes do rótulo é só candidata (`run_cand`); uma leitura do rótulo logo depois da leitura dos checks a promove a velha (`run_antes`) se o rótulo segue ausente, ou a descarta se presente. M14 (agents/tech-lead.md:19): um comportamento, 101 linhas de código e teste, abaixo do teto; fora de `hooks/` e `PROTEGIDOS`. Cumpre.

## Achados
- A1 (recomendado) tests/test_fechar_corrida_rotulo.py:64 · Resolvido: o teste novo falha só a leitura posterior do rótulo, com o rótulo presente depois, e afirma sem merge; o mutante C4-2 morre.
- A2 (recomendado) tests/test_fechar_corrida_rotulo.py:72 · Resolvido: o teste novo do rótulo retirado na espera (AB-C4-7) prende o `run_cand` zerado; o mutante C4-3 morre.
- A3 (recomendado) bin/forge-fechar:690 · Dois mutantes equivalentes (C4-6, C4-7), declarados com justificativa na spec do autor e aceitos pelo QA: sem a opção `run_cand` nunca enche; sem candidata a leitura a mais não muda estado.
- A4 (recomendado) tests/mutantes/impl-fechar-c-c4.json:1 · Resolvido: spec declarada pelo autor (7 mutantes: 5 morrem, 2 equivalentes).

## Revalidação (volta por delta)
`forge-check delta --parecer docs/qa/impl-fechar-c.md` listou `2e75595..6336b6b`: `tests/mutantes/impl-fechar-c-c4.json` (1-113, lido inteiro) e `tests/test_fechar_corrida_rotulo.py` (34-45 o `rotulo_lido`, 84-103 os dois testes novos, lidos). Já lido e sem mudança: `bin/forge-fechar` e o resto do diff (`bin/` não mudou na volta).
Conferência da lista contra o diff de `bin/forge-fechar`: uma linha de guarda mudada por mutante (candidata, leitura posterior, promoção, descarte, zerar a lista, condição da leitura). `forge-mutante --cobertura` só diz `não coberto: bin/forge-fechar` (shell); a conferência foi à mão.

## Critério → teste → resultado
O pedido não traz `CA-n`; os critérios são C4-1 a C4-8 do modelo de ameaças (SEC-FECHARC-1) e os casos AB-C4-1 a AB-C4-9.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| AB-C4-1 nova reprovando para na hora | `test_corrida_com_a_nova_reprovando_para_na_hora` | rótulo aparece após a leitura dele | passou (vermelho na base) |
| AB-C4-2 nova passando mescla preso ao head | `test_corrida_com_a_nova_passando_mescla_preso_ao_head` | `--match-head-commit` | passou (vermelho na base) |
| AB-C4-3 velha cancelada e nova em pass | `test_catraca_velha_cancelada_espera_a_nova_e_mescla_preso_ao_head` (existente, cenário ajustado) | promoção na leitura posterior | passou (vermelho na base) |
| AB-C4-4 leitura posterior falha | `test_so_a_leitura_posterior_falha_e_o_rotulo_presente_depois_segue_velha_e_nunca_mescla` (e o anterior, que falha toda leitura) | falha da API | passou (mata o mutante C4-2) |
| AB-C4-5 descartada em skipping | `test_a2_velha_cancelada_e_nova_em_skipping_...` e `test_a2_nova_em_skipping_depois_de_pendente_...` (existentes) | só pass libera | passou |
| AB-C4-6 descartada em fail sem velha | `test_descartada_em_fail_sem_velha_nunca_mescla` | `run_antes` vazio | passou (vermelho na base) |
| AB-C4-7 rótulo retirado durante a espera | `test_rotulo_retirado_na_espera_nao_deixa_candidata_descartada_virar_velha` | rótulo presente depois ausente | passou (mata o mutante C4-3) |
| AB-C4-8 head que muda | `test_esperar_rotulo_head_que_muda_durante_a_espera_para` (existente) | head preso | passou (regressão) |
| AB-C4-9 / C4-7 os testes da espera, só o cenário muda | `test_fechar_espera_catraca` | rótulo na 3ª leitura | passou |
| C4-5 a leitura nova só lê | `test_a_leitura_nova_so_le` | sem `rerun` nem POST | passou (regressão) |

## Cenários e resultado real
Vermelho dos testes antigos: parecer anterior (`forge-testes --vermelho 234dbe0...`, 3 provam no módulo novo mais os 6 `B=falha`, rc=0; com o módulo de espera junto, rc=2 pelo prazo da base, explicado lá). Os dois testes novos da volta cobrem código que a branch já tinha (a volta só mexeu em `tests/`), então o vermelho deles é o mutante: `forge-testes --vermelho d88f136~1` sai `nenhum teste prova a mudança` (esperado), e a prova são os mutantes C4-2 e C4-3, que sobreviviam e agora morrem.
Mutação, `bin/forge-mutante tests/mutantes/impl-fechar-c-c4.json`:
```
forge-mutante: pedido=impl-fechar-c-c4 rev=6336b6b442e5 spec=9a4654fb4f1b258440e301b030ed0bf7d2fffa80c2f6d00f2ee2d7178de63c98
C4-1 · morreu · bin/forge-fechar:345
C4-2 · morreu · bin/forge-fechar:691
C4-3 · morreu · bin/forge-fechar:696
C4-4 · morreu · bin/forge-fechar:691
C4-5 · morreu · bin/forge-fechar:691
C4-6 · equivalente · bin/forge-fechar:690
C4-7 · equivalente · bin/forge-fechar:690
rc=0
```
Suíte: `tests/test_fechar*.py` no head: `Ran 209 tests` / `OK (skipped=1)` (o skip é o shellcheck, que o CI roda). A bateria completa e o `scripts/validar-plugin.sh` ficam com o pre-push e o CI do envio.
