---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-visao-de-foco
commit: 7bbd973804f4813b47f47b43a894b4e18e9447dc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.338, desenho da visão de foco, E7.1)

Intervalo revisado: `1b88640e..6e99cc41` (Base-sha do brief = merge-base), 1 commit, 1 arquivo: `docs/arquitetura/visao-de-foco.md`, 178 linhas `.md`. Código e teste contados (M14): 0 linhas. Sem guarda nova nem mudada; sem mutante a declarar. Sem módulo de teste do item: a suíte fica no CI do PR; `forge-check docs` rc=0 no clone.

Conferido contra o código da base que o desenho cita (`4138445e`, ancestral do head): `scripts/jarvis:20,42`, `scripts/jarvis-forge:203-216`, `bin/forge-init:71-100`, `bin/forge-upgrade:111-122`, `hooks/meta.py:102-141`, `bin/forge_transcricao.py:301-367`, teto do núcleo 37.511 em `docs/regras/orcamento.json`: as referências batem. Escopo E7 e E7.1 cobertos (nome da opção, onde liga, onde não dá, texto do Jarvis, checagem de jargão). Checklist da fábrica: critério de reversão presente (seção final); "Por que o existente não basta" com evidência (5.1); não afrouxa controle (`R-CONFORMIDADE`), sem custo (`R-CUSTO`), nada de projeto (`R-NEUTRO`).

## Revalidação no head 7bbd9738 (E2.391)
Delta lido: `forge-check parecer delta docs/reviews/v047-visao-de-foco.md`, intervalo `6e99cc41..7bbd9738`; no domínio só `changelog.d/v047-visao-de-foco.md` (novo, 2 linhas, `### Adicionado`, E2.386). `bin/forge-changelog conferir --base origin/develop --branch melhoria/v047-visao-de-foco`: "ok: 1 fragmento(s) novo(s)", rc=0. O texto descreve o desenho entregue, sem código nem guarda; achados anteriores seguem como estavam. Achados recorrentes (PA-7) conferidos: nenhum alcança o delta.

## Achados
- A1 (recomendado) docs/arquitetura/visao-de-foco.md:60 · 2.2 e a tabela da seção 3 não preveem que o selo `.claude/` de hooks/conformidade.json:30 barra ao time o templates/projeto/.claude/settings.json (a E7.3 parou nisso). Falta a linha em "Onde não dá" com a saída: comando ao dono, sem contornar (R-CONFORMIDADE).
- A2 (recomendado) docs/arquitetura/visao-de-foco.md:155 · o critério de parada cita 6 oráculos tests/hooks/meta/jargao-<classe>.json que não existem na develop 1b88640e; a E7.4 entrou com jargao-classes-da-mensagem-do-evento.json. Atualize os nomes ou marque essa parte como já entregue por outro caminho.
- A3 (recomendado) docs/arquitetura/visao-de-foco.md:114 · padrão `regra` `R-[A-Z]{3,}` não pega R-QA (docs/regras/R-QA.md); herdado em hooks/meta.py:144 da develop: classes_de_jargao("Segue o R-QA na entrega.") devolve {}. Sugestão: `{2,}` no desenho e cartão para o hook (fora deste diff).

## Sondas

## Parecer
Aprovado. O desenho é fiel ao pedido, verificável e sem afrouxar trava; as referências ao código conferem na base citada. Os três achados são recomendados: A1 e A2 são o texto do desenho atrás do que já aconteceu na develop (trava do modelo e fixtures da E7.4); A3 é defeito provado, mas a expressão final é do autor ("ideia, o autor fecha a expressão", linha 110) e o código afetado (`hooks/meta.py:144`) já está na develop, fora deste diff: vai como cartão, não segura este commit de documentação.
