---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-release-0475b
commit: bc538cd3e72db368f73681ed9031c9ce4d5c7063
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: release 0.47.5 com o MP2/MP4 (v0474 E4.26)

Revalidação por delta da release 0.47.5 no head bc538cd3 (E4.26). O código revisado da release foi o head 74d6ccd9 (outro repositório; parecer aprovado em `docs/reviews/release-0.47.5.md`), squash na develop como 561ec804 (#657) sobre 31b29052 (#655, MP2/MP4). Esta branch nasce de 561ec804 (Base-sha) e traz um commit só.

## Achados

## Sondas

## Parecer
Aprovado.

- Delta da branch (`git diff 561ec804..bc538cd3`): `CHANGELOG.md` +1 e a remoção de `changelog.d/v0476-mp2-mp4.md`; nada de código. A linha `- Registro da máquina e fila pesada única (MP2, MP4): ...` é idêntica à do fragmento apagado, está na seção do tipo dele (`### Adicionado` da `[0.47.5] - 2026-11-18`) e aparece uma vez no arquivo (`grep -cF`: 1). `[Não publicado]` segue vazio e `changelog.d/` só traz o `README.md` (`bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes").
- A 0.47.5 inclui o MP2/MP4 (`git diff 95a01e54..bc538cd3`): além da marca, o intervalo traz o #655 (31b29052; `hooks/_maquina.py`, `hooks/pesado.py`, `bin/forge-status`, `bin/forge-pesado`, `bin/forge-testes`, hooks.json, conformidade, fixtures, mutantes e testes). A árvore de 31b29052 é a mesma do head do PR 655 (6889c028, `rev-parse ^{tree}` igual: 84b72f3d), que tem review e QA aprovados em 4bb3b48 (o delta 4bb3b48..6889c028 é só os dois pareceres) e segurança aprovada em d7ad2a42 (`docs/*/v0476-mp2-mp4.md`); o PR 655 e o 657 estão `MERGED`.
- Marca da versão inalterada: `git diff 31b29052 561ec804` fora de `docs/`, `CHANGELOG.md` e `changelog.d/` toca só `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` (0.47.4 → 0.47.5), iguais ao título da entrada.
- Testes: `tests/test_changelog.py` no head (discover, `-I`): 89 testes, OK. A suíte inteira fica no CI (`R-REVIEW`); a local falha por ambiente (sandbox: `/proc` e `gh`); sem PR nesta etapa, por decisão do brief.
- Observação, sem achado: o parecer de segurança do #655 está em d7ad2a42 e o head mesclado mudou depois em `bin/forge-testes` e três testes (19+/9-, mapa de módulos e testes de hooks); o merge passou pelo `forge-check pr` do `forge-fechar`, e a validade por domínio é da segurança (`R-REVIEW`), não refeita aqui.
