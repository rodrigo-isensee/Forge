---
tipo: review
contrato: 1
pedido: parecer-avisos
branch: melhoria/parecer-avisos
commit: 937ea10781ffc8d6fabc97df7a745fb094565b92
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Review: parecer-avisos

## Achados

## Parecer
Aprovado. Diff de 11 linhas, só texto, sem código (teto M14 não se aplica).

- Escopo (E1, E2, E3): a linha de avisos está nos três modelos de templates/projeto/docs (reviews, qa, security) e em docs/security/_modelo.md; a frase do brief de parecer entrou em agents/jarvis.md; o fragmento changelog.d/parecer-avisos.md existe.
- Os avisos citam o ID da regra sem copiar frase de regra; o teste regra_so_na_fonte (tests/test_forge.py) passa. Cada texto tem menos de 300 caracteres.
- Consistência: as quatro linhas são idênticas, ao lado da linha de bloqueio, antes de `## Achados`. O modelo de security do Forge e o do template já eram o mesmo blob e seguem iguais.
- Rodado: `forge-check docs` sem saída de erro; test_modelos_projeto e test_modelos_citados verdes (9 testes).
- Achados recorrentes (PA-7): nenhuma classe se repetiu; sem linha AR.
- Segurança: sem gatilho (só texto); parecer próprio não exigido.
- Observação sem peso: a linha de aviso será copiada para os pareceres; é inofensiva.
