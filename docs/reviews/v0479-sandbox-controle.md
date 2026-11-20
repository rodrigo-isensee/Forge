---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sandbox-controle
commit: 32c3528eaa65c8c85367465c506856befdd33818
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E29.18, revalidação da A3 de SANDBOX-TRAVA-CONTROLE, head 32c3528e)

Revalidação (H3, R-REVIEW): li só `forge-check parecer delta docs/reviews/v0479-sandbox-controle.md`, intervalo `64fca890..32c3528e`. A ferramenta avisou que o merge `f493e002` não está na `origin/develop` e por isso contou inteiro o que ele trouxe. Esse merge é da própria branch (`origin/melhoria/v0479-sandbox-controle`) e só traz pareceres. Por isso `bin/forge-testes`, `hooks/_comum.py` e `docs/hooks.md` aparecem no domínio, mas vieram da `develop` pelo `32c3528e`. Eu os separei com `git diff --stat 64fca890 0eedfdea` (código: só `.claude/settings.json`) e `git show --remerge-diff 32c3528e` (um único conflito resolvido, em `hooks/agentes.py`). A suíte inteira não rodou aqui, fica no CI do PR #713. Rodei os testes do item com o ambiente limpo, `python3 -m unittest tests.test_sandbox_controle tests.test_hooks_agentes_autor`: `Ran 24 tests ... OK (skipped=2)`, os dois do bubblewrap pulados aqui. O delta não muda nenhuma guarda, então não há mutante novo a declarar.

Delta lido:
- `.claude/settings.json` (`0eedfdea`): o `denyWrite` ganha `.git/forge/run` e `~/.forge/maquina`. É idêntico ao patch de `docs/devops/v0479-sandbox-controle.md:25-29` e só aperta o controle. Foi aplicado pelo dono e está coberto pela DECISÃO DO DONO de 2026-11-19 08:28 (OK do rótulo `afrouxa-regra` só neste PR). O mérito da sandbox é do parecer do devops.
- `hooks/agentes.py:71-72` (`32c3528e`): o conflito do import foi resolvido pela união `ler_trava, mensagem, raiz_declarada`. Os dois nomes são usados: `raiz_declarada` em `:164`, vindo da `develop`, e `ler_trava` em `:494`, vindo da A3. O arquivo compila. Fora essa linha, o merge não muda nada além das duas pontas.
- `docs/devops/v0479-sandbox-controle.md`: fora do meu domínio (parecer do devops).

## Parecer
Aprovado. O patch aplicado pelo dono bate com o que foi revisado, e a resolução do conflito apenas une os dois imports, sem mudar comportamento.
