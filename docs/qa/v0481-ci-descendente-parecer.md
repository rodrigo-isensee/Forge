---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-ci-descendente-parecer
commit: 523b0065035b3e0ce068d94360966ce20ed1c4d4
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481-ci-descendente-parecer (E8.20), 2ª volta do #895 por delta

Clone `/root/.forge-contrib/wt/v0481-ci-descendente-parecer-qa`, head `523b0065` (igual ao remoto e ao head do PR). Delta `aa26249f..523b0065`: o commit do autor `f8839529` (só duas linhas de skill) e duas fusões da develop; `bin/forge-check` do #895 e os testes dele não mudaram desde o parecer anterior.

- ci: 523b0065035b3e0ce068d94360966ce20ed1c4d4 verde

`gh pr checks 895` no head exato: todas as partes verdes (suítes 3.12 e 3.14 de 1/5 a 5/5, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, teto de pulados, instalação, árvore já provada); fora da linha, como manda PARECER-LE-O-CI: `bateria (pareceres)` (espera o parecer do head novo; o `PARECERES: failure` do log é o parecer antigo de `aa26249f`), `bateria` (agrega a anterior) e `catraca`. Causa da `catraca` (log do run 45696404450): `R-CONFORMIDADE: mudança em bin/forge-check ... só passa com o rótulo afrouxa-regra do dono, aplicado depois do último push (ADR 0008)`; não é defeito de código, é o rótulo do dono, já decidido em 25/11 07:27 ("aceitar a forma 'via' do #895").

Sem achados novos: o A1 do parecer anterior está fechado (provas abaixo).

## Critério -> teste -> resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 anterior: skills dentro do teto por arquivo | `test_metricas_texto` (2 OK local); engineering-practices 6961 de 6982, qa-testing 11760 de 11761 | teto por skill | passou; `tests/config.json` e `tests/test_metricas_texto.py` sem mudança em `aa26249f..523b0065` (0 linhas de diff): teto não subiu, teste não afrouxou |
| Encurtamento não tira regra nem invariante | `test_orcamento_instrucao` (8 OK local) | invariantes | passou |
| Skills continuam citando `via` e G3.7 | `test_pre_envio_brief` (29 OK) e `test_forge_check_pr` (71 OK, inclui `ChecksForaDaLinhaDoCi`) | n/a | passou |
| Regras da linha `via` (branco, gitlink, descendente, renomeação) | `LeOCiVia`, módulo `test_forge_check_pr` | espaço, tab, quebra, gitlink | 71 OK; código idêntico ao já provado (vermelho e M1 a M11 mortos no parecer de `aa26249f`) |
| CI do PR verde no head | `gh pr checks` do `523b0065` | n/a | verde fora das 3 da linha |

O texto das skills perdeu a frase "cujo diff toca apenas pareceres", mas a regra (diff só de pareceres) continua no `forge-check pr` e no brief; a forma `via` segue citada e testada.

## Mutantes e vermelho
Não rerodados: `bin/forge-check` do #895 e os testes não mudaram no delta (`f8839529` toca só skills). Vale a saída do parecer anterior (M1 a M11 mortos, vermelho no código de `2364a43b`).

## Melhoria vista
Nenhuma nova.
