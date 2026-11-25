---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: d92b3a07d25f6ac354b128937b30684c85dffb16
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 G4 F1 (modo aviso por grupo, só infra; classe C)

## Achados
- A1 (bloqueante) hooks/conformidade.py:1521 · `os.open` do `comandos.jsonl` sem `O_NONBLOCK`: se o arquivo for FIFO sem leitor, a recusa trava até o prazo de 10 s do hook e a chamada passa (R-CONFORMIDADE). Na base a recusa era imediata. Sonda: trava no head. Use `O_NONBLOCK` e exija arquivo regular.
- A2 (recomendado) hooks/conformidade.py:4203 · `GuardaDaProva.barrar` chama `super().barrar` e segue: com grupo em `avisar` o retorno cai nos `if` seguintes e pode registrar duas vezes ou levantar `ForaDaProva`. Latente na F1 (todos em barrar); tratar antes de qualquer grupo ir a `avisar`.

## Critério → teste → resultado
Sem especificação de UX; as obrigações vêm do brief (E7.9).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Nenhum grupo em aviso na entrega (6 IDs em barrar) | `ModoPorGrupo.test_a_politica_entregue_tem_todo_grupo_em_barrar` | mapa entregue com os 6 IDs | passou |
| Só o valor exato `avisar` passa | `test_grupo_fora_do_mapa_mapa_ilegivel_ou_valor_desconhecido_barra_e_registra` | `Avisar`, `aviso`, `True`, mapa string, lista ou None, grupo fora do mapa | passou |
| Recusa igual em todo caminho (mapa ilegível, valor desconhecido, grupo fora) | idem e fixtures `grupo-*` (3) | falha fechada | passou |
| Aviso: stderr e `teria_barrado` | `test_grupo_em_avisar_deixa_passar_imprime_a_forma_certa_e_registra_teria_barrado` | alvo nulo | passou |
| Grupo dado vale sobre o ID | `test_grupo_dado_vale_sobre_o_id_da_regra` | grupo explícito | passou |
| Registro: grupo e alvo, sem criar pasta, sem seguir symlink, erro não muda a decisão | `test_registro_vai_a_pasta_run...`, `test_registro_nao_segue_link...` | symlink, sem `run`, erro de gravação | passou |
| Registro não abre brecha | sonda FIFO (abaixo) | FIFO no lugar do arquivo | falhou (A1) |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.ModoPorGrupo`: 6 testes, OK. Fixtures `conformidade/grupo-*` (3): OK. Amostra de 1 em cada 3 das fixtures de conformidade (901 de 2708): OK. A suíte inteira não foi rodada (passa de 10 min): vale o check-run `bateria` do mesmo sha no CI do PR.
- Mutantes (`bin/forge-mutante --processos 2` nas duas specs): M1 a M10, todos `morreu`, nenhum sobrevivente. `--cobertura --base 6959cec2…`: linhas 1515, 1516, 1520, 1569, 1571 a 1573 cobertas; `hooks/conformidade.json` sai `não coberto` (dado, guardado pelo teste da política entregue). Os `alvo=` passados nas chamadas não têm mutante; as fixtures `grupo-*` os guardam.
- Sonda de brecha (A1): FIFO em `.forge/run/comandos.jsonl`, `Guarda.barrar("R-VERIFY", ...)` no head: `travou` (5 s sem saída). Na base (sem gravação) a recusa é imediata. Em produção o hook tem prazo de 10 s e estouro não é saída 2. O repositório já usa `O_NONBLOCK` em outras leituras (`_maquina.py`, `agentes.py`).
- Medida esperada (recusa falsa, alvo nulo contado): o registro grava `alvo: null` na recusa só pelo texto da linha; coberto pelo teste do aviso e pela fixture `grupo-barrar-texto-registra-alvo-nulo-bloqueia`.
- Vermelho antes do verde: `ModoPorGrupo` não existe na base; os mutantes M1 a M10 morrendo provam que cada teste falha sem a lógica.

## Bugs
- BUG-A1 (alta): o registro bloqueia em FIFO e a recusa vira passagem por estouro de prazo. Passos: criar FIFO em `.forge/run/comandos.jsonl` e provocar qualquer recusa da conformidade. Esperado: saída 2 imediata. Obtido: trava. Responsável: dev do hook.
