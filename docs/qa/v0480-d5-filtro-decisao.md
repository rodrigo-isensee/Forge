---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-d5-filtro-decisao
commit: 15fc9f9cff565c301e440a6f3cd78672995c1702
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E173.26 (PR #863, filtro de decisão D5, delta E173.25)

Delta de `8916a422..15fc9f9c` (domínio: código e testes): só `tests/test_decisor.py` (+15 linhas) e `tests/mutantes/v0480-d5-filtro-decisao-4.json` (+10, mutante D5M29). Nenhum arquivo de `bin/` mudou. O restante do parecer anterior (E173.20) segue valendo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A3: `GIT_DIR` de outro repositório no ambiente não confirma parecer que não está no git da raiz: pergunta | `ConfirmacaoDaSeguranca.test_git_dir_de_outro_repositorio_no_ambiente_vira_pergunta` | `GIT_DIR` herdado apontando para repositório com o mesmo parecer no HEAD | passou; rc 1 e `condição não atendida: seguranca` |

O teste roda a CLI real (`decisoes registrar`) com `GIT_DIR` do outro repositório, parecer só na árvore da raiz e o mesmo texto commitado no outro; o oráculo é o recibo de pergunta, não uma chamada interna.

## Execução local (só arquivo tocado)
`python3 -I -m unittest discover -s tests -p test_decisor.py`: 21 testes OK. Suíte inteira: check-run `bateria` do CI do PR.

## Vermelho antes do verde
O comportamento já existia no código (a limpeza das `GIT_*` está em `bin/forge_decisor.py:57` desde o 8916a422), então o teste passa na base: `forge-testes --vermelho 8916a422 --modulos tests.test_decisor` sai "não prova (passa na base)=21, nenhum teste prova a mudança", esperado para teste que cobre guarda já presente. A prova de que o teste falha sem a guarda é o mutante abaixo.

## Mutação
`bin/forge-mutante --base 8916a422 tests/mutantes/v0480-d5-filtro-decisao-4.json`:
```
base=8916a422b5b7b811f858847881a686e7f3108f19 mb=8916a422b5b7b811f858847881a686e7f3108f19 rev=15fc9f9cff565c301e440a6f3cd78672995c1702
forge-mutante: pedido=v0480-d5-filtro-decisao rev=15fc9f9cff56 spec=7777386f1aa3d897341bdf91708d9e2e856ca522e840e18bcac66f312c82fe51
D5M29 · morreu · bin/forge_decisor.py:57
```
D5M29 (`if not k.startswith("GIT_")}` -> `if True}`) é o Q1 do parecer anterior, agora declarado e morto pelo teste novo. A3 fechado.

Sem bug aberto; sem acessibilidade aplicável (CLI).
