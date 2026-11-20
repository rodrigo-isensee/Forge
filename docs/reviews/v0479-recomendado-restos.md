---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-recomendado-restos
commit: 985cf4e3dba073c6c6eaca14195a4ac94f4575da
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E46.2 (META85-RECOMENDADO-RESTOS, head 985cf4e3)

Lido: `git diff 004ce869..985cf4e3` (5 arquivos, só texto, um teste e um fragmento de changelog). Fecha os achados A1 e A2 de `docs/reviews/v0479-meta85-recomendado.md`: o modelo e o agente de devops dão destino ao recomendado (vira cartão, R-REVIEW) e a "Uma passada" de R-REVIEW passa a citar o recomendado de segurança, coerente com a linha "O que bloqueia".

## Comandos (head 985cf4e3)
- `python3 -I tests/test_achado_teto_doc.py`: 8 testes, OK.
- Mutantes (cópia por `git archive`): voltar o texto antigo no `templates/projeto/docs/devops/_modelo.md` e tirar a frase nova do `agents/devops-engineer.md`: 3 falhas, os dois mortos.
- `python3 -m unittest test_forge.AntiDuplicacao` (em `tests/`): OK.
- Invariante `**Uma passada:**` de R-REVIEW (`tests/config.json:493`) segue casando.
- Suíte inteira: no CI do PR. H1: 0 linhas de código; um comportamento. Sem guarda mudada, sem mutante declarado a exigir.

Gatilho: nenhum.

## Achados
- A1 (recomendado) docs/devops/_modelo.md:17 · A cópia do modelo de devops da raiz do Forge segue "recomendado e não devolve", sem destino; o par de segurança da raiz está em CARTAO no teste. Alinhar ao modelo do projeto e incluir no CARTAO.

## Parecer
Aprovado. O diff faz o que E46.2 pede, com teste que mata a regressão nos dois arquivos novos; o A1 é recomendado (R-REVIEW), vira cartão depois do merge.
