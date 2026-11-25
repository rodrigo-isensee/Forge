---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g4-f1-aviso
commit: 3682aebaa39bbb2607e45db5d699cc5e7293a65b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 G4 F1 (modo aviso por grupo, só infra; classe C), delta d92b3a07..3682aeba

## Achados
- A2 (recomendado) hooks/conformidade.py:4203 · `GuardaDaProva.barrar` chama `super().barrar` e segue: com grupo em `avisar` o retorno cai nos `if` seguintes e pode registrar duas vezes ou levantar `ForaDaProva`. Latente na F1 (todos em barrar); tratar antes de qualquer grupo ir a `avisar`. Segue aberto, fora deste delta.

## Delta lido
`git diff d92b3a07..3682aeba` (código e testes): `registrar_recusa` acha a pasta `run` só pelo disco (sem `git`), abre com `O_NONBLOCK` e só grava (`os.write`) se `S_ISREG`; `Guarda.barrar` decide o texto da recusa antes de gravar e engole `PrazoVencido` do registro; classe nova `RecusaComFifoNoRegistro` e 4 testes novos em `ModoPorGrupo`; mutantes M11 a M16 novos.

## Critério → teste → resultado
Sem especificação de UX; as obrigações vêm do brief (E7.13) e dos achados A1/A2 anteriores.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1: FIFO no registro não trava nem grava | `ModoPorGrupo.test_registro_nao_espera_fifo_nem_grava_nele` | FIFO sem e com leitor | passou |
| A1: recusa pelo hook de verdade, sessão Forge e projeto, push na main, `--force`, `--no-verify` | `RecusaComFifoNoRegistro.test_recusa_com_a_regra_dela_e_sem_prazo_vencido` (6 subtestes) | FIFO no lugar do `comandos.jsonl`, regra certa, sem "não decidiu" | passou |
| Prazo vencido no registro não muda a recusa | `test_prazo_vencido_no_registro_nao_troca_a_recusa` | `PrazoVencido` (BaseException) no registro | passou |
| Pasta do registro pelo disco, sem git, worktree grava na principal | `test_registro_acha_a_pasta_pelo_disco_sem_git` | fora de git; worktree | passou |
| Recusa decidida antes de gravar (texto iniciante) | `test_iniciante_recebe_o_texto_simples` | perfil iniciante | passou |
| Obrigações da volta anterior (aviso, grupo, mapa ilegível, symlink, sem `run`) | demais testes de `ModoPorGrupo` | n/a (já aprovados no head anterior) | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.ModoPorGrupo tests.test_hooks.RecusaComFifoNoRegistro`: 11 testes, OK (1,6 s). Só as classes do item; `tests.test_hooks` inteiro e a suíte não foram rodados: vale o check-run `bateria` do mesmo sha no CI do PR.
- Sonda própria (arquivo `sonda_fifo.py`, hook de produção por subprocesso, FIFO sem leitor em `.forge/run/comandos.jsonl`, 4 comandos: push `:main`, `--force`, `-f`, `commit --no-verify`) nas duas sessões. Head 3682aeba: 8 de 8 com rc 2, regra certa (R-MAIN/R-VERIFY), 0,2 a 0,4 s, nenhum travou.
- Vermelho antes do verde (mesma sonda no hook de d92b3a07, extraído com `git archive`): sessão Forge, push `:main`, `--force` e `-f` saem rc 0 (a recusa vira passagem); sessão projeto, 3 dos 4 saem "R-CONFORMIDADE: erro interno do hook" no lugar da regra; só `--no-verify` mantém a regra. É a falha que os testes novos guardam. `forge-testes --vermelho` com `--modulos tests.test_hooks` foi negado pelo classificador do ambiente (roda o módulo inteiro, fora do que o brief permitiu); a prova de vermelho vai pela sonda na base e pelos mutantes M5 a M16 mortos.
- Mutantes: `bin/forge-mutante --processos 2 tests/mutantes/v0481-g4-f1-aviso.json tests/mutantes/v0481-g4-f1-aviso-2.json`: M1 a M16, todos `morreu`, nenhum sobrevivente (M1, M3, M4, M8, M11 e M13 por erro do teste declarado sob o mutante, com controle verde). Delta: `bin/forge-mutante --base d92b3a07d25f6ac354b128937b30684c85dffb16 <as duas specs>`: M5 a M16 mortos. `--cobertura --base 6959cec2…`: linhas 1518, 1520, 1521, 1525, 1529, 1578, 1580, 1581 declaradas; `hooks/conformidade.json` `não coberto` (dado, guardado pelo teste da política entregue).
- A1 anterior: resolvido (FIFO sem travar). Nenhum bug aberto.

## Bugs
Nenhum aberto. BUG-A1 (alta) da volta anterior está corrigido no head 3682aeba.
