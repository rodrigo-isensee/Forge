---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-por-branch
commit: f39a94ed266957ef62be4bc1061c2581da54a7db
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 · entrega por branch (E79.4)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| K-345: entrega só grava a ponta enviada | `test_selo_e_entrega.Entrega.test_k345_ponta_local_diferente_da_enviada_nao_grava` | local adiante de origin/<branch>; `--sem-gravar` segue conferindo | passou no head; falha na base |
| K-345: `.md` de controle da classe não isenta de QA | `test_isencoes.IsencaoDoDiff.test_k345_md_em_caminho_de_controle_da_classe_nao_isenta` | `.github/`, `hooks/`; catraca ausente (falha fechada) | passou no head; falha na base |

## Cenários e resultado real
- Vermelho antes do verde (manual, pois `forge-testes --vermelho` caiu por prazo/sinal no módulo `test_selo_e_entrega`, rc sem veredito; o módulo `test_isencoes` rodou H 5.7 s, B 5.5 s): testes do head sobre o código da base adc52def: `test_k345_ponta_local...` FAIL (`0 != 1`, gravou o local); `test_k345_md_em_caminho...` FAIL nos 3 casos. No head f4689e12: os dois passam (`python3 -I -m unittest discover -s tests -p <módulo> -k k345`, OK).
- Mutantes (rodada anterior, rev f4689e1254bf): 4 de 4 mortos; superada pela revalidação abaixo.
- Sondas E79.1 por amostra (`sonda_e791.py`, cópia do head): K-345b local adiante não grava (`gravou o local ... False`); K-345c diff só de `.github/*.md` não diz mais "isento de QA" (pede QA, classe C); K-187/K-147 y com x conferida: base do brief, `resultado: cumpriu`; K-246 pr atrás da develop exige conferência do head.
- Suíte inteira não rodada localmente; vale o check-run `bateria` do mesmo sha no CI do PR.

## Revalidação por delta (head f39a94ed, E79.8)
`forge-check parecer delta`: mudaram `bin/forge-check` (gravação só com a ponta lida no origin pelo `ls-remote`), `tests/test_selo_e_entrega.py` (3 testes novos; os antigos enviam antes de gravar), a spec de mutantes e o fragmento de changelog.
- Vermelho antes do verde (cópia do head em $TMPDIR com o `bin/forge-check` de f4689e12, sem a guarda nova; `python3 -I -m unittest discover -s tests -p test_selo_e_entrega.py -k <teste>`): `test_k345_branch_nunca_enviada_nao_grava` FAILED (failures=1); `test_k345_ref_de_rastreio_apagada_ou_forjada_nao_grava` FAILED (failures=1); `test_k345_origin_sem_resposta_nao_grava` FAILED (failures=1). No head, os três passam.
- Classes afetadas no head (`-k Entrega -k JanelaDaEntrega -k JuncaoLimpa`, segundo plano): `Ran 31 tests in 183.983s`, OK, rc=0. Suíte inteira não rodada local; vale o check-run `bateria` do mesmo sha.
- Mutantes (`bin/forge-mutante tests/mutantes/v0479-entrega-por-branch.json`), rev f39a94ed2669, spec 110b9d77: M1 e M2 morreram (1044), M3, M4 e M5 (10092), M6 (10091), M7 (10024), M8 (10026). 8 de 8 mortos, rc=0; cada linha de guarda mudada no diff tem mutante.
- Falha fechada confirmada: sem a branch no remoto, com a ref de rastreio apagada ou forjada e com o remoto sem resposta, a gravação recusa; `--sem-gravar` segue conferindo.
