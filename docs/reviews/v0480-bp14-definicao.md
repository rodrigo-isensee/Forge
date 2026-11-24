---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-bp14-definicao
commit: 0f921872cf4e8f854bfc7ccefab316da3fd046e3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E163.2, BP14: definição de pedido parado nos modelos de retrospectiva)

Base `998e2e45`, head revisado `0f921872` (E163.1). Diff de 3 arquivos, 4 inserções e 2 remoções: o comentário da seção 1 de `docs/retrospectivas/_modelo.md` e de `templates/projeto/docs/retrospectivas/_modelo.md` (linha 9) e o fragmento `changelog.d/v0480-bp14-definicao.md`. Responde ao A1 (recomendado) do parecer `docs/reviews/v0480-bp14-retro.md`.

## Leitura
- Escopo: faz o que a E163.1 pede, a definição "aberto, sem movimento no quadro há 7 dias ou mais" no ponto em que a tabela pedido × não entregue é pedida; nada além. Os dois modelos seguem byte a byte iguais (`cmp` sem diferença).
- Prazo de 7 dias contra o que o Forge já mede: nenhum código do Forge mede pedido parado por dias. O que existe é o aviso "sem movimento no histórico" do `forge-check kanban --gerar` (sem prazo) e a política de `R-WIP` "Parado não se abandona" (sem limiar). A fonte da medida, `docs/kanban/historico.md` com a hora de cada movimento, já é a que `forge_voltas` e `forge_medidas` leem, então os 7 dias são mensuráveis sem mecanismo novo. O número combina com os prazos de semana já em uso (quarentena `PRAZO_DIAS = 7` em `bin/forge_quarentena.py:26`; prazo escrito de 7 dias em `bin/forge_autorizacao.py:313`) e não colide com o de 24 h do `forge-check retro --pendentes`, que mede tag sem retro, não pedido.
- `R-NEUTRO`: texto genérico, sem nome de projeto. Fragmento de changelog no formato (`### Adicionado`).
- Tamanho (H1): 2 linhas de texto de modelo, abaixo do teto.

## Verificação
- Testes dos arquivos tocados, ambiente limpo: `python3 -m unittest test_retro_pendentes test_modelos_projeto` em `tests/`: `Ran 45 tests ... OK`. Suíte inteira fica no CI do PR.
- Sem guarda de código no diff: sem mutante a declarar.

## Parecer
Aprovado. Mudança de texto pequena, consistente nos dois modelos e com prazo mensurável pela fonte que o Forge já tem.
