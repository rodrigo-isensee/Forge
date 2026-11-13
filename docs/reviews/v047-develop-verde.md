---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-develop-verde
commit: cc266228af35cfd870a34ab71cb4b3c3e3299f9f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (develop verde, E1.80)

## Achados
- A1 (recomendado) skills/esperar-estado/SKILL.md:19 · a frase "rode na pasta do repositório" saiu para caber no teto; nenhuma regra ou invariante depende dela, mas vale reavaliar se o agente ainda sabe de onde rodar o laço.

## Sondas

## Parecer
Aprovado. O diff tem 2 arquivos (SKILL.md com 2 linhas trocadas e o fragmento de changelog). A frase "pasta gravável (por exemplo, `${TMPDIR:-/tmp}`)" que `TmpdirComRecuo.test_formas_do_recuo` guarda voltou; o teste passa. Nenhuma regra saiu: o invariante `nunca por kill -0 no pid gravado` (R-TETO) segue no texto e `tests/test_esperar_estado.py` passa (15 testes). Os testes de teto e de skills em `tests/test_forge.py` passam. Sem mudança de código, guarda ou teste, então não há mutante a declarar. O CI do PR 538 estava com checks verdes (catraca, instalação, bateria de passos e de pareceres, verificações longas) e as suítes 3.12 e 3.14 em andamento na hora da leitura; o merge espera o verde delas.
