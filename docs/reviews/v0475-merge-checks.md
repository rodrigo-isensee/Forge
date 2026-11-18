---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: cc4934ded283fd19b3d614f7981431db61713739
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.193, branch melhoria/v0475-merge-checks)

## Achados
- A3 (recomendado) tests/test_forge_check_pr.py:1 · M14: agora são 492 linhas de código e teste sobre origin/develop (141 em bin/). O `teto:` do corpo do PR #653 ainda diz 476; atualize o número.

## Revalidação
Li o delta com `forge-check parecer delta docs/reviews/v0475-merge-checks.md`, no intervalo 27c4c567..cc4934de, só no domínio de código e testes.

O delta também traz o merge 881cf2cb da develop (f8e9c377): o mapa do `forge-testes`, `modelo_atras_do_plugin`, `branch_do_modelo_sem_pr` e `test_testes_tocados`. Esse merge está limpo: o `git merge-tree --write-tree` dos dois pais dá a mesma árvore, 794668c2. Por isso não revi esse trecho aqui.

O código do autor está só em cc4934de (E3.185), com 31 linhas a mais e 6 a menos.
- **bin/forge-check:1444.** `GH_SEM_PR` passa a incluir `"set the GH_TOKEN environment variable"`. É o texto que o gh mostra no GitHub Actions sem token, no lugar do "gh auth login". O casamento continua por trecho do stderr (bin/forge-check:1493), igual ao dos outros itens. Esse caso equivale ao "sem login" já aceito e não afrouxa a falha de rede, de teto ou de saída ilegível, que segue avisando e gravando reprovado.
- **tests/test_forge_check_pr.py:137.** O subteste usa a mensagem real do runner.
- **tests/test_pr_hook_prazo.py:55.** O `forge_check` dos testes põe à frente do PATH um `gh` falso que responde como o gh do runner (exit 4). O falso fica numa pasta irmã da raiz temporária. Com ele, o resultado gravado não depende da máquina nem da rede. O falso não é mais frouxo que o script (checklist 12): ele responde a qualquer subcomando com o mesmo erro do runner, e o script decide pelo stderr.
- **M31** (tests/mutantes/v0474-merge-checks-5.json) declara a guarda mudada, uma linha e um mutante.

## Verificação
- **Mutante M31:** apliquei-o à mão e restaurei o arquivo com `git checkout`. Os dois testes declarados falham com o mutante, e ele morre: `test_sem_pr_sem_remoto_do_github_ou_sem_gh_nao_marca` falha no subteste do GH_TOKEN, e `test_pr_aprovado_grava_e_o_hook_libera_so_lendo` também falha.
- **Testes do delta** (`tests.test_forge_check_pr`, `tests.test_pr_hook_prazo` e `tests.test_ambiente_git`): 66 testes OK.
- **Catraca** (`--base origin/develop`): nenhuma linha R-QA. O rc=1 vem só do aviso R-CONFORMIDADE de bin/forge-check, porque o rótulo `afrouxa-regra` tem de ser aplicado depois do último push.
- **PR #653:** head cc4934de, fora do rascunho, com o rótulo `afrouxa-regra`. O `gh pr checks` não mostra nenhum check, então ainda não há CI verde para citar. A suíte fica com o CI.

## Parecer
Aprovado no head cc4934de. Ficam pendentes:
- o CI verde do PR;
- a data do rótulo do dono em relação ao último push (R-CONFORMIDADE);
- o número no `teto:` (A3).
