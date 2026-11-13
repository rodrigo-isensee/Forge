---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-parte2
commit: 17c66fb251218a7656412fb5f48ff591a4f7b241
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 E4.2 (diretrizes 2, 11 e 16 na R-WIP e nas skills)

branch: melhoria/v047-jarvis-parte2 · head 17c66fb251218a7656412fb5f48ff591a4f7b241 · base 9b2c6474.

## Achados
- Nenhum bloqueante. A0 (bloqueante, parecer em 65cf916b) resolvido em 17c66fb2; A1 (recomendado) resolvido: a linha "Dois relógios (D-4)" voltou a skills/kanban-scrum/SKILL.md:73.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Diretriz 2: parado não se abandona (R-WIP) | `DiretrizesDoDonoNaRWip.test_a_regra_traz_as_tres_diretrizes_com_medida` | texto na linha única da R-WIP | passou |
| Diretriz 11: vaga livre não espera a versão | idem, e `test_as_skills_do_passo_citam_o_id` | só o merge espera | passou |
| Diretriz 16: pronto vai a PR próprio | idem | junção de frentes (R-FLUXO) | passou |
| Nenhuma regra nem invariante sumiu | `RegrasInviolaveis`, `AntiDuplicacao`, `RegrasComId`, `Neutralidade*` (16 testes) | invariantes de tests/config.json | passou |
| Teto do núcleo (37511) | `test_jarvis_nucleo`, `test_orcamento_instrucao` (25 testes) | teto de caracteres | passou |
| Links válidos | varredura dos `](*.md)` dos 3 arquivos | alvo existe | passou |

## Cenários e resultado real
- Diff lido (5 arquivos): os cortes são de redação (ex.: "decisão do dono", "AV5", "anti_duplicacao.excecoes", "pedido do usuário"). Todas as cláusulas normativas da R-WIP (1 cartão por agente, gargalo, teto, limites de coluna, Bloqueado/Aguardando, exceções do retrabalho) seguem no texto; nenhum item de `invariantes` falhou.
- Links: as 5 âncoras `R-LIMITES.md#…` viraram `R-LIMITES.md`; o arquivo existe com as 5 seções (R-MAIN, R-VERIFY, R-CUSTO, R-CONTRIB, R-COPIA). Nenhuma outra referência a essas âncoras em README, skills ou testes. `forge-check regras`: 12 em dia, 0 com aviso.
- Vermelho antes do verde (manual, cópia da base 9b2c6474 com o test_forge.py do head): `Ran 2 tests ... FAILED (failures=6)`: 5 subtestes do texto da R-WIP e o das skills caem. No head: `Ran 16 tests OK`.
- Mutação: cada trecho afirmado no teste é literal na linha; remover qualquer um derruba o subteste (vistos na base).
- Suíte inteira: no CI do PR, que não existe ainda (sem PR, só afetados; carga ~11-14 em 12 CPUs). `forge-testes --vermelho` oficial foi disparado em segundo plano; o veredito manual acima vale como prova.

## Revalidação por delta (head 65cf916b)
`forge-check parecer delta`: domínio = `skills/kanban-scrum/SKILL.md`, `skills/trabalho-em-paralelo/SKILL.md`, `tests/test_reval_delta.py` (junção da develop excluída).
- Texto das skills: cortes de redação; as cláusulas normativas (R-TETO, R-WIP, R-FLUXO, `forge-check sobreposicao|movimento|anotar|proximo`, lote por arquivo, lote de 3) seguem. Perdas: A1 e a frase que o teste exige (A0).
- Teste: `CITACOES_CONHECIDAS` de `tests/test_forge.py`/README.md de 14 para 15, coerente com a linha da R-WIP.
- Execução: `python3 -m unittest tests.test_reval_delta tests.test_metricas_texto tests.test_jarvis_nucleo` -> `Ran 29 tests ... OK`. `python3 -m unittest tests.test_forge` (2 rodadas, ~820 s): `Ran 583 tests ... FAILED (failures=1)`, sempre `test_as_skills_do_passo_citam_o_id`. Defeito do delta, não do ambiente: REPROVADO em 65cf916b.
- Vermelho/mutação: sem teste novo de regra neste delta; nada a repetir.

## Revalidação por delta (65cf916b..17c66fb2, E3.25)
Qual veredito vale: o de 17c66fb2 (este, APROVADO). A aprovação anterior (1c3e34f2) e a reprovação do 442b90ed valiam cada uma para o seu head (1c3e34f2 e 65cf916b); a reprovação não foi revogada por opinião, foi superada pelo conserto. O 442b90ed só altera este parecer, então o código de 442b90ed é o de 17c66fb2.
`forge-check parecer delta`: domínio = `skills/kanban-scrum/SKILL.md`, `skills/trabalho-em-paralelo/SKILL.md`, `tests/test_forge.py`.
- tests/test_forge.py:626: a asserção passa a exigir `com CI verde, entra na `develop` por PR próprio, sem juntar frentes (`R-FLUXO`)`, que é literal em skills/trabalho-em-paralelo/SKILL.md:14; PR próprio e o ID R-FLUXO continuam exigidos, nada foi removido do teste.
- skills/trabalho-em-paralelo/SKILL.md:10: volta "(serializam)", só redação; kanban-scrum: volta a linha dos dois relógios (D-4, `relogios:`).
- Execução (sem PR aberto, só afetados): `python3 -m unittest tests.test_forge.DiretrizesDoDonoNaRWip tests.test_reval_delta tests.test_metricas_texto tests.test_jarvis_nucleo tests.test_forge.RegrasInviolaveis tests.test_forge.AntiDuplicacao tests.test_forge.RegrasComId` -> `Ran 39 tests ... OK`. A suíte inteira não foi rerrodada local (carga ~11 a 14 em 12 CPUs, diretriz 15): na rodada anterior (65cf916b) o único FAIL de 583 era este teste, e o delta toca só esta asserção e duas linhas de skill; a suíte inteira vale pelo CI do PR, ainda não aberto.
- Vermelho/mutação: sem teste novo de regra; o ajuste da asserção foi visto falhar em 65cf916b (rodadas do parecer anterior) e passar agora.
