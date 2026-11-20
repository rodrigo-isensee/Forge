---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-forge-check-ci-verde
commit: 0b2e8d6f8ca3671cdba187ec985a5b15afe65b0b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 (E47.4, PARECER-SO-COM-CI-VERDE e META85-FC-RESTOS)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Aprovado só conta com CI verde no head (PR no mesmo head, todo check em pass/skipping, exigidos presentes) | `test_forge_check_pr.CiVerdeNoHead` | pendente, vermelho, ausente, outro head, sem rede, nenhum check: falha fechada | passa (M1-M3, M21 mortos) |
| Ou com a linha `- suíte: <sha40> rc=0 módulos=...` cobrindo os módulos de teste do diff | `test_forge_check_pr` (prova da suíte) | sha curto/outro, rc≠0, módulo faltando, base ilegível | passa (M4-M17 mortos) |
| `--previo` e passo 1 do fechar só avisam; fora do Forge nada | `test_forge_check_pr` (adiar) | previo; não-Forge | passa (M18-M20 mortos) |
| `parecer novo` traz a linha da prova e o caminho `<pasta>/<slug>.md` | `test_aq5_parecer_novo`, `test_forge_check_pr` | slug inseguro cai em `<pedido>.md` | passa (M22-M24 mortos) |
| Brief de merge-integracao manda juntar só `origin/<base>` | `test_forge.LerDirigidoDoBrief` | base remota, não a local | passa |
| Teto de arquivos com `python3 -I` e ambiente limpo; Jarvis passo 5 só com `revalida: sim` | `test_meta85_item_arquivos`, `test_jarvis_nucleo` | n/a | passa |

## Cenários e resultado real
Máquina com carga e sem suíte local, por ordem do brief. Rodados só os módulos tocados, com TMPDIR:
- `test_forge_check_pr` 45 OK; `test_aq5_parecer_novo` 8 OK; `test_meta85_item_arquivos` 6 OK; `test_jarvis_nucleo` 43 OK; `test_forge -k LerDirigidoDoBrief` 2 OK. O `test_forge.py` inteiro não foi rodado aqui (fica para o CI do PR, ainda sem PR no head; por isso não gravei a linha `- suíte:`).
- Vermelho antes do verde: `bin/forge-check` da base 004ce869 sobre a árvore do head: `test_forge_check_pr` Ran 45, FAILED (failures=2, errors=16); `test_aq5_parecer_novo` Ran 8, FAILED (failures=1). `forge-testes --vermelho` estourou o prazo de 400 s (rc=143, sem veredito; carga), então a prova foi por substituição manual em cópia em `$TMPDIR`.
- Mutação: `bin/forge-mutante` nas 4 specs (`--processos 2`): rc=0, M1 a M24 todos `morreu`, nenhum sobrevivente, nenhum equivalente.
- `forge-mutante --cobertura --base 004ce869`: toda condição mudada de `bin/forge-check` sai `coberta` por mutante declarado; nenhuma `não coberto`.
- Revisão do diff: `ci_verde_no_head` falha fechada (sem branch, head, PR, checks); `checks_ruins` é a mesma fonte do `checks_do_head`, sem divergência.
