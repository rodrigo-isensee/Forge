---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i2-regra
commit: 80f4bd1f2912d3222559b954eafde362e9e1a5dc
parecer: aprovado
escopo: incremental
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

## Revalidação (head 80f4bd1f, delta desde 0ce5173b)
Delta lido por `forge-check parecer delta`: `changelog.d/v0479-bp2-i2-regra.md`, `docs/protecao-de-branch.md`, `skills/trabalho-em-paralelo/ritmo-e-corte.md`, `templates/projeto/docs/engineering/protecao-de-branch.md` (só texto; o 4c53dc9c é merge com pareceres de review e segurança). Mudanças: fila "à mão até a I4" no Forge, passo 8 e Limites sem prometer o `bin/forge-fechar`, condições 3 e 4 do conserto completas (`--match-head-commit`, pais e árvore do `merge-tree`, pulado por id, classe ou módulo).
| Módulo | Resultado |
|---|---|
| `test_forge.py -k invariante -k regra -k neutr -k caminho` | 31 testes OK (37 no parecer anterior: a seleção `-k` muda com os nomes do head atual; nenhum falhou) |
| `test_modelos_projeto.py` | 20 OK |
| `test_invariante_gatilho.py` | 1 OK |
| `tests/config.json` | `json.load` ok |
Os invariantes de `ritmo-e-corte.md` e do modelo `protecao-de-branch.md` seguem presentes após a reescrita. Sem código, sem vermelho/mutante aplicáveis; nenhum rerun de CI.

## Achados
- A1 (recomendado) docs/regras/R-FLUXO.md:14 · a linha de `develop` (bateria no CI do PR, tech-lead mescla) saiu da regra e só vive no `ritmo-e-corte.md`; sem invariante que a proteja na fonte, ela pode sumir sem teste cair.
