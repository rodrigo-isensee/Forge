---
tipo: revisao-devops
contrato: 1
pedido: ci-ferramenta-antes
branch: melhoria/ci-ferramenta-antes
commit: 07bfbe856be86649836f0bdce50cb83874a6e2c5
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-21
---
# Review de devops: ci-ferramenta-antes

## Parecer
Aprovado. A entrega mexe só no job `bateria` de `.github/workflows/ci.yml` (mais teste e fragmento de changelog). Nenhum bloqueante.

Checklist da skill `ci-cd` sobre o diff:
- Permissões, SHAs das ações, `concurrency` e `timeout-minutes` não mudaram; nenhum passo novo de terceiros; nenhuma interpolação nova de entrada não confiável em `run:`.
- Testes iguais e obrigatórios: `Testes do Forge` mantém o mesmo comando e o mesmo `if`; nenhum `continue-on-error`, `[skip ci]` ou passo removido (`R-VERIFY`). Todos os passos movidos conservam `!cancelled()`, então uma falha barata não esconde os demais.
- Segunda tentativa: `instalar || { ...; sleep 5; instalar; }`. Se as duas falharem o passo falha (o shell do Actions usa `-e`), e `claude --version` confere a versão fixa. Não deixa passar vermelho.
- Custo (`R-CUSTO`): zero novo; no pior caso soma 5 s mais uma instalação npm. A ordem não muda minutos em corrida verde.
- Teste novo (`test_bateria_ferramenta_e_checagens_baratas_antes_dos_testes`) cobre ordem, `claude --version`, ausência de `continue-on-error`/`skip ci` e testes sem `||`.

Avisos do conferente:
1. Mudança de ordem de shellcheck, actionlint, zizmor e e2e para depois dos testes: aceito, sem perda de cobertura (todos continuam obrigatórios e com `!cancelled()`). Foi além do Entregar, e o item 7 do checklist (barato antes do caro) pede o contrário para esses três.
2. Nova tentativa em qualquer falha, não só de rede: aceito. O pedido diz "por falha de rede", mas o npm não distingue a causa de forma simples, e a falha persistente (por exemplo o postinstall bloqueado) continua reprovando na segunda tentativa, só com 5 s de atraso.

Recomendações (não bloqueiam):
- Em um próximo PR do CI, mover shellcheck, baixa/actionlint e zizmor para antes de `Testes do Forge`; só o e2e precisa ficar depois, por ser caro. Ganha feedback de lint em segundos.
- Ajustar o texto do nome do passo ou do pedido para "qualquer falha de instalação", para o nome não prometer distinção de rede.

Ferramentas: `actionlint`, `shellcheck` e `zizmor` não estão no PATH deste ambiente (lacuna registrada); a revisão foi por leitura do diff. A conferência fica com o CI da bateria no PR.
Mudança em `.github/` exige o rótulo `afrouxa-regra` do dono no PR; avisar o `tech-lead`.

## Achados

## Custo e rollback
Sem custo novo (`R-CUSTO`). Rollback: reverter o commit (reordena os passos de volta); sem estado nem migração.
