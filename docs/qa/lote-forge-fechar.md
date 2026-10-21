---
tipo: qa
contrato: 1
pedido: lote-forge-fechar
branch: melhoria/lote-forge-fechar
commit: 468f6c3f54645024be19a39a6262bf3156734bf6
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-21
---
# QA: lote-forge-fechar

Código testado: 468f6c3 (HEAD da branch 02f269d só acrescenta o parecer de review). Obrigações: o escopo E1 do pedido (log endurecido C1, número das execuções C2, limpeza com `--limpar` e código 3 C3) e as regras `R-FLUXO`, `R-MAIN`, `R-VERIFY`, `R-QA`. O pedido não traz `CA-n`; cada item do escopo vira uma obrigação.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1 log em arquivo, 600, pasta 700 própria, máscara de segredo, `fim: código n` | `test_l1_*`, `test_l2_*`, `test_l3_*`, `test_l5_*`, `test_l6_*`; sonda S-4 | link simbólico, modo, prosa com "token" | passou |
| C2 run e job de cada check, head e commit do merge no log | `test_c2_*`; sonda S-4 | URL sem padrão (`run=?`), check vermelho sem resumo | passou |
| C3 limpeza total, código 0 | `test_fluxo_completo_*`, `test_c3_ordem_*`; sonda S-1 | ordem worktree, branch, remota | passou |
| C3 limpeza pendente, código 3 e `--limpar` depois | `test_c3_ebusy_*`, `test_c3_worktree_suja_*`, `test_c3_limpar_com_prova_*`; sonda S-2 | EBUSY, worktree suja, repetir sem efeito colateral | passou |
| C3 branch com commit além do mesclado não é apagada (local e remota) | `test_c3_branch_com_commit_alem_*`, `test_c3_branch_remota_com_commit_alem_*`; sonda S-3 | sha diferente do head mesclado | passou |
| `--limpar` só com prova de PR MERGED na `develop`; `main`/`develop`/`homolog` recusadas (`R-FLUXO`, `R-MAIN`) | `test_c3_limpar_sem_prova_*`, `test_c3_limpar_continua_recusando_*` | PR aberto, mesclado na `main`, sem `gh` | passou |
| Sem força nem `--no-verify` (`R-VERIFY`) | `test_script_nunca_usa_force_no_verify_nem_rotulo` | n/a | passou |

## Cenários e resultado real
- Suíte completa: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q`: 1337 testes, OK (348 s).
- `scripts/validar-plugin.sh`: Validation passed.
- Sondas em `$TMPDIR`, repositório local, `gh` e `forge-check` dublês, sem rede (as negações de rede na saída são do sandbox, não do script):
  - S-1 merge com limpeza total: código 0, `limpeza: remota=ok worktree=ok branch=ok`, log termina em `fim: código 0`.
  - S-2 EBUSY com diretório de pé: código 3, comandos de limpeza impressos, `--limpar` com prova de PR MERGED termina em 0 e repete sem chamar git de novo.
  - S-3 commit além do mesclado: local e remota ficam, código 3, nenhum `branch -D` nem `push --delete`.
  - S-4 log: arquivo 600 em pasta 700, `check bateria pass run=9 job=8`, `head:`, `fim: código 0`.
  - S-5 worktree com commit novo e arquivo não versionado: código 3, worktree e arquivo preservados.
- Vermelho antes do verde: o review registra o teste da remota (R3 da segurança) visto falhando sem a correção; não repeti, o código de produção não mudou desde.
- Mutação: sem ferramenta gratuita para shell em `stacks/`; os testes de controle (sha, prova de MERGED, ordem) quebram se a condição sumir, conforme os nomes acima.
- Aberto, não bloqueante: R1 da segurança (a worktree limpa é removida antes de conferir o sha da branch; arquivo ignorado pelo git se perde) e as duas recomendações do review (`substr($0, 10)` no awk de worktree com espaço; linha sobre base local sem `git fetch`). `shellcheck` fica com o CI do PR.
