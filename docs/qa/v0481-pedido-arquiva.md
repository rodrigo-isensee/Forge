---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 687d97c8209f6e66cd813ce05f44423b6fb0ff87
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0481 E9.3 (registro do pedido que se arquiva sozinho antes do teto, #874, classe C)

## Achados
- A1 (bloqueante) bin/forge-check:8059 · etapa aberta é arquivada: toda linha do Histórico com `=aprovado` arquiva todos os ids que cita. Sonda: `=aprovado (E1.2; E20.1 ainda aberto)` moveu a E20.1 aberta ao arquivo (1141 etapas, esperado 1140). Só vale o id do parecer.
- A2 (bloqueante) bin/forge-check:9812 · o arquivamento acontece antes de montar o brief e não considera o `--cobre`: com `--cobre` numa etapa já `entregue`, o pedido é alterado e o brief falha (rc 2, `--cobre "E3.1" não existe em ## Etapas`). Antes, saía com aviso. Excluir cobre/citadas.
- A3 (recomendado) tests/test_forge_tamanho.py:66 · `forge-testes --vermelho` sai "sem veredito" (H=ok, B=erro) em `Funcoes.test_borda_dos_caracteres`; o autor repete o vermelho e confere o veredito por teste.

## Critério → teste → resultado
| Critério (brief E9.3) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Arquiva sozinho a 80% do teto, brief volta abaixo | `test_arquiva_as_fechadas_e_o_brief_fica_abaixo_do_teto`, `test_brief_curto_nao_arquiva`, `test_borda_dos_caracteres` (7999/8000) | 79,99% e 80% | passou |
| Nenhuma etapa aberta arquivada | `test_etapa_de_varias_linhas_fica_no_pedido`, `test_sem_fechada_nada_muda`; sondas A1 e A2 | etapa aberta citada em linha `=aprovado`; Cobre fechada | FALHOU (A1, A2) |
| Histórico, decisões, selo, entrega conferida e parecer conferido intactos; `pr` e entrega leem o arquivado | `test_arquiva_as_fechadas...` (igualdade do Histórico, `etapas_conferidas`, `entregas_conferidas`, `ultimos_do_historico`), `test_brief_antigo_cita_a_etapa_arquivada...`, `test_so_o_bloco_de_etapas_muda` | Histórico idêntico antes e depois | passou |
| Nada que barra hoje deixa de barrar (forge_tamanho é sensível da catraca) | 24 testes de `test_forge_tamanho`, mutantes M1 a M18 | aviso em 80% e acima do teto | passou |

## Cenários e resultado real
- test_brief_tamanho (13) e test_forge_tamanho (24) rodados local no head: OK. A suíte inteira vale pelo check-run `bateria` do mesmo sha; no momento do parecer, o run Catraca do sha 687d97c8 (45508585509) está `failure` e o CI em andamento. Não consegui ler o log (sandbox só leitura em ~/.cache/gh): o autor confira a causa.
- `forge-mutante --processos 4` nas 3 specs, `rev=687d97c8209f`: M1 a M18 morreram (M5 e M12 por erro do teste sob o mutante com controle verde). `--cobertura --base 8d7914bc...` sem condição sem mutante. A lista não cobre A1 nem A2: falta mutante e teste para a linha 8059 com id aberto na mesma linha.
- Vermelho: `forge-testes --vermelho 8d7914bc... --modulos test_brief_tamanho,test_forge_tamanho` abre com `vermelho: base=8d7914bc93e2 head=687d97c8209f`; prova (API ausente)=5, prova (asserção)=3, não prova (passa na base)=28 (existiam), sem veredito=1 (A3).
- Sondas em arquivo (scratchpad da sessão), com a fixture do próprio autor: A1 e A2 reproduzidas; o pedido foi alterado antes da falha em A2.
- Bugs: A1 = alto (etapa aberta some do `## Etapas`, o brief dela deixa de gerar); A2 = médio (contorno: pedido de continuação). Sem arquivo em docs/qa/bugs, por o brief limitar o commit ao parecer.

Reteste na volta: `forge-check parecer delta docs/qa/v0481-pedido-arquiva.md`, e os dois cenários das sondas viram teste do autor, com mutante.
