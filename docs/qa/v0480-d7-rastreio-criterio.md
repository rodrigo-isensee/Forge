---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 334af9c91abe5c6bbb4a4abe2a5fb4f20933a2bb
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E174.36, rastreio do critério à prova, PR #868), delta

Base aabc476c, head 334af9c9; delta desde 3ed7a573 (parecer anterior, aprovado). Mudança no domínio do QA: `etapas_conferidas(..., selados)` só conta brief de selo intacto (segurança A2), `provas_por_criterio` passa os selados, teste novo `test_outro_brief_alterado_depois_do_selo_nao_confere_a_etapa`, mutantes D718 a D720.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Brief alterado depois do selo não prova | `test_brief_alterado_depois_do_selo_nao_prova` | sha256 diferente do selo | passa, mas D73 sobrevive (A1) |
| Brief Y alterado para o `Cobre:` de X não confere a etapa (A2) | `test_outro_brief_alterado_depois_do_selo_nao_confere_a_etapa` | selo de Y não confere | passou; vermelho na base; D718, D719, D720 morreram |
| Demais CA do parecer anterior | 7 testes de `test_criterios` | sem mudança | passam (9 testes OK local) |

## Vermelho antes do verde
`bin/forge-testes --vermelho 3ed7a573dc9999ff05f8cc9c485603286c72fc59 --modulos test_criterios`, rc 0: `test_outro_brief_alterado_depois_do_selo_nao_confere_a_etapa · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=8; prova (asserção)=1`.

## Mutação
`bin/forge-mutante --base 3ed7a573dc99 <3 specs> --processos 3`, rc 1: `base=3ed7a573dc99 rev=334af9c91abe`; `D73 · sobreviveu · bin/forge-check:8196`; D71, D72, D74 a D720 `morreu`.
D73 (ler o brief cru em `provas_por_criterio`) passou a sobreviver porque a guarda nova em `etapas_conferidas` já tira a etapa do brief alterado das conferidas, e o teste alvo usa um brief que é o único da etapa. Não é equivalente: com um segundo brief intacto conferindo a mesma etapa (`Cobre:` igual), o brief alterado com `PQ ... cobre: C-n` provaria sob D73 e não no código real.

## CI
Check-run `bateria` do head 334af9c9: `CI` em andamento na leitura; a suíte inteira vale por ele. `Catraca` vermelha neste sha: gate de governança do ADR 0008 (rótulo `afrouxa-regra` do dono depois do último push), não defeito de código.

## Achados
- A1 (bloqueante) tests/test_criterios.py:118 · mutante D73 sobrevive após E174.33: nenhum teste prova que `provas_por_criterio` lê só o brief selado. Teste: 2º brief intacto confere a etapa e o alterado traz `cobre: C-n` com o mesmo `Cobre:`; ou D73 vira mutante com teste que o mate.
