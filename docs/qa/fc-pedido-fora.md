---
tipo: qa
contrato: 1
pedido: fc-pedido-fora
branch: melhoria/fc-pedido-fora
commit: 37b531f8dc936905206a2469a1957919024e077b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# Parecer de QA: o forge-check acha o pedido e o brief fora do repositório (FC-PEDIDO-FORA)

Escopo: E1 (pedido e brief em `~/.forge-contrib`, linha `origem:`), E2 (`movimento` e `conferencia registrar` recusam sem `KANBAN.md`) e E3 (testes). Sem UI: E2E de navegador e acessibilidade não se aplicam. O HEAD da worktree (9b81f68) difere de 37b531f só por `docs/reviews` e `docs/security`; o código testado é idêntico.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PQ-1 / E1: `brief` e `entrega` acham pedido e brief em HOME/.forge-contrib e imprimem `origem:` | `test_pedido_e_brief_na_raiz_de_brief_sao_lidos_com_origem`, `test_pedido_absoluto_com_arquivo_relativo`, `test_brief_gerar_acha_o_pedido_fora`, `test_entrega_acha_o_pedido_pelo_id`; roteiro manual | raiz do repositório sem o arquivo | passou |
| E1: mesmo nome nas duas raízes, a do repositório vence | `test_mesmo_nome_nas_duas_raizes_a_raiz_do_repositorio_vence`; roteiro manual (pedido sem `origem:`) | colisão de nome | passou |
| E1: `..` e link simbólico para fora recusados | `test_travessia_e_link_para_fora_sao_recusados` (3 pedidos, 3 briefs); roteiro manual (rc 2) | permissão: fora de `docs/pedidos` e `docs/briefs` | passou |
| E2: sem KANBAN.md, rc 1, mensagem com `--raiz`, sem `docs/kanban/` | `test_movimento_e_conferencia_registrar_recusam_sem_kanban_e_sem_criar_pasta` (2 subtestes); roteiro manual (pasta vazia, `ls -A` vazio) | pasta sem quadro | passou |
| E2: com KANBAN.md grava como antes | `test_com_kanban_nada_muda`; roteiro manual (rc 0, historico.md e conferencias.md criados) | quadro presente | passou |
| PQ-2: suíte e validar-plugin verdes | suíte completa; `scripts/validar-plugin.sh` | n/a | passou |

## Execução
- `python3 -m unittest discover -s tests -q` na worktree: 959 testes, OK (286 s).
- `scripts/validar-plugin.sh`: Validation passed, rc 0.
- Roteiro manual com HOME descartável em `$TMPDIR`, sem rede, repositório com o pedido e o brief só em `<HOME>/.forge-contrib`: `brief` e `entrega` imprimiram `origem:` dos dois; raiz vence confirmado; `../segredo` e link `elo` rc 2 sem `origem:`; `movimento` e `conferencia registrar` sem KANBAN.md rc 1 com a mensagem e a pasta intacta; com KANBAN.md rc 0 e gravação.

## Vermelho antes do verde
Comando: `git archive 37b531f` em `$TMPDIR/red`, com `bin/forge-check` trocado pelo de `50997b7` (develop), e `python3 -m unittest tests.test_pedido_fora`. Resultado: 8 testes, 6 falhas (`test_brief_gerar_acha_o_pedido_fora`, `test_entrega_acha_o_pedido_pelo_id`, `test_pedido_absoluto_com_arquivo_relativo`, `test_pedido_e_brief_na_raiz_de_brief_sao_lidos_com_origem` e os 2 subtestes de recusa sem KANBAN.md). Passam também na develop, por guardarem limites que já valiam: `test_travessia_e_link_para_fora_sao_recusados` (a develop recusa por não achar nada; guarda contra regressão da busca nova), `test_mesmo_nome_nas_duas_raizes...` e `test_com_kanban_nada_muda`. Na branch, os 8 passam.

## Instabilidade
Nenhum teste falhou e passou de novo sem mudança.

## Mutação
A stack do Forge não tem ferramenta de mutação gratuita em `pronto.md`; não rodada.

## Observações (não bloqueiam)
- Cobertas pelo review e pela segurança (cartão FC-SAIDA-SANITIZADA): `--volta`/`--anterior` sem teste, "raiz vence" só no pedido, nome com quebra de linha na linha `origem:`.
- O teste de "raiz vence" prova a precedência pela ausência de `origem:` do pedido; o brief do mesmo nome nas duas raízes não tem teste próprio (a ordem fixa está em `caminho_de_brief`).

## Achados
