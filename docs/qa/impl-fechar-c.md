---
tipo: qa
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c4
commit: 2e75595dcf1e7567cfccd6afbe6882708349bc50
parecer: reprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-fechar-c (branch c4)

Etapa E1.4, `R-QA`. Diff lido: `234dbe0..2e75595` (`bin/forge-fechar` 15+3, `tests/test_fechar_corrida_rotulo.py` novo, `tests/test_fechar_espera_catraca.py` 2+2, `docs/fechamento-integrador.md`, fragmento; mais os pareceres).

## Item entregue e M14
Item E4 do pedido (FECHAR-B-REC-REVIEW 3), pela opção B' do modelo de ameaças (SEC-FECHARC-1): a execução da Catraca vista antes do rótulo é só candidata (`run_cand`); uma leitura do rótulo logo depois da leitura dos checks a promove a velha (`run_antes`) se o rótulo segue ausente, ou a descarta se presente. M14 (agents/tech-lead.md:19): um comportamento, 101 linhas de código e teste, abaixo do teto; fora de `hooks/` e `PROTEGIDOS`. Cumpre.

## Achados
- A1 (bloqueante) tests/test_fechar_corrida_rotulo.py:64 · Mutante sobrevivente: descartar a candidata quando a leitura do rótulo falha (C4-2) passa os 20 testes; o AB-C4-4 falha toda leitura do rótulo. Falhar só a posterior, com o rótulo presente depois, e afirmar sem merge (R-QA).
- A2 (bloqueante) tests/test_fechar_corrida_rotulo.py:72 · Mutante sobrevivente: não zerar `run_cand` (bin/forge-fechar:696, C4-3) passa os testes; falta o AB-C4-7 (rótulo retirado na espera, nova em pass vista sem ele, sem merge). O AB-C4-5 já é pego por testes existentes (R-QA).
- A3 (recomendado) bin/forge-fechar:690 · Dois mutantes equivalentes, sem teste necessário: tirar `esperar = 1` da condição (sem a opção, `run_cand` nunca enche) e tirar o teste de `run_cand` vazio (só uma leitura a mais, sem mudar estado).
- A4 (recomendado) tests/mutantes:1 · Pedido que toca bin/ sem spec declarada pelo autor; a lista abaixo é do QA (7 mutantes). Declarar em tests/mutantes/impl-fechar-c-c4.json na volta, com os testes novos.

## Os achados da segurança (A1 e A2) bloqueiam?
Sim, os dois, por prova própria e não por promoção: o QA reproduziu o mutante do A1 (M4) e achou o do A2 (M5) como sobrevivente. São linhas de guarda mudadas no diff (`:691`, `:696`) sem teste que as prenda, e `R-QA` trata mutante sobrevivente como achado do QA até virar teste. O efeito de cada mutante é lido como seguro (nada mescla sem `pass` e com o head preso), então o bloqueio é de teste, não de produto; a correção é só teste, sem mexer em `bin/forge-fechar`.

## Critério → teste → resultado
O pedido não traz `CA-n`; os critérios são C4-1 a C4-8 do modelo de ameaças (SEC-FECHARC-1) e os casos AB-C4-1 a AB-C4-9.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| AB-C4-1 nova reprovando para na hora | `test_corrida_com_a_nova_reprovando_para_na_hora` | rótulo aparece após a leitura dele | passou (vermelho na base) |
| AB-C4-2 nova passando mescla preso ao head | `test_corrida_com_a_nova_passando_mescla_preso_ao_head` | `--match-head-commit` | passou (vermelho na base) |
| AB-C4-3 velha cancelada e nova em pass | `test_catraca_velha_cancelada_espera_a_nova_e_mescla_preso_ao_head` (existente, cenário ajustado) | promoção na leitura posterior | passou (vermelho na base) |
| AB-C4-4 leitura posterior falha | `test_leitura_posterior_do_rotulo_que_falha_...` | falha da API | passa, mas NÃO DISTINGUE o mutante (A1) |
| AB-C4-5 descartada em skipping | `test_a2_velha_cancelada_e_nova_em_skipping_...` e `test_a2_nova_em_skipping_depois_de_pendente_...` (existentes) | só pass libera | passou |
| AB-C4-6 descartada em fail sem velha | `test_descartada_em_fail_sem_velha_nunca_mescla` | `run_antes` vazio | passou (vermelho na base) |
| AB-C4-7 rótulo retirado durante a espera | nenhum | rótulo presente depois ausente | SEM TESTE (A2) |
| AB-C4-8 head que muda | `test_esperar_rotulo_head_que_muda_durante_a_espera_para` (existente) | head preso | passou (regressão) |
| AB-C4-9 / C4-7 os testes da espera, só o cenário muda | `test_fechar_espera_catraca` | rótulo na 3ª leitura | passou |
| C4-5 a leitura nova só lê | `test_a_leitura_nova_so_le` | sem `rerun` nem POST | passou (regressão) |

## Cenários e resultado real
Vermelho antes do verde. `forge-testes --vermelho 234dbe0fb90b005450d7c2eb59e6241ea9779155 --modulos test_fechar_corrida_rotulo` (módulo novo): `prova (asserção)=3; não prova (passa na base)=2` (o de texto e o AB-C4-4), rc=0. Com `--modulos test_fechar_corrida_rotulo,test_fechar_espera_catraca` o veredito é rc=2: dois testes existentes (`test_a2_velha_vermelha_e_nova_em_skipping_...` e `test_catraca_nova_reprovada_para_na_hora_...`) saem `B=erro · sem veredito`. Conferi numa cópia do head com o `bin/forge-fechar` da base: os dois estouram o prazo de 60 s do subprocesso (`TimeoutExpired`, a base espera até 600 s), isto é, falham na base e passam no head; a ferramenta só não os conta. Não é defeito, mas o rc=2 não vale como vermelho; a prova vem dos 9 testes com `B=falha`.

Mutação (`bin/forge-mutante`, spec do QA fora do repositório, 7 mutantes, rev 2e75595dcf1e):
```
M1 · morreu · bin/forge-fechar:345
M2 · morreu · bin/forge-fechar:691
M3 · morreu · bin/forge-fechar:691
M4 · sobreviveu · bin/forge-fechar:691
M5 · sobreviveu · bin/forge-fechar:696
M6 · sobreviveu · bin/forge-fechar:690
M7 · sobreviveu · bin/forge-fechar:690
rc=1
```
M4 é o A1, M5 é o A2; M6 e M7 são equivalentes (A3).

Suíte: módulos `tests/test_fechar*.py` no head, sem bytecode: `Ran 207 tests` / `OK (skipped=1)` (o skip é `test_shellcheck_fechar_passa_limpo`, que pula sem `shellcheck` no PATH; o CI o roda). A bateria completa e o `scripts/validar-plugin.sh` ficam com o pre-push e o CI do envio.
