---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-agentes-pesado
commit: e54654c906288892ddc3462ee4503c55f848692f
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.23 (PR #859, agentes e pesado recusam no prazo vencido do vigia; item E172.3)

Revisão completa do diff `f82c7cc5..e54654c9` (base `develop` entrou por merge em e54654c9, fora do escopo): `hooks/_comum.py`, `hooks/agentes.py`, `hooks/pesado.py`, 6 fixtures, `tests/test_hooks.py`, `tests/test_hooks_volta_propriedades.py`, spec de mutantes e fragmento de changelog.

## Achados
- A1 (bloqueante) tests/mutantes/v0480-vigia-trava-critica.json:6 · o diff reescreve as linhas do prazo_vencido e do hook.prazo_s em hooks/_comum.py, e o `de` de M1 a M4 desta spec e de P11 em tests/mutantes/v0455-prazo.json:115 não existe mais; ConferirTodas falha no CI (parte 4/5). Alinhe as 5 entradas no mesmo commit.
- A2 (bloqueante) tests/test_hooks_volta_propriedades.py:312 · o `git init` do teste novo monta o env à mão, sem `sem_manutencao` de tests/ambiente_git.py; LeituraEstatica.test_nenhum_modulo_roda_git_sem_o_ponto_unico falha no CI (parte 5/5). Monte o env com `sem_manutencao({...})`.
- A3 (recomendado) hooks/pesado.py:450 · se o alarme de 290 s cai entre o gravar_a_vez e a saída do hook, a tarefa é recusada com a trava já gravada no pesado.json e sem PostToolUse que a solte; janela estreita, sem sonda. Grave a vez como último passo antes do return ou solte a trava no PrazoVencido.
- A4 (recomendado) docs/hooks.md:1 · a seção do vigia e do orçamento ainda descreve o vigia só no conformidade e no parecer (pendência declarada no PR); doc afetada pela mudança deveria vir no mesmo item.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (env -i, head e54654c9) · espera: OK · obtido: FAIL, 5 entradas com `de` fora da fonte (v0455-prazo P11; v0480-vigia-trava-critica M1 a M4)
- S2 · python3 -m unittest tests.test_ambiente_git.LeituraEstatica.test_nenhum_modulo_roda_git_sem_o_ponto_unico (env -i, head e54654c9) · espera: OK · obtido: FAIL, test_hooks_volta_propriedades.py:312 env não montado com sem_manutencao

## Parecer
Reprovado. A lógica está correta e enxuta: no `prazo_vencido`, o ramo novo só alcança hooks sem `critico` (agentes, pesado), então conformidade e parecer não mudam; `prazo_do_hook` só alonga (`max`), 8 s e 290 s ficam abaixo dos timeouts de 10 s e 300 s do PreToolUse no hooks.json; nos eventos fora do PreToolUse (SubagentStop, PostToolUseFailure, PermissionDenied) o vencimento só vai ao erros.log. Tamanho dentro do H1 (cerca de 20 linhas de código).

Testes: `tests.test_hooks_volta_propriedades.VigiaAgentesPesado` rodado aqui, 3 testes OK em 3,7 s; a inversão da asserção do E169.1 em `tests/test_hooks.py` segue a decisão do dono e cobre o PreToolUse e o SubagentStop. Spec `v0480-vigia-agentes-pesado.json` com M1 a M6 (autor: 6 de 6 mortos em 85d7f988), um por guarda mudada.

CI do head e54654c9 (run 45432245342): suíte partes 4/5 e 5/5 vermelhas nas duas versões de Python, pelas falhas de A1 e A2, ambas causadas pelo diff e reproduzidas localmente (S1, S2). `bateria (pareceres)` e `catraca` vermelhos aguardam os pareceres. Na volta: corrigir A1 e A2, rodar os dois testes das sondas e o `bin/forge-mutante` das specs alinhadas antes do push.
