---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-recomendado-restos
commit: 8d9f2b959719c61ea66e182f5e3720514e82d539
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E46.2 (META85-RECOMENDADO-RESTOS, head 8d9f2b95; revalidado de 985cf4e3)

Lido: `git diff 004ce869..985cf4e3` (5 arquivos, só texto, um teste e um fragmento de changelog). Fecha os achados A1 e A2 de `docs/reviews/v0479-meta85-recomendado.md`: o modelo e o agente de devops dão destino ao recomendado (vira cartão, R-REVIEW) e a "Uma passada" de R-REVIEW passa a citar o recomendado de segurança, coerente com a linha "O que bloqueia".

## Comandos (head 985cf4e3)
- `python3 -I tests/test_achado_teto_doc.py`: 8 testes, OK.
- Mutantes (cópia por `git archive`): voltar o texto antigo no `templates/projeto/docs/devops/_modelo.md` e tirar a frase nova do `agents/devops-engineer.md`: 3 falhas, os dois mortos.
- `python3 -m unittest test_forge.AntiDuplicacao` (em `tests/`): OK.
- Invariante `**Uma passada:**` de R-REVIEW (`tests/config.json:493`) segue casando.
- Suíte inteira: no CI do PR. H1: 0 linhas de código; um comportamento. Sem guarda mudada, sem mutante declarado a exigir.

Gatilho: nenhum.

## Revalidação (head 8d9f2b95)
Delta lido: `forge-check parecer delta docs/reviews/v0479-recomendado-restos.md`, intervalo 985cf4e3..8d9f2b95 sem o que veio da base (develop c2cec75); no domínio só `agents/devops-engineer.md:17` (8d9f2b95, E46.6). A linha encurta "quando houver gatilho" → "com gatilho", "na passada do code review" → "no code review" e junta a última frase ("vira cartão depois do merge e promovê-lo pede `critério mudou:`"); o sentido, os IDs (R-REVIEW, R-SEGURANCA) e a frase que o teste do pedido protege ficam. Arquivo 5187 → 5155 bytes.
- `python3 -I test_orcamento_instrucao.py` (em `tests/`): 8 testes, OK.
- `python3 -I test_achado_teto_doc.py` (em `tests/`): 8 testes, OK.

## Achados
- A1 (recomendado) docs/devops/_modelo.md:17 · A cópia do modelo de devops da raiz do Forge segue "recomendado e não devolve", sem destino; o par de segurança da raiz está em CARTAO no teste. Alinhar ao modelo do projeto e incluir no CARTAO.

## Parecer
Aprovado. O diff faz o que E46.2 pede, com teste que mata a regressão nos dois arquivos novos; o A1 é recomendado (R-REVIEW), vira cartão depois do merge.
