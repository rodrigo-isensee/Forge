---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-agente-preso-baixa
commit: af5dde244f771d0bf2f1b45e1ddc9c41128e685f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048 (AGENTE-PRESO-SEM-BAIXA, E12.2), volta 1 (E12.15)

Gatilhos: trava de controle do R-TETO (hook `agentes`), leitura de arquivo fora do repositório (transcript da sessão), comando novo que regrava o registro do teto.

## Delta lido
`forge-check parecer delta` de `2a310c7c..af5dde24`: nenhum arquivo do domínio mudou; fora dele, só `tests/mutantes/trava-agente-morto.json` (M6) e `tests/test_agente_preso_baixa.py` (comentário que cita a S9), além dos pareceres. `hooks/`, `bin/`, `scripts/` e `.github/` sem diff no intervalo; o mérito do código, aprovado na 1ª rodada (sondas S1 a S8, no git em `2a310c7c`), não reabre.

## Achados anteriores
- A1 (1ª rodada, bloqueante): corrigido. O `de` de M6 agora é `entrada.get("promptSource") == "system":` com `para` `True:` e casa com `hooks/agentes.py:492` (uma ocorrência na fonte). Conferido no head:
  - S9 refeita: `python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` · espera: OK · obtido: OK (junto com `tests.test_agente_preso_baixa` e `tests.test_trava_agente_morto`, 69 testes, OK).
  - `bin/forge-mutante --ids M6 tests/mutantes/trava-agente-morto.json` · obtido: `M6 · morreu · hooks/agentes.py:492`. O mutante segue exercendo a guarda C1 (com `True:`, toda entrada `type user` viraria texto de notificação), não só casando o texto.
  - CI do Revisar-sha (run 46162734439, head `af5dde24`): suíte partes 1 a 5, bateria (passos, python 3.14, verificações longas), teto de pulados, instalação, catraca e catraca (conferência) verdes; só `bateria (pareceres)` e o agregador `bateria` falham, porque esperam os pareceres de review e QA desta volta.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática e sondas locais com a biblioteca padrão; o delta não toca dependência, workflow nem segredo.
