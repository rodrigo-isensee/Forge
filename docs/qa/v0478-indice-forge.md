---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-indice-forge
commit: 7bd4913edcb31af54510071cb86fe53a07087174
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (índice do Forge, H7, E8.1)

Passada única no head 7bd4913e, só os testes dos arquivos tocados (`R-QA`); a suíte inteira é do check-run `bateria` do CI do PR, não rodada aqui.

## Critério → teste → resultado
| Critério (obrigação) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Índice gerado em dia com `bin/`, `hooks/`, `scripts/` e o mapa | `test_indice_esta_em_dia`, `test_conferir_da_rc_0_em_dia`; `indice-forge.py --conferir` | arquivo desatualizado | passou |
| Toda entrada versionada tem linha (guarda de suíte vazia, mínimo 60) | `test_toda_entrada_versionada_tem_linha` | lista vazia | passou |
| `--conferir`: rc 1 desatualizado ou sem arquivo, rc 0 em dia; sem argumento grava; argumento inválido rc 2 sem gravar | `Main.*` (5) | arquivo ausente, argumento extra | passou |
| Primeira linha de doc: Python, shell, sem doc, `\|` escapado, corte em 160 | `PrimeiraLinhaDeDoc.*` (4) | exatamente 160 e 161 caracteres | passou |
| Testes por arquivo: ordem, corte em 6 com "e mais N", sem oráculo, modo completo | `TestesDoArquivo.*` (3) | 6 e 7 módulos, lista só de oráculo | passou |
| Só versionados, um nível, sem `GIT_*` herdado (AR-7) | `Arquivos.*` (2) | não versionado, subpasta | passou |
| Mapa: `docs/indice-forge.md` aciona `test_indice_forge`; o índice não é portão | `test_testes_tocados` (162 testes, 1 skip herdado da base) | lista fechada `AVISOS` | passou |

## Cenários e resultado real
- `python3 scripts/indice-forge.py --conferir`: `docs/indice-forge.md: em dia`.
- `python3 -m unittest tests.test_indice_forge`: 18 testes, OK (16,6 s). `test_testes_tocados.py` via discover: 162 testes, OK, 1 skip existente na base (não adicionado por este diff).
- Vermelho antes do verde, `bin/forge-testes --vermelho 4182a6b9 --modulos test_indice_forge`:
  `vermelho: base=4182a6b95a12 head=7bd4913edcb3 módulos=test_indice_forge (restrito por --modulos)`; revertidos à base: `bin/forge-testes`, `changelog.d/v0478-indice-forge.md`, `docs/indice-forge.md`, `scripts/indice-forge.py`; `contagem: prova (API ausente)=18`, rc 0.
- Mutação, `bin/forge-mutante` nas 3 specs (`--processos 2`), `rev=7bd4913edcb3`: M1 a M22 `morreu`, nenhum sobrevivente, nenhum equivalente (M1 morreu por erro do teste declarado, que passa sem o mutante, aceito).
- `forge-mutante --cobertura --base 4182a6b9`: só linhas `coberta`, nenhuma condição do arquivo novo sem mutante; `base=4182a6b9… mb=4182a6b9…`.
- Observação: `-I` com `-m unittest tests.test_indice_forge` não importa o pacote `tests` (o módulo usa `from tests.ambiente_git`); é a forma do comando, não defeito (o `bin/forge-testes` e o discover do CI o rodam certo).
- Acessibilidade e E2E: não se aplicam (ferramenta de linha de comando e documento gerado).
