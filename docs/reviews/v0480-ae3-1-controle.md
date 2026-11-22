---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 98882c4903c31dd2e074783dec70b31882046244
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E108.2, AE3.1 bin/forge_controle.py)

Escopo conferido contra o brief do autor (E108.1): só o módulo `salvar`, teste, specs de mutante, uma linha em `tests/pesos-d4.json` e o fragmento; sem `bin/forge-check`, sem relógio (AE3.2), sem push. Diff b0895f6c..98882c49: 8 arquivos, 116 linhas de código (dentro do teto H1), um comportamento. O merge da `develop` (98882c49) só trouxe a base, pedido no brief por causa do `pesos-d4.json` (`R-FLUXO`).

## Achados
- A1 (recomendado) bin/forge_controle.py:35 · o hook é recusado por rodar código de fora, mas `core.fsmonitor` na config da pasta roda um programa no `git status` e o salvar segue (sonda S3: `salvo`, programa rodou); filtros `clean` e `commit.gpgsign` idem. Cabe ao parecer de segurança (E108.3, R-SEGURANCA) dizer se entra.
- A2 (recomendado) bin/forge_controle.py:113 · commit que falha deixa os nomes preparados no índice (sonda S2: `KANBAN.md` em `diff --cached`); o próximo commit à mão os leva junto. Sugestão: `reset -q -- <nomes>` no ramo de erro do commit.
- A3 (recomendado) bin/forge_controle.py:110 · arquivo novo no índice e apagado na árvore (`AD`) faz o primeiro salvar sair `erro` (`pathspec did not match`; sonda S1); o `add` limpa o índice e o segundo salvar sai `nada`. Não trava, mas é um `erro` falso.
- A4 (recomendado) tests/test_forge_controle.py:149 · nenhum teste prova que hook sem bit de execução não conta (`os.access(..., X_OK)` da linha 45 sem mutante); tirar a condição não mata nenhum teste.

## Sondas

## Parecer
Aprovado. Faz o que o AE3.1 pede: lista positiva (`KANBAN.md`, `docs/`), mensagem fixa, `commit --only` sem `add -A` (o teste confirma que o preparado fora da lista fica fora), nunca push nem `--no-verify`, nunca mexe no `core.hooksPath` (`R-VERIFY`), sem `GIT_*` herdadas, tudo ou nada nas recusas e trava por `flock`. Cada guarda tem teste do ramo de falha por comportamento.

Provas lidas e rodadas:
- `python3 -I -m unittest discover -s tests -p test_forge_controle.py`: `Ran 25 tests ... OK`.
- `bin/forge-mutante --processos 1` nas 4 specs `v0478-ae3-controle*.json` no rev 98882c4903c3: 25 de 25 mortos, rc=0 (CTL24 morreu por erro do teste declarado, aceito pela ferramenta).
- Sondas de leitura (recomendados, não bloqueiam): S1 `AD` → `('erro', "error: pathspec 'docs/novo.md' did not match ...")`; S2 commit falso que falha → índice com `KANBAN.md`; S3 `core.fsmonitor` = script que grava marca → `('salvo', ...)`, marca criada.
- Suíte inteira: fica no CI do PR (não rerrodada aqui).

Os recomendados viram cartão depois do merge (`R-REVIEW`); A1 depende do parecer de segurança.
