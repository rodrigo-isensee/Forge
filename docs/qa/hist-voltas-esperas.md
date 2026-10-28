---
tipo: qa
contrato: 1
pedido: hist-voltas-esperas
branch: melhoria/hist-voltas-esperas
commit: 27f86b680d95cf26083be9515bfdef20c47048ef
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: hist-voltas-esperas

Base a83de9e24908195fef0c92ebfcb1603518b58390, head 27f86b680d95. Pedido de controle (`bin/forge-check`): vale a prova de mutação declarada, conferida contra o diff.

## Achados
- A1 (bloqueante) bin/forge-check:3407 · linha de guarda mudada sem mutante: `(?<![A-Za-z0-9._-])` em `cita_o_pedido` (id colado depois de letra, dígito, ponto ou hífen). Mutante Q1 (remover o lookbehind) sobrevive à `tests.test_medidas_m14b.Esperas`; falta teste com o id colado atrás (ex.: `xped-d`) e o mutante H8 na spec.
- A2 (recomendado) bin/forge-check:5184 · `--kanban` sem `--pedido` é aceito e ignorado em silêncio (o uso diz `--pedido ID [--kanban ARQUIVO]`); o `--help` já avisa "com --pedido", mas não há erro.
- A3 (recomendado) agents/jarvis.md:46 · E2 (registrar volta e espera como movimento) é só texto; nenhum teste o guarda além do `test_o_movimento_do_jarvis_alimenta_as_esperas`, que não lê o jarvis.md.

## Critério → teste → resultado
Escopo E1 a E3 do pedido (o pedido não traz CA-n em EARS; cada item de escopo é a obrigação).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 casar pelo motivo do movimento | Esperas.test_motivo_que_cita_o_pedido_casa_o_cartao (H1, H5, H7) | id colado (`ped-dx`), maiúsculas, ponto final | passou |
| E1 id colado a hífen ou ponto não casa | Esperas.test_motivo_com_o_id_colado_ao_hifen_ou_ponto_nao_casa (H2) | `ped-d-2`, `ped-d.md`; id colado ATRÁS não coberto | passou, com lacuna (A1) |
| E1 `--kanban` vale no lugar do da raiz | Esperas.test_kanban_passado_vale_no_lugar_do_da_raiz (H3) | quadro da raiz com outro cartão | passou |
| E1 lista dos cartões casados e soma dono/credencial | Esperas.test_pedido_com_dois_cartoes_soma_... e test_pedido_filtra_... (H4) | dois cartões, espera aberta | passou |
| E1 custo/voltas não quebram sem motivos | CustoCasaOPedidoComOsCartoes (H6) | `motivos=None` | passou |
| E2 jarvis.md registra volta e espera | leitura do texto (linha 46) | n/a | sem teste (A3) |
| E3 fragmento de changelog | arquivo presente, formato `### Alterado` | n/a | passou (conferido à mão) |
| Pronto PQ-1 do pedido | `forge-check esperas --pedido REL-DEC` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_medidas_m14b`: 33 testes, OK.
- Mutantes H1 a H7 (`bin/forge-mutante tests/mutantes/hist-voltas-esperas.json`), rc=0: H1 a H7 todos `morreu`.
- Conferência da lista contra o diff: guardas novas em `cartoes_do_pedido` (`citados`), `cita_o_pedido` (lookbehind, lookahead, `(?!\.…)`, IGNORECASE), `cartoes_do_quadro` (`kanban`), a lista de saída e `motivos or {}`. Só o lookbehind ficou sem mutante. Mutante extra Q1 (`de` = `(?<![A-Za-z0-9._-])`, `para` = vazio, testes `Esperas`): `Q1 · sobreviveu · bin/forge-check:3407`.
- Vermelho antes do verde: `forge-testes --vermelho a83de9e2… --modulos test_medidas_m14b`, rc=0, `contagem: não prova (passa na base)=29; prova (asserção)=4` (kanban_passado, motivo_que_cita, pedido_com_dois_cartoes, pedido_filtra, todos falham na base e passam no head). O teste de id colado passa na base por ser negativo (a base não casa por motivo); a mutação o cobre (H2).
- Sonda manual (raiz de teste, `--pedido ped-d`): `xped-d` isolado não casa; `ped-d` junto de `xped-d` casa; `--kanban /nao/existe` não falha (cai no que o histórico tem), rc=0.
- Real: `forge-check --raiz ~/.forge-contrib esperas --pedido REL-DEC --kanban ~/.forge-contrib/KANBAN.md` (rc=0): `cartoes: PARECER-CITA-REGRA REL-D1A REL-R4`, total zerado (os cartões não têm espera registrada). Lista REL-R4 e REL-D1A; PARECER-CITA-REGRA entra pelo motivo "melhoria vista em 4 entregas do REL-DEC", o que é o desenho do E1, mas é um cartão de outra família (cuidado de leitura, não defeito).
- Suíte completa: não rodada por mim (brief: só os testes do item; o autor registra 2186 testes OK no pre-push).
- Acessibilidade e E2E de interface: não se aplicam (CLI, sem interface).

## Revalidação
Fechar A1 com teste do id colado atrás (`xped-d` e `1ped-d` não casam) e o mutante Q1 na spec; revalidar por delta (`forge-check delta`), com `H1` a `H8` mortos.
