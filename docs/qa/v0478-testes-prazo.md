---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: c460102d3d64d4f87b4367a4e5a32d365c43e759
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 testes de prazo (E12.6)

Escopo: DEFEITO-TESTES-DE-PRAZO-SOB-CARGA. O pedido `docs/pedidos/v0478.md` não está neste clone; as obrigações vêm do fragmento `changelog.d/v0478-testes-prazo.md` e do diff contra a base `4182a6b9`. O hook não muda (o diff só toca `tests/`, `tests/mutantes/` e a função `pids_do_proc`, extraída em `bin/forge_sempre_atual.py` sem mudar a lógica).

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O1: o oráculo do forge-sempre-atual vê só os descendentes do teste | `test_sempre_atual.ProcessoDeOutraParteDaSuite` (3 testes) | órfão, init, stat ilegível, ciclo de pais | passou |
| O2: só o `forge-sempre-atual` troca a lista; outro programa vê tudo | `test_lancador_troca_a_lista_de_pids_so_do_forge_sempre_atual` | programa diferente | passou |
| O3: a varredura lê os pids de `pids_do_proc` | `test_processos_de_interesse_le_os_pids_de_pids_do_proc` | com e sem a troca | passou |
| O4: recusa do vigia de 8 s só vale como carga com CPU+sono ≤ prazo−1 s | `test_carga_explica_a_recusa_so_pelo_vigia_do_prazo_longo_com_cpu_folgada` | fronteira exata da folga, vigia de 3 s, sem medida | passou |
| O5: o merge que libera roda em série e a recusa de regra de verdade continua reprovando | `test_liberar_ou_provar_a_carga_aceita_so_a_recusa_explicada_pela_carga`, `test_prazo_do_merge` | CPU acima da folga; recusa por R-REVIEW | passou |

## Cenários e resultado real
- Local (`python3 -I -m unittest discover -s tests -p test_sempre_atual.py -k ProcessoDeOutraParteDaSuite`): 3 testes, OK.
- Local (`test_hooks.py -k test_carga_explica -k test_liberar_ou_provar -k test_prazo_do_merge`): 4 testes, OK, 35 s.
- Módulo `test_sempre_atual` inteiro: falha no sandbox também na base (leitura do /proc); a prova dele é o check-run `bateria` do CI no mesmo sha. Não rodei suíte local (E12.6).
- Vermelho (`R-QA`): `forge-testes --vermelho` do módulo inteiro não dá veredito aqui (estoura o prazo, rc 124, pelo /proc do sandbox). Feito à mão, em cópia em `$TMPDIR`: testes do HEAD com `bin/forge_sempre_atual.py` e `tests/sem_claude_ancestral.py` da base: `FAILED (failures=1, errors=2)` (`descende_de` e `pids_do_proc` não existem; o lançador entrega a lista inteira ao forge-sempre-atual).
- Os dois testes novos de `test_hooks.py` testam auxiliares que moram no próprio arquivo de teste; não há base do auxiliar para ficar vermelho (recomendação A1).

## Mutação
`bin/forge-mutante tests/mutantes/v0478-testes-prazo.json`:
```
forge-mutante: pedido=v0478-testes-prazo rev=bf3ce6af7420 spec=e8358fa7cc57dcdb8281386684f2caeee3ccd9229a96a790c18c8e64ff41f7a4
M1 · morreu · tests/sem_claude_ancestral.py:33
M2 · morreu · tests/sem_claude_ancestral.py:34
M3 · morreu · tests/sem_claude_ancestral.py:52
M4 · morreu · tests/sem_claude_ancestral.py:56
```
Os quatro mutantes morreram, um por linha de guarda do lançador. A spec antiga S14 (`v047-sempre-atual-12.json`) foi reapontada para `pids_do_proc` (mesma guarda `isdigit`, em outra linha); não a rodei aqui (o teste que a mata vive no módulo que falha no /proc do sandbox): o CI cobre.

## Achados
- A1 (recomendado) tests/test_hooks.py:114 · `carga_explica_a_recusa` decide por condições (vigia, relógio, folga de CPU) sem mutante declarado em `tests/mutantes/v0478-testes-prazo.json`; os subtestes de fronteira cobrem, mas fica "declarado, não provado". É código de teste, não guarda: não bloqueia.

## Revalidação (delta bf3ce6af..318721db)
`forge-check parecer delta` lista: ci.yml (passo que só conta `PRAZO-CARGA` no resumo), fragmento do changelog, `tests/prova_de_carga.py` (novo), `tests/test_hooks.py` e as duas specs de mutantes. A1 anterior atendido: o critério saiu de `test_hooks.py` para `prova_de_carga.py` e ganhou M5 a M10, um por guarda.
- Mutantes (`bin/forge-mutante tests/mutantes/v0478-testes-prazo.json tests/mutantes/v0478-testes-prazo-2.json`, rev=318721dbbb87): M1 a M10 morreram (M1 a M4 no lançador; M5 a M8 em `prova_de_carga.py:64,66,68,70`; M9 `:58` e M10 `:51`, estes dois mortos por erro do teste declarado sob o mutante, que passa sem ele). Nenhum sobrevivente, nenhum equivalente.
- Local (`test_hooks.py -k test_prazo_do_merge -k test_carga_explica -k test_referencia_da_cpu -k test_liberar_ou_provar`): 6 testes, OK, 43 s, inclusive a sonda S1 (`test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`) e o critério com disputa provada.
- A suíte inteira: check-run `bateria` do CI no mesmo sha; não rodei suíte local.
- Achados: nenhum novo. Bugs: 0.

## Revalidação (delta 318721db..c460102d)
`forge-check parecer delta` lista só `tests/mutantes/v047-ci-rapido-3.json`: M33 e M34 alinhados ao passo novo de `PRAZO-CARGA` no `ci.yml` (a develop trazida pelo forge-fechar fica fora do domínio). Comando `bin/forge-mutante tests/mutantes/v047-ci-rapido-3.json --base 318721dbbb87ab4db3db719d6f0207e8def10423`, saída 0:
```
M25 a M32 · morreu
M33 · morreu · .github/workflows/ci.yml:205
M34 · morreu · .github/workflows/ci.yml:393
```
M33 e M34 morrem (`tests.test_suite_partes.FiacaoDoCI`); nenhum sobrevivente. A suíte inteira: check-run `bateria` do CI no mesmo sha; não rodei suíte local. Achados: nenhum novo. Bugs: 0.
