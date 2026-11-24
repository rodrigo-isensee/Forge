---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 1467c3425e822ef75901c1dbc8c607635eba75f8
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E174.39, rastreio do critério à prova, PR #868), delta

Base aabc476c, head 1467c342; delta desde 334af9c9 (parecer anterior, reprovado por A1). Mudou no domínio do QA só o teste novo `test_brief_alterado_nao_prova_mesmo_com_outro_brief_intacto_conferindo_a_etapa` e a lista `testes` do mutante D73 na spec; código de produção intacto.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Brief alterado depois do selo não prova, mesmo com outro brief intacto conferindo a etapa (A1) | `test_brief_alterado_nao_prova_mesmo_com_outro_brief_intacto_conferindo_a_etapa` | selo sha256 do brief; etapa conferida por outro brief | passa; D73 morre |
| Brief alterado não prova | `test_brief_alterado_depois_do_selo_nao_prova` | sha256 diferente do selo | passa |
| Brief Y alterado para o `Cobre:` de X não confere a etapa | `test_outro_brief_alterado_depois_do_selo_nao_confere_a_etapa` | selo de Y | passa |
| Demais CA | demais testes de `test_criterios` | sem mudança | 10 testes OK local |

## Vermelho antes do verde
O teste novo guarda um mutante, não uma correção de código: contra a base 334af9c9 (mesmo código de produção) ele passa, como esperado (`bin/forge-testes --vermelho 334af9c9 --modulos test_criterios`, rc 1: `contagem: não prova (passa na base)=10`). O vermelho está no mutante D73, abaixo: sem o teste o D73 sobrevivia (parecer anterior); com ele, morre.

## Mutação
`bin/forge-mutante --base 334af9c91abe <3 specs> --processos 3`: `rev=1467c3425e82`; D73 `morreu · bin/forge-check:8196`; D71, D72, D74 a D720 e D717 `morreu`; nenhum sobrevivente. A spec do D73 lista o teste novo.

## CI
Check-run `bateria` do head 1467c342 ainda em andamento na leitura (suíte 1 a 5/5 pendentes); `bateria (pareceres)` falha por ler o parecer reprovado anterior, que este substitui, e `Catraca` falha por gate de governança do ADR 0008 (rótulo do dono), não defeito de código. A suíte inteira vale pelo `bateria` do mesmo sha.

A1 do parecer anterior: fechado.
