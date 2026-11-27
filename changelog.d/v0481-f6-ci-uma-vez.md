### Alterado
- CI do PR: a suíte inteira roda uma vez (python 3.12); no 3.14 só instalação e fumaça; o envio na develop reaproveita a prova do PR mesclado (scripts/arvore-testada.py --do-pr); mutantes e a suíte no 3.14 rodam uma vez por dia na develop (diario.yml), com issue automática se quebrarem (v0481 E32.1)
