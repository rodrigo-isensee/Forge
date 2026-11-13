---
tipo: review
contrato: 1
pedido: v047-hook-heredoc-fp
branch: melhoria/v047-hook-heredoc-fp
commit: 0eee14533b579e8a7117666faad15f421fe4b17b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047-hook-heredoc-fp

Code review da E4.4 (E4.8, classe C) no head 58312004, por instância que não fez a entrega. Retomada depois da queda das 10:01, sem parecer anterior.

## Achados
- A1 (recomendado) hooks/parecer.py:174 · a lista COMANDO_DE_PR só vê o comando escrito em sequência: em corpo de Python com subprocess, 'gh pr '+'merge' ou ['gh','pr']+['merge'] passa e a develop barrava; é a mesma lacuna do python3 -c (HOOK-PYTHON-C-GH-PR); a segurança (E4.9) decide o alcance.
- A2 (recomendado) hooks/parecer.py:179 · o texto montado por função (`chr(103)+'h pr merge 5'`, base64) segue sem marcador no corpo e passa; é a lacuna da lista de nomes, igual à da `develop` e à do `python3 -c`; não afrouxa nada, só o registro.

## Sondas

## Parecer
Aprovado. O que o pedido pede está feito: corpo de heredoc lido só por `python3 -` (também com `timeout`, `env`, opções) deixa de ser conferido como comando de PR e não liga a rede D; o corpo de `sh` que só lê ou espera segue conferido e não liga a rede D; o caso verdadeiro segue barrado (subprocess com o comando de PR em lista ou texto, `gh api`, `os.system` com `git pull`, `sh` com o comando por número ou `eval`, `python3 -` em pipe para `sh`, Python gravado e rodado pelo `sh`, ruby, zsh, script, caminho, atribuição).

Verificações: o hook rodado do head em 22 entradas (sondas minhas, comparadas com a `origin/develop`), o corpus `heredoc-interpretador-*` (24 fixtures, os dois lados, mínimo afirmado no teste) e `tests/test_hooks_parecer_pasta.py` (4 testes, OK, 36 s). Mutação do autor no head (log `v047-e44-mut3.log`, rc=0): 17 mortos nos 3 specs, 1 por guarda. Sem PR aberto, então sem CI para citar. Tamanho: 74+5 linhas em `hooks/parecer.py` e 11 em `tests/*.py`, abaixo de 150, um comportamento só. Falso de git/gh: não há no diff.

Confira da rede D (ADR 0011, afrouxa para Python): o caminho de execução real que passa é só o que o corpo de Python monta de modo que o texto não traz o comando em sequência (A1). Equivale ao que `python3 -c` e a concatenação `'g'+'h'` já faziam passar na develop, então não abre capacidade nova, só tira a defesa em profundidade do caso do texto literal; com a lista de lançamento (`subprocess`, `os.system`, `exec(`) mais a de comando, o descuido comum segue barrado. Fica registrado para o parecer de segurança e para o cartão HOOK-PYTHON-C-GH-PR; não bloqueia por não ser requisito do pedido nem defeito dos casos declarados.

## Revalidação por delta (E4.12, volta E4.11)
Delta lido: `forge-check parecer delta`, intervalo 58312004..0eee1453, 25 arquivos no domínio: `hooks/parecer.py` (LANCA_PROCESSO com lançador também depois de `_`, mais `getattr`, `globals`, `vars`, `__dict__`, `modules`; `comando_de_pr_no_python` por `ast` nas constantes do corpo, sem as soltas, falha fechado no que o `ast` não lê; `chamada_muda_o_corpo` para atribuição e `git` na chamada), 12 fixtures `heredoc-interpretador-*` novas (36 no mínimo do teste), doc, emenda v047 na ADR 0011 e 2 specs novos (25 mutantes no total). O delta cobre o que a segurança e o QA acharam em 58312004 sem abrir caminho novo.

Sondas refeitas (hook rodado do head e da `main` 0.46.0, repositório de teste, ambiente limpo). Barrados com saída 2 no head: subprocess em lista, em duas linhas, concatenação `"gh "+"pr merge"`, `create_subprocess_exec`, `posix_spawnp`, `getattr(os,"sy"+"stem")`, `globals()[...]`, bytes, f-string, `" ".join([...])`, alias de `subprocess`, `os.popen` com `gh api`, `exec("...")`, corpo ilegível (falha fechado), `PATH=` e `env PATH=` antes do `python3 -`, `git` na mesma chamada, `sh` com `git merge`, `python3 -` em pipe para `sh`, ruby. Liberados (0): `print(1)`, docstring ou comentário com `gh pr merge`, `print('gh pr merge 5')`, `subprocess.run(["ls"])`; a `main` barrava os três do meio, que são os falsos positivos do pedido. Os casos verdadeiros dão o mesmo nos dois lados: sem regressão. O único que passa e deveria barrar é o A2, igual na `main`.

Verificações: `tests/test_hooks_parecer_pasta.py` (4 testes, OK, 81 s); `bin/forge-mutante tests/mutantes/v047-hook-heredoc-fp-4.json` (M25 e M26 mortos); log do autor `v047-e411-mut3.log` no head, rc=0, 25 mortos. Sem PR aberto, sem CI para citar. Tamanho: 56 linhas em `hooks/parecer.py` e 1 em `tests/*.py`, abaixo de 150, um comportamento só. Sem falso de git/gh no delta.

Aprovado no head 0eee1453, sem bloqueante.
