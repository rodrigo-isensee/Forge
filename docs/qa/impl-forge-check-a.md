---
tipo: qa
contrato: 1
pedido: impl-forge-check-a
branch: melhoria/impl-forge-check-a-a3
commit: caa3d8d0132d080387cb710456319eaa27bce4af
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
revisor: forge:qa-engineer
data: 2026-10-30
---
# QA: impl-forge-check-a (branch a3)

Diff lido: `234dbe0..caa3d8d` (código em `bin/forge-check` e `tests/test_forge.py`; o resto são pareceres e fragmento).

## Item entregue e M14 (agents/tech-lead.md:19)
E4 do pedido (FC-VERSAO-BASE-AVISO): `base_do_repositorio` tira um prefixo `origin/` de `--base` (`removeprefix`), então `--base origin/develop` não vira refs/remotes/origin/origin/develop e a conferência de versão usa a base certa.
M14: `bin/forge-check` +1 -1 e `tests/test_forge.py` +10, 12 linhas. Um comportamento só; abaixo do teto de 150.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E4 / C4 | FerramentaDefasadaNoForge.test_base_com_prefixo_origin_e_conferida_como_a_sem_prefixo | prefixo único aceito; origin/origin/develop, ../x, -c e develop..main seguem "não conferida", sem Traceback | passou |
| regressão do aviso de versão | FerramentaDefasadaNoForge (12 testes) | caminho sem prefixo intacto | passou |

## Cenários e resultado real
- `FerramentaDefasadaNoForge` na worktree: 12 testes, OK.
- `forge-testes --vermelho 234dbe0`: rc 0; contagem: não prova (passa na base)=1612; prova (asserção)=1; pulado=26; nenhuma regressão. Os pulados são do corpus de lançadores, iguais na base.
- Mutação à mão em cópia descartável (não há spec em tests/mutantes/ para o pedido, e o diff não muda hook, catraca nem guarda de script): (M3) remover o `removeprefix`: 1 falha. Morreu.
- Bordas (prefixo duplo, caminho relativo, opção, intervalo) cobertas no subTest do teste novo.

## Parecer
Aprovado: a entrega faz o que o item pede, o teste falha na base e passa no HEAD, e o mutante da linha de guarda morre.
