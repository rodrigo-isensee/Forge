---
tipo: qa
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a2
commit: 1f91008e938e57fb5abf4f6cca9f486d3e042124
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
revisor: forge:qa-engineer
data: 2026-10-30
---
# QA: impl-forge-check-a (branch a2)

Diff lido: `234dbe0..1f91008` (código em `bin/forge-check` e `tests/test_forge.py`; o resto são pareceres e fragmento).

## Item entregue e M14 (agents/tech-lead.md:19)
E3 do pedido (FC-E4-FALHA-ABERTA): `nomes_do_intervalo(..., estrito=True)` devolve None quando o git falha, e o filtro do E4 em `cmd_entrega` reprova com a linha "escopo: E4 sem o diff da base" em vez de virar escopo vazio com rc 0.
M14: `bin/forge-check` +12 -7 e `tests/test_forge.py` +18, 37 linhas. Um comportamento só; abaixo do teto de 150.

## Achados
- A1 (recomendado) tests/test_forge.py:4536 · cobrir a falha do git com --desde válido (D2 do modelo de ameaças); hoje só as duas etapas de merge sem desde são exercitadas

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E3 / C3 | FalhaDoGitNoE4.test_diff_da_base_que_falha_reprova_e_lista_os_arquivos | git com falha (rc 128) nas duas etapas de merge; arquivos seguem à vista; sem "nada a conferir" | passou |
| regressão do E4 | PrAposMergeDaBase (13 testes com a classe nova) | filtro por conteúdo intacto no caminho sem falha | passou |

## Cenários e resultado real
- `FalhaDoGitNoE4` e `PrAposMergeDaBase` na worktree: 13 testes, OK.
- `forge-testes --vermelho 234dbe0`: rc 0; contagem: não prova (passa na base)=1611; prova (asserção)=2; pulado=26; nenhuma regressão. Uma rodada anterior, sob carga alta da máquina (load ~16), acusou regressão=2; a repetição deu 0 e o teste novo provou. Os pulados são do corpus de lançadores, iguais na base.
- Mutação à mão em cópia descartável (não há spec em tests/mutantes/ para o pedido, e o diff não muda hook, catraca nem guarda de script): (M1) devolver [] na falha em vez de None: 1 falha; (M2) trocar o teste "is None" por False: 2 erros. Os dois morreram.
- Lacuna não bloqueante: sem caso com --desde válido (D2); o código não roda a união com None, então não devolve.

## Parecer
Aprovado: a entrega faz o que o item pede, o teste falha na base e passa no HEAD, e os mutantes das linhas de guarda morrem.
