---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-jargao-medida
commit: b8d4cda82594978d6edd6f309721a742848a3b81
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Code review: medida de jargão por classe na mensagem ao dono (E7.4, revisão E2.219)

Escopo: `git diff e13aed85...b8d4cda8` (3 commits; `hooks/meta.py`, `tests/test_meta.py`, uma fixture de `meta`, o índice `docs/hooks-fixtures.md`, o fragmento de changelog e três specs de mutante). Parecer completo, que é o primeiro deste item. O revisor não fez a entrega.

## Achados
- A1 (bloqueante) hooks/meta.py:139 · a classe etapa não conta o termo no fim da frase: o `(?![\w.])` recusa o ponto final, e "Terminei a E7.4." dá `{}` (sonda S1). É a forma mais comum na mensagem ao dono, e a medida da diretriz 31 fica subcontada. Sugestão: `(?!\w|\.\w)` e um caso com ponto final no teste.
- A2 (recomendado) hooks/meta.py:153 · a cerca `~~~` não abre bloco de código, e o comando dentro dela conta (`~~~\ngit push\n~~~` dá ferramenta 1). Sugestão: aceitar as duas cercas, com um caso no teste.
- A3 (recomendado) hooks/meta.py:162 · `explicado` divide o prefixo inteiro a cada termo, e o custo cresce com o quadrado: 22.800 caracteres com 1.600 termos levam 0,86 s. Com o teto de 1.200 caracteres e o timeout de 300 s não pesa. Sugestão: procurar só o último separador antes de `inicio`.

## Sondas
- S1 · `python3 -c 'import meta; print(meta.classes_de_jargao("Terminei a E7.4."))'` em hooks/ · espera: {'etapa': 1} · obtido: {}

## Parecer
Reprovado por A1 (`R-REVIEW`: defeito provado, com gatilho). Fora ele, o item faz o que a E7.4 pede: a medida lê `last_assistant_message` e cai para o transcrito quando o campo vem vazio; conta por classe, só fora de cerca e de citação; nunca grava o termo nem bloqueia; e o erro continua isolado da conferência do objetivo (`tests/test_meta.py`, caso já existente).

Verificadores, rodados no clone no head b8d4cda8:
- `python3 -m unittest tests.test_meta`: 9 testes, OK.
- `bin/forge-mutante --processos 1` com as três specs: M1 a M17 morreram, rc=0.
- `bin/forge-mutante --cobertura --base e13aed85`: toda condição mudada tem mutante declarado (linhas 153, 154, 155, 163, 169, 171 e 177).

A suíte inteira fica para o CI do PR. O item ainda não tem PR (o brief manda não abrir). Tamanho (M14): 133 linhas de código e teste (`hooks/meta.py` com 64, `tests/test_meta.py` com 69), dentro de 150, com um comportamento só e a fixture `jargao-*` no corpus de `meta`. Neutralidade (`R-NEUTRO`): nada de projeto entra. Os itens do Entregar da E7.4 e a E2.218 (índice regenerado) têm commit.

Na volta, corrija A1 com um caso de teste e um mutante para a guarda nova da linha 139. A revalidação lê só o delta.

Achados recorrentes: A1 a A3 não se repetem em `docs/engineering/achados-recorrentes.md`, então nenhuma linha AR é gravada.
