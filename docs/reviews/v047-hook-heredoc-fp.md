---
tipo: review
contrato: 1
pedido: v047-hook-heredoc-fp
branch: melhoria/v047-hook-heredoc-fp
commit: 58312004dfd8940079d5232a98e1d2936e51e108
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047-hook-heredoc-fp

Code review da E4.4 (E4.8, classe C) no head 58312004, por instância que não fez a entrega. Retomada depois da queda das 10:01, sem parecer anterior.

## Achados
- A1 (recomendado) hooks/parecer.py:174 · a lista COMANDO_DE_PR só vê o comando escrito em sequência: em corpo de Python com subprocess, 'gh pr '+'merge' ou ['gh','pr']+['merge'] passa e a develop barrava; é a mesma lacuna do python3 -c (HOOK-PYTHON-C-GH-PR); a segurança (E4.9) decide o alcance.

## Sondas

## Parecer
Aprovado. O que o pedido pede está feito: corpo de heredoc lido só por `python3 -` (também com `timeout`, `env`, opções) deixa de ser conferido como comando de PR e não liga a rede D; o corpo de `sh` que só lê ou espera segue conferido e não liga a rede D; o caso verdadeiro segue barrado (subprocess com o comando de PR em lista ou texto, `gh api`, `os.system` com `git pull`, `sh` com o comando por número ou `eval`, `python3 -` em pipe para `sh`, Python gravado e rodado pelo `sh`, ruby, zsh, script, caminho, atribuição).

Verificações: o hook rodado do head em 22 entradas (sondas minhas, comparadas com a `origin/develop`), o corpus `heredoc-interpretador-*` (24 fixtures, os dois lados, mínimo afirmado no teste) e `tests/test_hooks_parecer_pasta.py` (4 testes, OK, 36 s). Mutação do autor no head (log `v047-e44-mut3.log`, rc=0): 17 mortos nos 3 specs, 1 por guarda. Sem PR aberto, então sem CI para citar. Tamanho: 74+5 linhas em `hooks/parecer.py` e 11 em `tests/*.py`, abaixo de 150, um comportamento só. Falso de git/gh: não há no diff.

Confira da rede D (ADR 0011, afrouxa para Python): o caminho de execução real que passa é só o que o corpo de Python monta de modo que o texto não traz o comando em sequência (A1). Equivale ao que `python3 -c` e a concatenação `'g'+'h'` já faziam passar na develop, então não abre capacidade nova, só tira a defesa em profundidade do caso do texto literal; com a lista de lançamento (`subprocess`, `os.system`, `exec(`) mais a de comando, o descuido comum segue barrado. Fica registrado para o parecer de segurança e para o cartão HOOK-PYTHON-C-GH-PR; não bloqueia por não ser requisito do pedido nem defeito dos casos declarados.
