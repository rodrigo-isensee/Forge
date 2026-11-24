---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-branches-paradas-a1
commit: 135689e492fc45806fb49b12120f79966aae4420
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E149.4, pareceres pós-merge das branches paradas pelo blob)

Classe T, só documentação. Diff `206303511c93..135689e4`: 5 pareceres (2 novos, 3 substituindo a versão da develop) e 2 fragmentos de changelog. PR #836, em rascunho.

## Achados
- A1 (bloqueante) changelog.d/v0480-branches-paradas-a1.md:2 · fragmento extra repete a mudança que changelog.d/v0480-branches-paradas.md:3 já registra (os 3 de QA pelo blob) e omite os 2 de segurança; a release junta duas linhas sobre o mesmo PR. Apagar o fragmento: o conferir passa sem ele (PR só de parecer).

## Parecer
Reprovado só pelo A1; o resto está aprovado.

**Pareceres pelo blob.** Os cinco arquivos são iguais ao blob da branch de origem (`git diff --stat origin/<branch> HEAD -- <arquivo>` vazio): `forge-pesado-m12` (bfbd2592), `v047-h4-atualiza-branch` (5dcab8df), `v0479-conformidade-sessao-forge` (2b3aa8cc), `v0476-mp2-mp4` (5895657f) e `v0474-pos-merge-631` (70d87299).

**Substituições, nenhuma perde parecer mais novo.** Em cada uma, o commit da branch de origem é posterior ao último da develop no arquivo, e o `commit:` novo é o código do head que o PR mesclou (só commits de parecer depois dele):
- `docs/qa/v047-h4-atualiza-branch.md`: develop em a698d0ee (#633, cita 80679f19); origem 5dcab8df cita ecc07992, ancestral do head 78170196 do #633, com diff só em `docs/reviews` e `docs/security`.
- `docs/qa/v0479-conformidade-sessao-forge.md`: develop em d4f0b10a (#742, cita 96c0215f); origem 2b3aa8cc cita 6aa5b7be, ancestral do head c14b1a14 do #742, diff só em pareceres.
- `docs/security/v0476-mp2-mp4.md`: develop em 31b29052 (#655, cita d7ad2a42); origem 5895657f cita 4bb3b48e, ancestral do head 6889c028 do #655, diff só em pareceres.

**Fragmentos.** A edição de `changelog.d/v0480-branches-paradas.md` confere: 2 de review pelo #807 (8d94b175), 3 de QA e 2 de segurança, 7 pareceres em 6 branches. O fragmento novo `-a1` não é exigido: `bin/forge-changelog conferir` (linhas 363-365) aceita PR cujos arquivos da fábrica são só pareceres, e `changelog.d/` não está em `CAMINHOS_DA_FABRICA` (linha 29). Com ele, a mesma mudança sai duas vezes na release e a segunda linha fala só de QA (A1).

**Ferramentas.** `bin/forge-check docs`: verde. `bin/forge-changelog conferir --base origin/develop`: rc 0. Sem código, sem teste nem mutante a rodar; suíte inteira só no CI do PR #836.

**Corpo do PR.** O corpo pronto do QA citava só os 3 pareceres de QA; abri o #836 com o corpo completo (os 5 pareceres e as 3 substituições conferidas).

**Volta.** Basta um commit que apague `changelog.d/v0480-branches-paradas-a1.md`; a revalidação lê só esse delta.
