---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/release-0.47.0
commit: 72bb40084ec4b32d979dbbd8ba7379934aa5d055
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: release 0.47.0 (v047, E2.10)

Head revisado 72bb4008 (classe C: CHANGELOG e placar), instância que não fez a entrega. Revisão por delta da marca 51c51139 até 72bb4008.

## Achados
- A1 (recomendado) tests/mutantes/v0457-escopo-ponto-2.json:M10 · atualizar o M10 (guarda movida pelo PR 536) para a próxima release não repetir o inválido; segue da review anterior, não bloqueia

## Sondas

## Parecer
Aprovado. O achado A1 bloqueante da review anterior (placar) está resolvido.

- Delta lido (`forge-check parecer delta`): CHANGELOG.md, docs/engineering/placar-mutacao.md e o fragmento `changelog.d/v047-teste-carga.md` (junção do PR 540 vinda da develop).
- Placar: a linha gravada é `placar: 0.47.0 mortos=62 sobreviveu=0 equivalente=0 invalido=1 sem-veredito=0 specs=9`, igual à que a review anterior mediu no head (62 mortos, 1 inválido, 9 specs), com a nota do M10 explicando o inválido (spec `v0457-escopo-ponto-2`, guarda movida pelo PR 536). Medida, não portão.
- CHANGELOG: o fragmento apagado (2 linhas, 1 entrada) aparece uma vez em `## [0.47.0]` / `### Corrigido`; `changelog.d/` fica só com o README; sem perda.
- Versão e plugin.json: sem mudança no delta (já 0.47.0 na review anterior).
- Testes: `tests.test_changelog` OK (74 testes); `forge-check docs` sem erro. A suíte inteira fica no CI; máquina com carga 24, só o afetado rodou.
