---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-0-ameacas
commit: 68fb5f6ffbb257cad65515cfa8697597e984f5ee
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E6.12, PR #876, modelo de ameaças do G2; classe T), revalidação por delta

Lido: só `git diff bfd788ef..68fb5f6f` (volta E6.10), em `docs/security/ameacas/g2-parecer-status.md`; o outro arquivo do delta é o meu parecer anterior (reprovado em bfd788ef, A1 bloqueante, A2 a A4 recomendados). Delta pela ferramenta: `forge-check parecer delta` dá intervalo `bfd788ef..68fb5f6f`, "nenhum arquivo do domínio mudou" (o domínio dele é código e testes; o delta é só documentação) e "revalida: sim (este parecer barrou)". Classe T, só documentação: o review é o único portão; a suíte é do CI do PR, sem rerrodar aqui (R-REVIEW).

## Parecer
Aprovado. Os quatro achados anteriores estão resolvidos no head 68fb5f6f.

- A1 (bloqueante), resolvido em :72 (M4.1) e na emenda E-3 (:160): o registro vai para `pareceres-publicados.jsonl` numa pasta de controle única por máquina (no Forge `~/.forge-contrib/.forge/run/`; no projeto, o `.forge/run/` da cópia que contém `.forge/wt/`), achada por uma função só da ferramenta confiável, sem seguir link e falhando fechada; o texto diz por que não serve o `.forge/run/` do clone. Conferido: `RAIZES_DE_BRIEF` em `bin/forge-check:3940` é `Path.home() / ".forge-contrib"`, `raiz_principal` em `:2340` devolve o próprio clone quando o `.git` não é de worktree (a sonda S1 do parecer anterior), `hooks/conformidade.json:38` protege só o `.forge/run/` da raiz do repositório (por isso a regra nova no G2.1, como o texto diz), e `.forge/wt/<item>` é a pasta dos clones do projeto (`skills/trabalho-em-paralelo/ritmo-e-corte.md:43`). C5 (:136) ganhou os dois casos novos (registro só no clone; pasta trocada por link), o corpus de legítimos (:156) ganhou o publicado num clone e lido noutro, e a seção 3 nomeia os quatro testes, em G2.1 e G2.2.
- A2, resolvido em :105: M3.2 cita `tests/test_pr_hook_rapido.py` com `test_reprovado_do_mesmo_head_recusa_so_lendo` (:58) e `test_aprovado_forjado_nao_libera_o_merge_s3` (:137), que existem, e um teste novo nomeado para o G2.2.
- A3, resolvido em :74: M10.2 saiu; a condição foi para M10.1 (extração e lista de M1.4 só de `refs/remotes/origin/develop` igual ao `git ls-remote`, senão falha fechada), e a seção 3 (:116) e C12 (:143) acompanham.
- A4, resolvido em :10-11: C22 na linha de R2 e C23 na de R3; M10.2 também saiu da linha de R3.

Nada novo no delta: as linhas citadas batem com o código do Base-sha e o texto não cria regra nova além do que a ADR 0019 e a emenda E-3 já tratam.
