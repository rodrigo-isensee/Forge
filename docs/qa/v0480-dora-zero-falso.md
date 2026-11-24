---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-dora-zero-falso
commit: 38d9c349c671dd76f5a71f30f3734bac2d0d64d3
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 (E160.3, FORGE-DORA-ZERO-FALSO, PR #844)

Base 789fc141, head 38d9c349. Mudança: `bin/forge_dora.py` (quadro ausente ou ilegível sai `nao-medido` com o motivo, e não 0, na vazão, taxa de falha e recuperação), `tests/test_forge_dora.py`, spec `tests/mutantes/v0480-dora-zero-falso.json`, retirada do M7 da spec v0457 (o teste dele foi substituído) e o fragmento do changelog. Sem especificação de UX nem contrato de API: as obrigações são as afirmações do fragmento e do docstring (ausente → nao-medido; ilegível → nao-medido; existente e vazio segue 0; frequência não é afetada).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Historico ou escapes ausente sai `nao-medido` com motivo, e não 0 | `Metricas.test_quadro_ausente_ou_ilegivel_sai_nao_medido_e_nao_zero` | pasta `docs/kanban` sem os dois arquivos; `recusados` segue vazio | passou; vermelho na base; M1 a M4 morreram |
| Arquivo ilegível (pasta no lugar do arquivo) sai `nao-medido` | mesmo teste, 2ª volta do laço | `ler_texto` devolve None | passou |
| Arquivo existente e vazio segue 0 | `Metricas.test_quadro_vazio_existente_segue_zero` | arquivo de 0 byte nos dois quadros | passou; M4 morreu por ele |
| Saída de texto do comando mostra o estado e o motivo | `Comando.test_raiz_pedidos_le_o_quadro_de_la` | quadro ausente via `--raiz-pedidos` | passou; vermelho na base |
| Menos de 20 releases sem `taxa_pct`, com `escapes.md` existente | `Brutos.test_taxa_pct_so_com_20_releases` (ajustado para criar o arquivo vazio) | limite 20 | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_forge_dora.py`: 17 testes, OK, 2,2 s.
- Sem suíte local; a inteira roda no CI do PR (`R-QA`).
- Combinação mista (só um dos dois arquivos ausente) não tem teste próprio: os dois caminhos são independentes no código (`vazao` e `falhas`) e cada um tem a guarda coberta por M2 e M3.

## Vermelho antes do verde
`bin/forge-testes --vermelho 789fc14160fd7bb07096668ca0bd567e8458e01c --modulos test_forge_dora`:
```
revertidos à base: bin/forge_dora.py, changelog.d/v0480-dora-zero-falso.md
mantidos no HEAD: tests/mutantes/v0457-dora.json, tests/mutantes/v0480-dora-zero-falso.json, tests/test_forge_dora.py
tests.test_forge_dora.Comando.test_raiz_pedidos_le_o_quadro_de_la · H=ok · B=falha · prova (asserção)
tests.test_forge_dora.Metricas.test_quadro_ausente_ou_ilegivel_sai_nao_medido_e_nao_zero · H=ok · B=falha · prova (asserção)
tests.test_forge_dora.Metricas.test_quadro_vazio_existente_segue_zero · H=ok · B=ok · não prova (passa na base)
contagem: não prova (passa na base)=15; prova (asserção)=2
```
O teste "vazio segue 0" passa na base por desenho: é guarda de não regressão da fronteira (arquivo vazio), provada pelo M4 abaixo.

## Mutação
`bin/forge-mutante tests/mutantes/v0480-dora-zero-falso.json`:
```
forge-mutante: pedido=v0480-dora-zero-falso rev=38d9c349c671 spec=d20d71c4ae8b1f81338358a83f2947fcffee3adeeab8a401168a0232964ee152
M1 · morreu · bin/forge_dora.py:69 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M2 · morreu · bin/forge_dora.py:96 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M3 · morreu · bin/forge_dora.py:115 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
M4 · morreu · bin/forge_dora.py:160
```
Quatro mortos, nenhum sobrevivente. Cobertura contra a base (`forge-mutante --cobertura --base 789fc141…`): as quatro condições mudadas (linhas 69, 96, 115, 160) saem `coberta`; a condição apagada (`ler_texto(arq) or ""`) sai `isenta` com motivo; `spec editada · tests/mutantes/v0457-dora.json` é a retirada do M7, cujo teste foi substituído, sem guarda órfã.
