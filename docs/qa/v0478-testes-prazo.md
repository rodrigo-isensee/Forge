---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-testes-prazo
commit: bf3ce6af7420bc86931931866ef462163b5cec3c
parecer: aprovado
escopo: completo
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
