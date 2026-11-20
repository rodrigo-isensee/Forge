# v0479-ae1-afirmacao-conta-citacao-e-codigo - a medida conta "feito" dentro de citação e código
- Severidade: média
- Responsável sugerido: python-backend (autor do `hooks/meta.py`)
- Ambiente: branch melhoria/v0479-ae1-medida-afirmacao, commit f15b9b85

## Passos para reproduzir
1. Chamar `afirmacao_sem_prova("> mesclado")` ou com "```\nintegrado\n```" em `hooks/meta.py`.

## Resultado esperado
Desenho aceito (`docs/propostas/v0479-melhorias-anti-erro.md:147`, confirmado pelo ERRO-JARVIS de 2026-11-20 18:02 no pedido v0478): a medida conta o texto fora de citação e de código.

## Resultado obtido
`True` nos dois casos: a medida lê o texto inteiro, e `tests/test_meta.py` (`test_afirmacao_escondida_em_citacao_ou_codigo_tambem_conta`) fixa esse comportamento, que o desenho deu por errado.

## Evidência
`hooks/meta.py:240-247` (regex sobre `medido`, sem `fora_de_codigo_e_citacao`); `tests/test_meta.py` AfirmacaoSemProva. Já existe `fora_de_codigo_e_citacao` no mesmo módulo.
