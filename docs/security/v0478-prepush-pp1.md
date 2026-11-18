---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-prepush-pp1
commit: 3d4a84ffecfeaf5ae35c2107706eafdaff2f37b6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (patch PP1 do envio local, E14.8)

Revalidação no head 3d4a84ff, por delta desde 6c84adb4 (a rodada anterior está no git). Lido: `forge-check parecer delta docs/security/v0478-prepush-pp1.md`, no domínio `docs/devops/pp1-pre-push.patch` e `tests/test_pre_push_patch.py`; fora do domínio, só o trecho "Aplicar" de `docs/devops/pp1-aplicar.md`, para conferir o A1.

Gatilhos: controle do envio local (`.githooks/pre-push`, via patch), leitura de arquivo compartilhado entre processos (trava), execução de Python da árvore no hook.

## Conferido no delta

- **A1 da rodada anterior: resolvido.** `docs/devops/pp1-aplicar.md:20-23` fixa `SHA=0a986ebe`, extrai o patch com `git show "$SHA:docs/devops/pp1-pre-push.patch"` para `$TMPDIR`, roda `git apply --stat` (com a ordem de parar se listar outro arquivo além de `.githooks/pre-push`) e só então `--check` e `apply`. Conferido: o patch em 0a986ebe é idêntico byte a byte ao da árvore em 3d4a84ff (`cmp`) e não mudou entre 0a986ebe e 3d4a84ff; o `--stat` lista só `.githooks/pre-push` (119+, 3-) e o `--check` passa no head.
- **A2 da rodada anterior: resolvido.** patch:91 agora traz `[ ! -L bin/forge-check ]`, igual às guardas vizinhas. Teste: `test_forge_check_que_e_link_nao_roda_a_checagem` (com o link, a checagem não roda).
- **FILA-INTERVALO-ZERO, base dez** (patch:155-159). O `case` segue antes da conta, então `$((10#$intervalo))` só recebe dígitos; o valor decimal substitui `intervalo` e é o que `a_cada_intervalo` soma (`.githooks/pre-push:489`). Sonda: `08` deu 8; `0` e `00` recusados; `$(id)`, `10#1` e `a[$(id)]` recusados no `case`. Testes: `test_zeros_a_esquerda_em_base_dez_sao_aceitos` e `test_conta_da_espera_usa_o_valor_decimal`.
- **Testes novos dos mutantes M11 e M12** (pulos): só fixam o comportamento já revisado da conta da catraca; sem superfície nova.
- `tests.test_pre_push_patch` rodou isolado: 23 testes OK em 41 s. A suíte inteira fica para o CI do PR; esta etapa não abre PR e o brief pede o parecer sem suíte local.

## Riscos aceitos e ferramentas

Nenhum risco aceito. Ferramentas: leitura estática do delta, `git show`/`cmp`/`git apply --stat --check`, sonda local do intervalo e o módulo de teste isolado. Não estavam no PATH (lacuna): `gitleaks`, `shellcheck`, `semgrep`. O shellcheck do hook roda no CI quando o patch for aplicado.
