---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s3-registro
commit: 1f31729169cd2163c883a4891ba761d0da9c1830
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 BP3 S3 (registro por item, E39.9)

Escopo: `hooks/agentes.py`, `tests/test_agentes_interrompidos.py`, specs de mutantes `tests/mutantes/v0479-bp3-s3-registro{,-2}.json`. Sem a suíte local (CI do PR é a prova da suíte). O `docs/pedidos/v0478.md` não existe neste clone; as obrigações vêm do fragmento de changelog e do diff.

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O1 reserva guarda caminho e hash do brief, nunca texto do prompt | test_a_reserva_guarda…, test_nenhum_byte_do_prompt…, test_so_o_caminho_seguro… | caminho inseguro, sem brief (lista vazia) | passou |
| O2 sessão provadamente morta com brief vai para `interrompidos` | test_sessao_morta_com_brief…, test_reserva_que_nunca_comecou…, test_sem_briefs… | id nulo, sem briefs | passou |
| O3 sessão viva, outro namespace ou PID ausente ficam nos agentes; fora do prazo não vira item | test_sessao_viva…, test_registro_fora_do_prazo…, test_o_interrompido_nao_ocupa_vaga | prazo | passou |
| O4 teto 64 | test_teto_de_interrompidos | máximo | passou |
| O5 `interrompidos` que não é lista torna o estado ilegível | test_interrompidos_que_nao_e_lista… | tipo inválido | passou |
| O6 sai no relançamento do mesmo tipo e caminho (hash novo), não em outro tipo/caminho nem em lançamento recusado | test_relancamento…, test_outro_tipo…, test_lancamento_recusado… | tipo/caminho distintos | passou |
| O7 sai na retomada por SendMessage do mesmo id; sem id ou outro destino não fecha | test_retomada…, test_send_message_sem_id… | id ausente | passou |
| O8 sai no prazo e deixa linha no `liberacoes.log` (id fora da forma vira `-`, sem descrição) | test_prazo_vencido…, test_vencido_com_id_fora_da_forma… | id inválido | passou |
| O9 só registro: nenhuma trava de recusa muda | test_agentes*.py (89 testes) | regressão | passou |

## Provas executadas
- `python3 -I -m unittest discover -s tests -p test_agentes_interrompidos.py`: 23 testes, OK. `-p 'test_agentes*.py'`: 89 testes, OK.
- Vermelho: `forge-testes --vermelho 004ce869` rodou 11 de 92 módulos e foi cortado pelo meu `timeout 500` (rc=124, sem veredito; o primeiro módulo saiu "H 1.7 s, B 1.5 s"). Valeu o vermelho dirigido: o teste novo contra `hooks/agentes.py` da base, numa cópia em `$TMPDIR`: `Ran 23 tests ... FAILED (failures=6, errors=25)`; no head, OK. Os 5 itens revertidos à base pelo `--vermelho`: `changelog.d/...`, `hooks/agentes.py`.
- Mutação: `bin/forge-mutante` das duas specs (29 mutantes): todos `morreu` (M1..M29; M15, M25, M26, M27, M28, M29 por erro do teste sob o mutante com o controle verde, que mata). Nenhum sobrevivente, nenhum equivalente.
- `forge-mutante --cobertura --base 004ce869`: todas as linhas de guarda mudadas em `hooks/agentes.py` saem `coberta`, nenhuma `não coberta` nem `isenta velha`.
- Simulação de merge: o remoto avançou (`fbac6fd3`, só parecer de segurança); trazido por merge fast-forward, sem conflito.

## Revalidação no head b3cd1ee4 (E39.9, delta da volta da segurança)
Delta (`forge-check parecer delta`, base d03cc57f): `hooks/agentes.py` (`caiu_em_finito`, `interrompidos_vigentes` levanta `EstadoIlegivel` com `caiu_em` não finito), `tests/test_agentes_interrompidos.py`, specs de mutantes (`-3.json` nova; `-2.json` e `.json` com trecho do M15 ajustado) e changelog. Head do remoto 1a86b815 só soma o parecer de segurança sobre b3cd1ee4.

| Obrigação (A1 da segurança) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `caiu_em` 10**400, -10**400, inf, -inf, nan deixam o estado ilegível | test_caiu_em_nao_finito_deixa_o_estado_ilegivel | inteiro enorme, não finito | passou |
| finito, mesmo enorme (10**300), é aceito; texto, None, lista não | test_caiu_em_finito_e_aceito_mesmo_enorme | máximo finito | passou |
| disparo com `caiu_em` enorme recusa (saída != 0) e não regrava o estado | test_disparo_com_caiu_em_enorme_e_recusado_sem_regravar_o_estado | recusa sem efeito | passou |

- `python3 -I -m unittest discover -s tests -p test_agentes_interrompidos.py`: 26 testes, OK (23 + 3 novos). (`-m unittest tests.test_agentes_interrompidos` não importa sob `-I`.)
- Vermelho dirigido (cópia em `$TMPDIR` com `hooks/agentes.py` de d03cc57f): `Ran 26 ... FAILED (failures=3, errors=4)`, todas nos 3 testes novos (inf, -inf, nan falham; 10**400 e `caiu_em_finito` ausente dão erro); no head, OK. O `forge-testes --vermelho` completo é lento (módulos demais); não vale como veredito.
- Mutação: `bin/forge-mutante --base d03cc57f` nas 3 specs: `base=d03cc57f22b83532dccb1a96acb43cb76ed6578a mb=d03cc57f22b83532dccb1a96acb43cb76ed6578a rev=1a86b81578537c6ba5015a692af7405b7c94cb1b`; M1..M32 `morreu`, sem sobrevivente nem equivalente. Os novos: M30 `hooks/agentes.py:647 · morreu`, M31 `:634 · morreu`, M32 `:633 · morreu`.
- `forge-mutante --cobertura --base d03cc57f`: linhas 633, 634, 647 `coberta` pelos M32, M31, M30; nenhuma `não coberta` nem `isenta velha`.
- Suíte inteira: no CI do PR (check-run `bateria` do mesmo sha), não rodada local.

## Revalidação no head 1f317291 (E39.9)
Delta (`forge-check parecer delta`, intervalo b3cd1ee4..1f317291, sem o que veio da develop): só `tests/mutantes/v047-h2-autor-fica-3.json`, M23 alinhado ao nome `registro` em `hooks/agentes.py:363` (E39.22). Nenhum código de produção mudou; o trecho `de` casa com a linha.
- `bin/forge-mutante --ids M23 tests/mutantes/v047-h2-autor-fica-3.json`: `M23 · morreu · hooks/agentes.py:363`, rc 0.
- `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k ConferirTodas`: 4 testes, OK.
- Suíte inteira: check-run `bateria` do CI do PR no mesmo sha, não rodada local.

Parecer: aprovado no head 1f317291.
