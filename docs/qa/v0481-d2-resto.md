---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-resto
commit: f1d048fb8051ee5c7a6d152ccc767e6794ea37a6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: D2 forge-check pronto, delta do #881 (v0481 E11.15, classe C)

Escopo lido: `git diff ec5c7040..f1d048fb` (bin/forge-check, bin/forge_pronto.py, tests/test_forge_pronto.py, 4 specs de mutante, changelog). O parecer anterior (head ec5c7040, reprovado) tinha A1 (ids de mutante repetidos entre specs) e A2 (rc 2 de passo virava 1).

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1: as quatro specs rodam numa só chamada, ids únicos | rodada única, M1..M27 | ids únicos no conjunto | passou (rc 0) |
| A2: passo que sai 2 fica "não verificável" e a saída final é 2, nunca 0 | `test_passo_que_sai_2_fica_nao_verificavel_e_sai_2`; mutantes do delta em forge_pronto.py:56..76 | rc 2 de passo | passou |
| Reprovado (1) vence o não verificável; só sai 0 com tudo passando | `test_reprovada_vence_o_nao_verificavel`, teste do caminho feliz | mistura de 1 e 2 | passou |
| gh em erro sem `--corpo`: corpo não verificável com o motivo, sem rodar o teto, saída 2 | `test_gh_em_erro_sem_corpo_sai_2_com_o_motivo`, `CmdPronto.test_gh_em_erro_deixa_o_corpo_nao_verificavel` | erro do gh (motivo) | passou |
| Sem PR ou PR fechado (motivo None) segue reprovando; `--corpo` dado vence o motivo | `test_motivo_com_corpo_dado_confere_o_corpo`, testes de corpo ausente do parecer anterior | corpo None sem motivo | passou |
| Help do `pronto` diz "2 não verificável" e agora é verdade | leitura de bin/forge-check:10952 | n/a | passou |

## Provas
- Módulo do item: `python3 -I -m unittest discover -s tests -p test_forge_pronto.py` → `Ran 19 tests ... OK`. A suíte inteira fica para o CI do PR.
- Mutantes, uma chamada das quatro specs (`--processos 3`), rc 0: `pedido=v0481-d2-resto rev=f1d048fb8051`, M1..M27 todos `morreu`. Nenhum sobrevivente, nenhum equivalente, nenhuma "spec inválida".
- Sondas por leitura: `pr_da_branch` só devolve `(None, motivo)` em erro do gh; "no pull requests found" dá `({}, None)` e continua reprovando; HEAD solto (branch vazia) sem motivo também reprova. Nenhum caminho do delta transforma 2 em 0.
- O delta só soma o estado 2; reprovado segue 1 e nenhuma checagem foi afrouxada.

A1 e A2 do parecer anterior ficam resolvidos.
