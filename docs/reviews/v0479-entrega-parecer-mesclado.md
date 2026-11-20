---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: aebace7125b5873038e1c4ffefbb512cd7e111b2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E50.12 (ENTREGA-PARECER-MESCLADO, volta E50.11)

Revalidação pelo delta (`forge-check parecer delta`, intervalo `8cff35a0..aebace71`, com o merge do parecer reprovado a2a7505e; H3, `R-REVIEW`): hooks/conformidade.py, docs/hooks.md, changelog.d, tests/test_hooks.py, tests/test_selo_e_entrega.py, a fixture `pp-sessao-forge-outro-repo-dev-write-reviews-libera`, as 12 fixtures novas `pp-sessao-forge-wt-*` e as specs `v0478-guardas-conformidade`, `v0479-entrega-parecer-mesclado`, `-5` e `-6`. Código da volta: 19 linhas em hooks/conformidade.py, dentro do teto (H1). Rodadas anteriores: aprovado em 48153733 e cdf62e0a; reprovado em 8cff35a0 só por A1 (caminho pessoal na fixture).

## Sondas
- S1 · `scripts/verificar-contribuicao.sh 8a503799299d189c8c35eb8bcf4bf850d9f7d5a0` no head aebace71 · espera: `ok: nenhum segredo nem caminho pessoal` · obtido: `ok: nenhum segredo nem caminho pessoal no diff contra 8a503799...`

## Parecer
Aprovado no head aebace71.

A1 da rodada anterior resolvido: a fixture saiu de `{tmp}/home/outro` para `{tmp}/outro` (S1), sem mudar o que ela prova (repositório que não é do Forge segue livre).

E50.11 (A5 da segurança): `PARECER_NO_TEXTO` casa a pasta de parecer citada no texto com borda dos dois lados (o vizinho `docs/reviewsx/` fica fora, M30) e com `docs/security/aceites` antes de `docs/security` (M31). `parecer_alheio_no_texto` procura a entrada da própria pasta na política (a ordem de `conformidade.json` põe `aceites/` antes de `security/`, M32) e recusa só o papel que não é dono (M26, M27). Entra nos dois caminhos que faltavam: a construção que o hook não modela (`recusa_do_estado`, M25, com M4 e M5 de v0478 ajustados ao trecho novo) e a linha sem leitura ou erro interno em `prova_fora_de_projeto` (M28), em que só o erro interno vai ao registro (M29, M33). A1 do QA: `test_sem_conferida_o_parecer_com_commit_no_base_sha_segue_fora` mata o M1 na 1.a entrega. Os mínimos de `test_fixtures_do_parecer_pelo_papel` subiram para 13 liberam e 19 bloqueiam (checklist 11). docs/hooks.md e o fragmento acompanham.

Rodei com ambiente limpo: `ParecerMescladoNaVolta` (15) e `test_fixtures_do_parecer_pelo_papel` OK; `forge-mutante` M25 a M33, M4 e M5 de v0478 e M1 da spec 1 morreram; `--cobertura --base 8cff35a0` cobre toda guarda mudada e `--conferir` acusa os trechos no lugar. A suíte inteira fica com o CI do PR (`R-REVIEW`).
