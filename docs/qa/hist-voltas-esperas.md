---
tipo: qa
contrato: 1
pedido: hist-voltas-esperas
branch: melhoria/hist-voltas-esperas
commit: d623eaf3234393d585d3212b0364a9da9f5f2be9
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: hist-voltas-esperas

Base a83de9e24908195fef0c92ebfcb1603518b58390, head d623eaf3234393d585d3212b0364a9da9f5f2be9 (revalidação da volta 1; o parecer anterior, 3a58a35, reprovou sobre 27f86b6). Pedido de controle (`bin/forge-check`): vale a prova de mutação declarada, conferida contra o diff.

## Achados
- A1 (recomendado) bin/forge-check:3407 · fechado na volta 1: teste do id colado atrás e mutante H8, morto
- A2 (recomendado) bin/forge-check:5184 · `--kanban` sem `--pedido` é aceito e ignorado em silêncio (o uso diz `--pedido ID [--kanban ARQUIVO]`); o `--help` já avisa "com --pedido", mas não há erro.
- A3 (recomendado) agents/jarvis.md:46 · E2 (registrar volta e espera como movimento) é só texto; nenhum teste o guarda além do `test_o_movimento_do_jarvis_alimenta_as_esperas`, que não lê o jarvis.md.

## Critério → teste → resultado
Escopo E1 a E3 do pedido (o pedido não traz CA-n em EARS; cada item de escopo é a obrigação).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 casar pelo motivo do movimento | Esperas.test_motivo_que_cita_o_pedido_casa_o_cartao (H1, H5, H7) | id colado (`ped-dx`), maiúsculas, ponto final | passou |
| E1 id colado a hífen ou ponto não casa | Esperas.test_motivo_com_o_id_colado_ao_hifen_ou_ponto_nao_casa (H2) | `ped-d-2`, `ped-d.md`; id colado ATRÁS não coberto | passou; lacuna fechada na volta 1 por test_motivo_com_o_id_colado_atras_de_letra_digito_ponto_ou_hifen_nao_casa (H8) |
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

## Revalidação (volta 1, d623eaf)
Delta 27f86b6..d623eaf (`forge-check delta`): só `tests/mutantes/hist-voltas-esperas.json` (+H8) e `tests/test_medidas_m14b.py` (+1 teste); `bin/` e `agents/` intactos.
- `python3 -m unittest tests.test_medidas_m14b`: 34 testes, OK.
- `bin/forge-mutante tests/mutantes/hist-voltas-esperas.json`, rc=0: H1 a H8 todos `morreu` (H8 em bin/forge-check:3407, equivale ao meu Q1 e cobre o lookbehind, a única guarda sem mutante).
- Vermelho: `forge-testes --vermelho a83de9e2… --modulos test_medidas_m14b`, rc=0, `vermelho: base=a83de9e24908 head=d623eaf32343`; `não prova (passa na base)=30; prova (asserção)=4`. O teste novo é negativo e passa na base; a prova dele é o mutante H8.
- `scripts/validar-plugin.sh`: Validation passed.
- Suíte completa: não rodada por mim (brief: só os testes do item).
- A2 e A3 seguem recomendados, sem devolver.
