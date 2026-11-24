---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: ec38cbc4121cdbf7641309bab3de4bcd30d867e2
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 E9.7 (delta do #874, de 687d97c8 a ec38cbc4)

## Achados
- A1 (recomendado) bin/forge-check:8062 · `etapa_entregue_na_linha` fecha etapa aberta por texto livre: "E1.1 nunca entregue", "E1.1 despachada para corrigir o que foi entregue no #5" e "E1.1 reprovada, volta entregue pelo dev" a arquivam; só "não entregue" é excluído. Cartão: negação ampla e `entregue` só na forma `E<id> entregue`.

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: só a etapa da própria linha fecha | `test_linha_que_cita_outra_etapa_so_fecha_a_atribuida`; sondas (`=aprovado (E1.3 e E1.4)` fecha só a E1.3; `reprovado (E1.1); aprovado (E1.2)` só a E1.2) | id citado e aberto na linha | passou |
| A2 anterior: `--cobre` e Entregar nunca saem | `test_cobre_entregue_fica_no_pedido_e_o_brief_sai`; sonda `--cobre` numa etapa aprovada: segue no pedido, rc 0 | cobre já entregue | passou |
| Junta delegações, papel errado e contradição iguais depois do arquivo | `test_corte_barra_igual_antes_e_depois_do_arquivo`, `test_corte_de_pedido_so_com_arquivadas_ainda_barra` | arquivada sem papel (None) | passou |
| Arquivo e pasta que não são regulares não recebem nada | 3 testes (pasta, arquivo, fifo) | atalho simbólico e fifo | passou |
| A3 anterior: vermelho por teste | `test_borda_dos_caracteres` | 8000 de 10000 | passou (prova por asserção) |

## Cenários e resultado real
- Local no head: test_brief_tamanho (20) e test_forge_tamanho (24) OK. Sonda em arquivo (scratchpad): 3 de 5 negações livres fecham etapa aberta (A1); as demais sondas passaram.
- `forge-mutante --processos 4` nas 5 specs, `rev=ec38cbc4121c`: M1 a M39 morreram (M5 e M37 por erro com controle verde, aceitos). `--cobertura --base 8d7914bc...`: toda linha `coberta`, nenhuma sem mutante.
- Vermelho: `forge-testes --vermelho 8d7914bc... --modulos test_brief_tamanho,test_forge_tamanho`: contagem não prova (passa na base)=28; prova (API ausente)=10; prova (asserção)=6; sem veredito=0 (A3 resolvido).
- `forge-check parecer delta`: só `tests/test_forge_tamanho.py` (1 linha) no domínio do QA.
- CI: o run Catraca do sha ec38cbc4 (45512304394) está `failure`; não leio o log no sandbox. A suíte vale pelo check-run `bateria` do mesmo sha: o tech-lead confere a causa antes do merge. O remoto já andou para 99ae83f9.
