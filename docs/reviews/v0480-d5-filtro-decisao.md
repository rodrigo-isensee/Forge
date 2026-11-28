---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d5-filtro-decisao
commit: 8916a422b5b7b811f858847881a686e7f3108f19
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E173.19, D5, PR #863, volta E173.12)

## Achados
- A1 (recomendado) skills/falar-com-o-dono/SKILL.md:1 · Segue o A3 do 6c4a7dcc: a skill não cita `--tipo-pergunta` nem os 7 tipos, e o R-DECISAO não cita `--so-aperta`/`--seguranca` nem a linha `Só aperta: <porta>`. Vira cartão depois do merge.

## Parecer
Aprovado. Revalidação por delta: li `forge-check parecer delta docs/reviews/v0480-d5-filtro-decisao.md` (revalida: sim, o parecer anterior barrou) e o diff 6c4a7dcc..8916a422 em `bin/forge_decisor.py`, nos testes e nos mutantes.

- A1 anterior (bloqueante) resolvido: `confirmacao_escrita(raiz, caminho, pedido, porta)` lê o parecer pelo git no HEAD (`parecer_no_git`: raiz igual ao `--show-toplevel`, modo 100644, até 1 MiB, sem diferença no índice nem na árvore), exige o frontmatter `tipo: revisao-seguranca`, `parecer: aprovado`, `revisor: forge:security-engineer` e `pedido:` igual ao `--pedido`, e uma linha inteira `Só aperta: <porta>` com a porta registrada (espaços normalizados por `_campo`, dos dois lados). A S1 da volta anterior virou caso: `test_parecer_de_outro_item_ja_na_develop_vira_pergunta` usa `heredoc-donos.md` e `release-0.47.15.md` reais.
- A2 anterior (recomendado) resolvido: a busca solta saiu; a `fullmatch` por linha recusa negação, pergunta, recuo e minúscula (`test_frase_solta_pergunta_ou_negacao_vira_pergunta`, inclui a S2).
- Falha fechada: frontmatter sem abertura, sem fechamento, com linha fora de `chave: valor` ou chave repetida devolve `None`; `_git` limpa as `GIT_*` herdadas e devolve `(1, b"")` sem o git. O teste de subprocesso usa `-I` e `sem_git_herdado`.

Tamanho (H1): `bin/` soma 114 linhas acrescidas desde a base 8a6f5907 (forge_decisor 78, forge_dono 22, forge-check 14), dentro do teto. Guardas novas com um mutante cada (D5M18 a D5M22 na spec principal, D5M23 a D5M28 na `-4`); rodei a `-4` aqui: 6 de 6 mortos no 8916a422. As guardas trocadas (D5M2 a D5M5 antigos) saíram com o código que guardavam.

Suíte: no CI do 8916a422 as 10 partes da suíte (3.12 e 3.14), a instalação e o teto de pulados estão verdes; `bateria`, `bateria (pareceres)` e `catraca` falham, como se espera com os pareceres desta volta pendentes. Rodei só os testes tocados: `tests.test_decisor`, `tests.test_forge_dono.SoApertaComSeguranca` e `tests.test_forge_dono.FiltroDaPergunta`, 35 testes OK.
