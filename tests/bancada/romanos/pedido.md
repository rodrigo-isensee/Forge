Pedido de referência do bench de versões (BENCH-VERSAO, romanos v1). Este texto é igual em toda rodada; não pergunte o que já está decidido abaixo.

Quero um conversor de numerais romanos neste projeto.

Critérios de aceite:
1. `para_romano(n)` em `src/romanos.py` converte um inteiro de 1 a 3999 no numeral romano na forma canônica, em maiúsculas, com a subtração padrão (4 = IV, 9 = IX, 40 = XL, 90 = XC, 400 = CD, 900 = CM).
2. `de_romano(texto)` em `src/romanos.py` converte um numeral na forma canônica de volta para o inteiro; aceita minúsculas e espaços nas pontas.
3. Entrada inválida levanta `ValueError`: inteiro fora de 1 a 3999; valor de tipo errado (em `para_romano`, o que não é `int`, inclusive `bool` e `float`; em `de_romano`, o que não é texto); texto vazio; símbolo desconhecido; ou forma que não é a canônica (por exemplo IIII, VV, IC, MMMM).
4. Linha de comando `python3 src/romanos.py <valor>`: um número vira romano e um romano vira número, impresso numa linha na saída padrão, com código 0. Entrada inválida, sem argumento ou com mais de um argumento escreve o erro na saída de erro e sai com código 2, sem nada na saída padrão.
5. Testes do projeto em `tests/` cobrindo os quatro critérios acima e, na raiz, um README em Markdown (extensão `.md`) com o uso da linha de comando.

Decisões já tomadas pelo dono (valem como respondidas):
- Python 3.10 ou mais novo, só a biblioteca padrão; nenhuma dependência nova.
- O pronto do projeto é o comando gravado no CLAUDE.md pelo forge-init; os testes usam unittest.
- Valor com dígitos (`2024`) é número; qualquer outro texto é tratado como romano.
- Fora do escopo: números acima de 3999, zero, frações e numerais com barra.
- Entrega pelo fluxo do projeto: branch própria, pareceres da classe e PR para a `develop` no remoto `origin`. Pode integrar na `develop` com tudo verde; a `main` não se toca.
- Ninguém vai responder perguntas durante a rodada: para o que não está aqui, siga a opção recomendada e registre a escolha no PR.
