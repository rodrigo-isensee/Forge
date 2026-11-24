---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-guarda
commit: 9e460e4f1aa51ef214386390351faf9ebc749deb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E123.26, corte 1 do hook de ordens: só a guarda, PR #811)

## Achados
- A1 (recomendado) hooks/conformidade.json:66 · o motivo cita o hook `ordens` e o item 6 da emenda da ADR 0003, que ainda nomeia `.forge/ordens-em-vigor.md`, `docs/kanban/ordens-em-vigor.md` e "no mesmo PR do hook"; até o item 2, a develop tem guarda e ADR com caminhos diferentes. O item 2 traz a emenda; cartão para conferir.

## Sondas

## Parecer
Aprovado no head 9e460e4f.

Escopo: o diff contra a `develop` (Base-sha fc488261) é só a guarda. Conferi o que o autor declara: `git diff ee74a51b HEAD -- bin/forge-init hooks/conformidade.py hooks/conformidade.json` (ee74a51b é o head remoto da `melhoria/v0480-ordens-hook`) sai vazio, e as fixtures `tests/hooks/conformidade/ordens-*` também não mudam. O que difere da origem é só o recorte: sem o hook `ordens`, o `hooks.json`, a emenda da ADR, as fixtures do `ordens` e os testes que o importam; a classe `GuardaDasOrdens` não importa o hook.

Teto H1: código com 34 linhas adicionadas e 12 removidas (`conformidade.py` +29 -10, `conformidade.json` +2, `forge-init` +3 -2), um comportamento só (quem grava o arquivo de ordens).

Leitura: `relativos_a_copia_principal` reaproveita o `diretorio_comum` de `_comum.py` e o `relativo_ao_pai` já existente; o custo extra só aparece quando as duas formas anteriores não casam e a entrada é `.forge/ordens/` (curto-circuito do `or`). `entrada_valida` sem função interna, uma guarda por campo, com caso de teste por guarda. O `CONTROLE_NO_TEXTO` e o `PEDIDO_OU_BRIEF` ganham `ordens` e o U6 acompanha a linha mudada (AR-12).

Mutantes, um processo, no head: `bin/forge-mutante` com `v0480-ordens-guarda.json` e `-2.json` dá 16 de 16 mortos (M15, M16, M22 a M26, M28, M30 a M37); o M26 morre por erro do `git check-ignore` (o teste levanta quando o arquivo não é ignorado, como o comentário diz). U6 morreu. `--cobertura --base fc488261` dá cobertas todas as linhas de guarda do `conformidade.py`; `forge-init` e `conformidade.json` aparecem como "não coberto" na análise por linha, mas o M26, o M28 e o M30 os mutam e morrem. `--conferir` aponta cada trecho no lugar.

Testes dos arquivos tocados: `GuardaDasOrdens` (4), `test_politica_de_conformidade_malformada_bloqueia` e `test_o_arquivo_de_ordens_fica_fora_do_git`: 6 OK. `scripts/indice-fixtures.py --conferir`: em dia. Suíte: CI do PR #811 no head, as 10 partes de `suíte` (3.12 e 3.14) verdes, sem rerrodar.

Sondas de falso positivo no hook da branch (passaram, não provam bloqueante): `git add`, `git commit` e `git push origin melhoria/v0480-ordens-guarda` com a pasta corrente numa worktree de `~/.forge-contrib/wt/`, gravar parecer de branch com `ordens` no nome pelo caminho de `wt/`, `cat` das ordens para fora e um texto com `subordens` liberam; `cp` e `>>` do tech-lead em `docs/ordens/` recusam; o jarvis grava.

Pendência fora do código (não é do review): a `catraca` do PR falha por R-CONTRIB, sem as seções `Projeto de origem` e `Como medir` no corpo do PR; e a `bateria (pareceres)` espera os pareceres deste head. O autor corrige o texto do PR sem novo commit.
