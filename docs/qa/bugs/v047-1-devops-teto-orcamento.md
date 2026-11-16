# B-v047-1 - devops-engineer passa do teto do orcamento
- Severidade: alta (corrigido em b33bed29)
- Responsavel sugerido: autor da correcao (agente de desenvolvimento do Forge)
- Ambiente: melhoria/v047-frontmatter-agentes, head b1fa63a8

## Passos para reproduzir
1. python3 tests/test_orcamento_instrucao.py

## Resultado esperado
Nenhum agente acima do teto.

## Resultado obtido
devops-engineer: agente_caracteres = 5054 passa do teto 5052 (base: 5052).

## Evidencia
forge-testes --vermelho: test_nenhum_agente_passa_do_teto H=falha B=ok, regressao.
