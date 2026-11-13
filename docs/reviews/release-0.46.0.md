---
tipo: review
contrato: 1
pedido: release-0.46.0
branch: melhoria/release-0.46.0
commit: 2e45133689fbddb381d134637cc1e5c6569e8b75
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: release 0.46.0 (develop em 2e451336 contra a main)

Pedido v0457, etapa E23.82. Leva: `git log origin/main..2e451336` com 327 commits, 29 na primeira mãe; `git diff --stat origin/main..2e451336` mostra 485 arquivos, +23937 -1873. Main em `4099658f`.

## Achados
- A1 (recomendado) skills/falar-com-o-dono/SKILL.md:12 · o #492 (E18.3, develop-verde-491) entrou na develop sem pareceres da classe próprios (o corpo do PR diz "Faltam os pareceres") e sem o rótulo afrouxa-regra; li o diff aqui: conteúdo certo, a lista segue protegida em R-DECISAO
- A2 (recomendado) docs/reviews/v046-forge-pesado-m12.md:4 · o #499 foi mesclado antes do QA; o parecer de QA aprovado no cdfafd25 existe (bfbd2592), mas só na branch melhoria/forge-pesado-m12, fora da árvore da release
- A3 (recomendado) CHANGELOG.md:7 · risco aceito pelo dono: #506, #507 e #508 mesclados com CI vermelho e o #507 reprovado na segurança (A11) e no QA (A4), decisão de 12/11 17:05 e ordem de 17:25; corrigidos depois pelos #509 a #513

## Sondas

## Parecer
Aprovado no `2e451336`. A leva pode subir à homolog. Os três achados são recomendados: nenhum aponta defeito no código que vai para a main, e o A3 é um risco que o dono já aceitou.

**Todo commit veio por PR.** Os 29 commits da primeira mãe em `origin/main..2e451336` são todos squash `(#n)` ou `Merge pull request #n`. O filtro que acha linha fora desses dois formatos não achou nenhuma. Os #478, #482 e #486 são a main trazida de volta à develop.

**Pareceres na árvore.** Foram adicionados ou mudados na leva 63 pareceres em `docs/{reviews,qa,security,devops}/` (o `_modelo` fica fora), e os 63 estão com `parecer: aprovado`; são os mesmos que o `scripts/promover-homolog.py` lê. Liguei cada PR mesclado (do #488 ao #513, `gh pr view`) aos pareceres pelo campo `branch:`:
- 22 dos 26 têm o parecer da própria branch na árvore.
- O #488 e o #490 usaram o parecer por pedido (`docs/*/v0457.md` e `docs/*/v046.md`), que PRs seguintes sobrescreveram. No commit do merge (`e6e47681` e `ed021b71`), os três pareceres de cada um estavam aprovados no head do PR.
- O #492 não tinha parecer próprio (A1). Li o diff dele (5 arquivos, +7 -5), e o conteúdo está certo. As duas skills trocam a lista copiada pela citação de `R-DECISAO`. A lista continua inteira na fonte (`docs/regras/R-DECISAO.md:26`) e protegida em `tests/config.json:562`.
- O #499 não tem o QA na árvore (A2).
- Para o #507, o parecer de segurança foi reprovado no merge. O mesmo arquivo foi aprovado depois no `abfccb7e` do #512, que fecha o A11, pela decisão do dono de 12/11 18:20.

**CHANGELOG e versão.** `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3` estão em `0.46.0`, e a `marketplace.json` não leva versão. `CHANGELOG.md:7` traz `## [0.46.0] - 2026-11-12`, com Adicionado, Alterado e Corrigido, e `## [Não publicado]` está vazio. O `changelog.d/` só tem o README, portanto não sobrou fragmento fora da entrada. A entrada descreve a leva: envio leve, RITMO, R-LIMITES, F6, forge-pesado e o hook pesado, PREPUSH-REFS, as voltas da conformidade (#507 e #512), os pesos (#510) e os afrouxamentos listados com destaque.

**Risco aceito (A3).** Os #506, #507 e #508 foram mesclados com CI vermelho. O dono disse "foi consciente, mas faça as correções" (DECISÃO DO DONO de 12/11 17:05) e mandou corrigir a develop vermelha por PR (ORDEM DO DONO de 12/11 17:25). As correções já estão na leva: os #509 e #511 juntam os fragmentos, o #510 traz os pesos da suíte, e os #512 e #513 fecham a brecha A11 com a nota dela.

**Testes:** não rodei nenhum. Este review não traz diff de código, só o parecer (`.md`), e por isso o teto M14 conta zero linhas. A suíte da leva fica com o CI do PR de promoção.
