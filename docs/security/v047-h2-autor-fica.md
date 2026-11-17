---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 32c4832a80afd4d8cb4383fec8db0ac2d232d7dd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474, H2-AUTOR-FICA-ATE-O-MERGE (E2.78, volta por delta)

Delta lido (`forge-check parecer delta`, `f26b0721..32c4832a`, sem o que veio da base): no domínio só o fixture `tests/hooks/agentes/autor-ativo-inicio-repetido-nao-converte.json` (agente ativo com o mesmo id, de outro tipo, não se converte no `SubagentStart`). Fora do domínio: `docs/hooks-fixtures.md` (índice regerado) e `tests/mutantes/v047-h2-autor-fica-3.json` (M25). `hooks/agentes.py` igual a `f26b0721` (o `iniciar`, linha 987, já lido e sem achado). A junção da develop `bda457e4` só trouxe código da base: `git diff bda457e4 32c4832a` em `bin/`, `hooks/` (menos `agentes.py`), `.githooks/`, `.github/` e `scripts/` vazio. Já lido (no git, `f26b0721` e antes): o resto do H2, os achados A3 a A5 e as sondas S1 a S12.

## Gatilhos
Gatilhos: guarda em hook de controle (`R-TETO`, uma delegação de escrita por branch), leitura de estado que um agente pode corromper (`.forge/run/agentes.json`).

## Achados
- A3 (recomendado) tests/test_hooks.py:838 · corrigido: rpartition e a cauda exigida em "/.forge/run/agentes.json"
- A4 (recomendado) hooks/agentes.py:987 · sem mudança: SubagentStart do retomado depois de RESERVA_S acha a reserva vencida (sonda S8 do parecer em f26b0721); segue recomendado
- A5 (recomendado) hooks/agentes.py:745 · sem mudança: a recusa por reserva de retomada anuncia a expiração por expiracao_horas, não RESERVA_S (sonda S11 do parecer em f26b0721)

## Detalhe
O fixture novo fixa o lado seguro da guarda do `iniciar`: só o registro `SendMessage` com o mesmo `agent_id` se converte; um agente ativo com o mesmo id não troca de tipo nem de `desde` (o que reabriria o prazo dele). Mutante M25 (tira `a.get("tipo") == RETOMADA` da condição) aplicado numa cópia de `32c4832a`: `test_fixtures_do_pedido` falha só no fixture `autor-ativo-inicio-repetido-nao-converte`, então o teste distingue a guarda. Sem achado novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI (PR 639), que o portão do merge exige verde; rodei `tests/test_hooks_agentes_autor.py` no head (10 testes, OK) e o M25 na cópia. `gitleaks` ausente do PATH (lacuna; o delta não traz credencial nem configuração).
