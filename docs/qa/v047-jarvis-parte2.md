---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-jarvis-parte2
commit: 65cf916b96d6bfa7e0acb7472bfe21b2c7b91551
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 E4.2 (diretrizes 2, 11 e 16 na R-WIP e nas skills)

branch: melhoria/v047-jarvis-parte2 · head 65cf916b96d6bfa7e0acb7472bfe21b2c7b91551 · base 9b2c6474.

## Achados
- A0 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:15 · em 65cf916b a frase "sem juntar frentes" quebra DiretrizesDoDonoNaRWip.test_as_skills_do_passo_citam_o_id (tests/test_forge.py:617): FAIL em 2 rodadas de tests.test_forge (583 testes, failures=1). O commit 17c66fb2 (E3.22) declara o conserto; precisa de novo delta.
- A1 (recomendado) skills/kanban-scrum/SKILL.md:72 · a skill deixou de citar os dois relógios (D-4) e a linha `relogios:`; agents/agile-coach.md:17 e bin/forge_voltas.py seguem com a medida. Sem teste que a exija; confirmar que o corte é intencional.

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
