---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-agentes-pesado
commit: e54654c906288892ddc3462ee4503c55f848692f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E172.25, PR #859, VIGIA-AGENTES-PESADO)

## Gatilhos
Gatilhos: hook de controle (vigia de prazo em `agentes` e `pesado`), falha fechada no PreToolUse.

## Resumo
O código só aperta ou fica neutro, nunca libera: confirmado por leitura de `hooks/_comum.py:2856-2867`, `hooks/_comum.py:2884-2911`, `hooks/agentes.py:1420-1426` e `hooks/pesado.py:461-466`.

- `prazo_vencido`: para hook com marcador (`conformidade`, `parecer`) a condição é a mesma de antes (PostToolUse ou fora da sessão vigiada: só registra; senão, recusa). A única mudança é o caso `critico is None`, que antes sempre liberava e agora recusa no PreToolUse da sessão vigiada. Só aperta.
- `executar`: `hook.prazo_s` continua `PRAZO_DA_DECISAO_S` (3 s) para `conformidade` e `parecer`, porque eles não passam `prazo_do_hook`; continua `None` para os hooks sem `regra_do_prazo`; o `max` nunca encurta o prazo; `estender_prazo` não o reduz (`PRAZO_DO_MERGE_S <= hook.prazo_s` sai). Neutro para os hooks existentes.
- `clone_do_forge=True` em `agentes` e `pesado`: com `critico` None, só pesa em `sessao_vigiada` dentro de `prazo_vencido` (`falhar_fechado` sai cedo e `FORGE_GUARDA_ABERTA` não se aplica a eles). Estende a recusa ao clone do Forge. Só aperta.
- Prazos abaixo do timeout do `hooks.json`: `agentes` 8 s contra 10 s (PreToolUse `Agent|Task` e `SendMessage`); `pesado` 290 s contra 300 s (PreToolUse `Bash`). Nos outros eventos (SubagentStart/Stop, PostToolUse, PostToolUseFailure, PermissionDenied) o prazo vencido só registra; no `pesado`, o timeout de 10 s desses eventos vem antes dos 290 s, então nada muda lá.
- `PrazoVencido` é `BaseException` (`hooks/_comum.py:2829`), e nenhum `except Exception` de `agentes` ou `pesado` o engole. A escrita de estado é atômica (`gravar_json`, `os.replace`). Uma vez do `pesado` gravada no instante do alarme fica, no pior caso, presa até `TRAVA_S` ou até o pid morrer. Isso afeta só a disponibilidade e não abre nada.

A reprovação vem do CI vermelho no head revisado (run 45432245342, `pull_request`, headSha e54654c9). Uma das duas causas tira a prova por mutante do controle anterior (A1).

## Achados
- A1 (bloqueante) tests/mutantes/v0480-vigia-trava-critica.json:1 · Specs de mutante do vigia fora da fonte após mudar _comum.py:2860 e :2900: v0455-prazo P11 e v0480-vigia-trava-critica M1-M4 não aplicam mais, e o CI falha; o controle VIGIA-PRAZO-TRAVA perde a prova de morte. Realinhe o `de` dos 5 no mesmo commit.
- A2 (bloqueante) tests/test_hooks_volta_propriedades.py:312 · `subprocess.run(["git", "init", ...])` fora do ponto único de git dos testes: test_ambiente_git.LeituraEstatica falha no CI (suíte 5/5, 3.12 e 3.14). Use o utilitário de git dos testes.

## Sondas
- S1 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes · espera: OK · obtido: FAIL, v0455-prazo.json P11 e v0480-vigia-trava-critica.json M1, M2, M3, M4
- S2 · gh pr checks 859 (head e54654c9) · espera: suíte verde · obtido: suíte 4/5 e 5/5 (3.12 e 3.14) fail: test_forge_mutante.ConferirTodas e test_ambiente_git.LeituraEstatica (test_hooks_volta_propriedades.py:312)

## Detalhe dos achados
**A1.** Evidência: as linhas `de` de `tests/mutantes/v0455-prazo.json` P11 (a antiga `hook.prazo_s = PRAZO_DA_DECISAO_S if regra_do_prazo and critico is not None else None`) e de `tests/mutantes/v0480-vigia-trava-critica.json` M1, M2, M3 e M4 (a antiga `if critico is None or hook.entrada.get("hook_event_name") == "PostToolUse" or not sessao_vigiada(...)`) sumiram de `hooks/_comum.py`. O conjunto novo, `tests/mutantes/v0480-vigia-agentes-pesado.json` M1 a M6, cobre `critico None`, o arme sem marcador, o `prazo_do_hook` e o `clone_do_forge`. Ele não cobre "fora da sessão vigiada" (antigo M2) nem "depois da ferramenta" (antigo M4) na forma nova. Caminho: uma regressão futura que troque `not sessao_vigiada` ou o teste do `PostToolUse` passaria sem nenhum mutante a pegá-la. O efeito seria recusa indevida depois da ferramenta, ou um vigia que deixa de distinguir a sessão. Severidade: baixa, porque o controle segue correto hoje. É bloqueante porque é defeito provado (CI vermelho) num controle com gatilho. Correção mínima, a lista inteira: realinhar o `de` (e o `para`) de `v0455-prazo.json` P11 e de `v0480-vigia-trava-critica.json` M1, M2, M3 e M4 às linhas `hooks/_comum.py:2860`, `:2863` e `:2900`, sem apagar a guarda de nenhum. Esforço: P. Dono: autor da branch (dev do pedido), com o `qa-engineer`.

**A2.** Evidência: `tests/test_hooks_volta_propriedades.py:312` chama o git direto, com ambiente próprio. O ambiente é limpo (só `PATH` e `HOME`), então não há caminho de ataque: a variável de git herdada não chega ao subprocesso. O bloqueio vem do defeito provado (CI vermelho), não de risco. Correção mínima: usar o ponto único de git dos testes (o que `tests/test_ambiente_git.py:234` exige). Esforço: P. Dono: autor da branch, com review do `tech-lead`.

## Testes rodados (só os dos arquivos tocados)
- `python3 -m unittest tests.test_hooks_volta_propriedades.VigiaAgentesPesado tests.test_hooks.Hooks.test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera`: 4 testes, OK. Cobrem as fixtures VIGIA-AGENTES-PESADO dos dois hooks, o prazo de cada hook pelo relógio falso e o prazo abaixo do timeout do `hooks.json`.
- Suíte inteira: só no CI, vermelha no head (S2).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `unittest` local nos testes tocados e `gh pr checks` / `gh run view --log-failed` (só leitura). Não se aplicam a este delta, que não tem dependência nem workflow: `gitleaks`, `osv-scanner`, `zizmor`, `actionlint`.
