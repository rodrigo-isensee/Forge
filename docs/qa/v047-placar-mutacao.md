---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-placar-mutacao
commit: 4b465b8cef7333485127a1abdadb21d7546a3bbc
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 · E1.101 (placar de mutação: falhas= e aviso do --desde)

Branch melhoria/v047-placar-mutacao, head 4b465b8c, intervalo origin/develop..4b465b8c (merge-base 6517ff14). Classe C. Sem especificação de UX nem contrato de API: as obrigações vêm da E1.101 do pedido v047. No check-run do PR #556 as partes da suíte ainda estavam `pending` quando li; a prova da suíte inteira é o CI do mesmo sha, não a rodada local.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1.101: spec com rc diferente de zero marca `falhas=<n> (<spec>)` na linha `placar:` | `PlacarDaRelease.test_spec_com_rc_diferente_de_zero_aparece_na_linha_placar` | uma falha entre specs boas; rc do placar segue 0 | passou; vermelho na base; M4 morto |
| Sem falha, a linha não ganha sufixo | `test_uma_rodada_por_spec_soma_as_classes_e_sai_0_com_sobrevivente` | ausência de falha | passou; M5 morto |
| `--desde` que não é tag neste clone avisa (ramo) | `test_desde_que_nao_e_a_tag_anterior_ou_nao_e_tag_avisa_sem_mudar_o_rc` | ramo em vez de tag | passou; M1 e M7 mortos |
| `--desde` diferente da tag imediatamente anterior à `--versao` avisa; igual não avisa; versão igual à tag não a conta como anterior | mesmo teste (4 subcasos: v0.1.0/0.3.0, v0.2.0/0.3.0, v0.1.0/0.2.0, ramo) | tag anterior exata, `<` contra `<=`, um aviso só, rc 0 | passou; M2, M3 e M6 mortos |
| M10 da spec v0457-escopo-ponto-2 aponta o trecho atual | conferência direta | trecho `de` presente em `bin/forge-check:2757` | `de in bin/forge-check` = True |

## Vermelho antes do verde
Comando: `bin/forge-testes --vermelho 6517ff14 --modulos test_forge_mutante` (rc=0). Contagem real: `não prova (passa na base)=110; prova (asserção)=2`. Os dois que provam são os dois testes novos (falha na base por asserção); os 110 restantes já existiam e passam nos dois lados.

## Mutação (pedido de controle de `scripts/`, 7 mutantes, um por linha de guarda mudada)
`bin/forge-mutante --cobertura --base 6517ff14` (rc=0): todas as 7 linhas de guarda de `scripts/placar-mutacao.py` (49, 55, 57, 58, 79, 92, 96) saem `coberta` por M1..M7; a spec editada v0457-escopo-ponto-2 é só listada.
`bin/forge-mutante tests/mutantes/v047-placar-mutacao.json` (rc=0): M1 a M7 `morreu`, nenhum sobrevivente.

## Bordas conferidas na leitura
Sem tag `v*` no clone: `anterior` fica None e não há aviso de tag diferente, só o de "não é tag". `--versao` fora do padrão numérico: `alvo` None, vale a maior tag. Aviso só imprime; o rc 0 do placar não muda (placar, não portão). Sem teste para `--versao` fora do padrão; é fronteira menor, sem bug.

## Bugs
Nenhum aberto.
