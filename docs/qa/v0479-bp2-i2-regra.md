---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i2-regra
commit: 0ce5173bf504d028f1a49eeb94491c9d22cdedae
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E38.11 (branch v0479-bp2-i2-regra)

Diff contra a base 004ce869: 7 arquivos, só texto e `tests/config.json` (sem código de produção). A suíte inteira roda no CI do PR; aqui rodaram só os módulos que leem os arquivos tocados.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E38.4 / `R-FLUXO`: fila em série e conserto no texto da regra | invariantes de `docs/regras/R-FLUXO.md` (2 trechos novos) conferidos por regex contra o arquivo: 0 ausentes | trecho removido ou reescrito | passou |
| Invariantes de `ritmo-e-corte.md` (4 novos) e do modelo `protecao-de-branch.md` (`Require merge queue`) | mesma conferência; `test_forge` (invariante traz regra e porquê; mínimos 48 arquivos e 410 trechos) | lista só encolhe, regex inválida | passou |
| Neutralidade e caminhos citados existem | `test_forge.py -k invariante -k regra -k neutr -k caminho`: 37 testes OK | caminho inexistente, termo de projeto | passou |
| Modelos de projeto | `test_modelos_projeto.py`: 20 OK; `test_invariante_gatilho.py`: 1 OK | n/a | passou |
| `tests/config.json` válido | `json.load` ok | n/a | passou |

## Cenários e resultado real
- Leitura do diff: o texto "bateria completa roda no CI do PR" saiu da `R-FLUXO` e passou para `ritmo-e-corte.md`; nenhum invariante apontava para ele (0 ausentes).
- Pedido de texto, sem regra de código nova: sem mutante nem vermelho-antes-do-verde aplicáveis (nenhum teste novo; só trechos de invariante).
- CI pago: nenhum rerun feito.

## Achados
- A1 (recomendado) docs/regras/R-FLUXO.md:14 · a linha de `develop` (bateria no CI do PR, tech-lead mescla) saiu da regra e só vive no `ritmo-e-corte.md`; sem invariante que a proteja na fonte, ela pode sumir sem teste cair.
