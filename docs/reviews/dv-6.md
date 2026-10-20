---
tipo: review
contrato: 1
pedido: dv-6
branch: melhoria/dv-6
commit: e316b0b1665442f203bde8489531ca125594836f
parecer: aprovado
revisor: forge:tech-lead (outra instância)
data: 2026-10-19
---
# Review da DV-6: `forge-changelog conferir` aceita o PR que só fecha fragmentos

Escopo: `git diff e9c81e0..e316b0b` (bin/forge-changelog, tests/test_changelog.py, changelog.d/dv-6.md).

## O que conferi
- E1: o fechamento (sem versão nova, sem fragmento novo, mudanças só em fragmentos apagados, CHANGELOG.md e pareceres de docs/reviews, qa, security, devops) passa só se cada linha de cada fragmento apagado estiver no CHANGELOG.md do HEAD; senão sai com erro citando fragmento e linha. Confere.
- Não afrouxa: fragmento novo junto, ou qualquer outra mudança da fábrica (ex.: docs/regras), cai no caminho antigo e exige fragmento novo. Antes, o fechamento sem pareceres passava sem checar linha alguma; agora é checado. PR de release e PR sem mudança na fábrica seguem iguais.
- Testes (29 em tests/test_changelog.py, OK): os 3 casos (fechar com linhas passa; sem a linha reprova; fechar com outra mudança exige fragmento novo) e os 2 da volta (parecer em docs/reviews passa; docs/regras exige fragmento). Cobrem o comportamento e a borda.
- Fragmento changelog.d/dv-6.md no formato; sem custo (R-CUSTO), sem termo de projeto (R-NEUTRO). Regras "ferramenta" do projeto: sem saída a citar neste diff.

## Achados
- A1 (recomendado): a conferência é por substring no CHANGELOG.md inteiro; uma linha curta presente em outra seção ou versão antiga passaria. Aceitável agora (mais estrita que antes); exigir a linha sob `## [Não publicado]` ou comparar por linha inteira endureceria depois.
