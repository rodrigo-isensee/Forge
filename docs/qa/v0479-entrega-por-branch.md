---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-por-branch
commit: f4689e1254bf579f5110b4f58c677fac1b9f05e3
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
- Mutantes (`bin/forge-mutante tests/mutantes/v0479-entrega-por-branch.json`), spec 47c019ff, rev f4689e1254bf: M1 morreu (bin/forge-check:1044), M2 morreu (1044), M3 morreu (10081), M4 morreu (10081). 4 de 4; um por linha de guarda mudada no diff.
- Sondas E79.1 por amostra (`sonda_e791.py`, cópia do head): K-345b local adiante não grava (`gravou o local ... False`); K-345c diff só de `.github/*.md` não diz mais "isento de QA" (pede QA, classe C); K-187/K-147 y com x conferida: base do brief, `resultado: cumpriu`; K-246 pr atrás da develop exige conferência do head.
- Suíte inteira não rodada localmente; vale o check-run `bateria` do mesmo sha no CI do PR.
