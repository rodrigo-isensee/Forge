---
tipo: review
contrato: 1
pedido: release-0.47.5
branch: melhoria/v0475-pareceres-release
commit: fc3f2ed87165a80bb10aef78bd525abd7f53e629
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: release-0.47.5

Code review da versão 0.47.5 inteira no commit da develop fc3f2ed8 (#658), para a promoção à homolog (v0474 E4.30). Substitui o parecer anterior deste arquivo, no head 74d6ccd9 (outro repositório, antes do MP2/MP4), que a promoção recusa por commit inexistente aqui; o escopo dele e o da revalidação em `docs/reviews/release-0.47.5-b.md` (bc538cd3, outro repositório) entram juntos abaixo.

## Sondas

## Achados

## Parecer
Aprovado.

- Leva: `git log --first-parent v0.47.4..fc3f2ed8` traz 16 entradas: as 13 da marca original (#642, #644 a #654, #656, cada uma com os pareceres próprios na develop; #644 e #646 com o rótulo de regra afrouxada no título), o #655 (31b29052, MP2/MP4), a marca #657 (561ec804) e a junção #658 (fc3f2ed8).
- MP2/MP4 (#655): `git diff 95a01e54 31b29052` toca 32 arquivos (+1355/-49: `hooks/_maquina.py`, `hooks/pesado.py`, `bin/forge-status`, `bin/forge-pesado`, `bin/forge-testes`, hooks.json, conformidade, fixtures, mutantes e testes). Revisado e aprovado no PR 655 (review e QA em 4bb3b48, segurança em d7ad2a42, `docs/*/v0476-mp2-mp4.md`), com a árvore mesclada igual à do head do PR, conforme `release-0.47.5-b.md`; não refeito aqui.
- Marca: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.5"` (lido em fc3f2ed8); `CHANGELOG.md` com `[Não publicado]` vazio (linha 5) e `[0.47.5] - 2026-11-18` (linha 7) acima de `[0.47.4]`.
- Junção (#658, `git diff 561ec804 fc3f2ed8`): 8 arquivos; fora de pareceres, só `CHANGELOG.md` +1 e a remoção de `changelog.d/v0476-mp2-mp4.md`. A linha do MP2/MP4 aparece uma vez no `CHANGELOG.md` (`grep -cF 'Registro da máquina e fila pesada única'`: 1). `changelog.d/` só traz o `README.md`; `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes".
- CI: PR 658 `MERGED` (head ae88bbe5), 20 checks `SUCCESS`; o `catraca` `CANCELLED` (06:46:04Z) é a execução substituída pela seguinte, `SUCCESS` (06:46:25Z); os `SKIPPED` são os jobs de push na develop. O CI do push em fc3f2ed8 estava `in_progress` na leitura; a promoção o confere.
- Testes: `tests/test_changelog.py` em fc3f2ed8 (discover, `-I`): 89 testes, OK. A suíte inteira fica no CI (`R-REVIEW`), não rerrodada aqui.
- Promoção: `scripts/promover-homolog.py --conferir-ref fc3f2ed8...` antes deste commit listava este arquivo, `docs/qa/release-0.47.5.md` e `docs/security/release-0.47.5.md` com "commit não existe no repositório"; os dois últimos são de QA e segurança, não deste parecer.
