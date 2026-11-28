---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-textos-time
commit: 932c43c7b8550a2c9e2759ed38825fe969cfe8ad
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 textos do time (E19.4)

Escopo: diff `0c47762a..932c43c7` (jarvis.md, tech-lead.md, falar-com-o-dono, `tests/config.json`, fragmento de changelog). Sem suíte local; o CI do PR roda a bateria.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| R-DECISAO: recibo no meio da rodada (jarvis.md, toda-mensagem.md) | invariantes `RegrasInviolaveis.test_trechos_obrigatorios` | trecho ausente do texto | passou (3 testes OK) |
| R-FLUXO: tech-lead lê ritmo-e-corte | idem | idem | passou |
| Invariante novo traz regra e porquê | `test_invariante_traz_regra_e_porque_e_o_legado_so_encolhe` | invariante sem regra/porque | passou |
| Teto de instrução dos textos | `test_orcamento_instrucao.py` | tamanho máximo | 8 OK |
| Métricas de texto | `test_metricas_texto.py` | n/a | 2 OK |
| Gatilhos | `test_invariante_gatilho.py`, `test_jarvis_nucleo.py`, `test_textos_dono_f7/f10.py` | n/a | 1, 43, 2, 3 OK |

Vermelho antes do verde (conferência direta): os 3 trechos novos de `invariantes` não casam nos arquivos da base `0c47762a` (ausentes: jarvis, toda-mensagem, tech-lead) e casam no head, então `test_trechos_obrigatorios` cai na base e passa no head. Não rodei `forge-testes --vermelho`. Os 3 invariantes novos têm entrada em `invariantes_motivo_trecho` com regra e porque. `forge-check docs` sem erro. Não há código de controle no diff, então não há mutantes.
