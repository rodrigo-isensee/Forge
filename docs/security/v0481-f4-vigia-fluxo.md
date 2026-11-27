---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: dd25e4a821e0e284215c2916f78147edbd285e7e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-27
---
# Review de segurança: v0481 (E34.12, #931, F4 do hook `vigia`, volta 2, por delta)

Delta lido (`forge-check parecer delta`, `04b508f6..dd25e4a8`), no domínio: só `bin/forge_estado.py` (`gravar_prs_abertos`). Fora do domínio, conferidos por causa do A3: `tests/mutantes/v0481-s1-status.json`, `tests/mutantes/v0481-f4-vigia-fluxo-7.json` e `tests/test_hook_vigia_f4.py` (`GravacaoDaLista`). A rodada anterior fica no git.

Gatilhos: controles do Forge (hook `vigia`), dado externo do `gh` no contexto do modelo, arquivo de estado novo.

## Achados
- A1 (bloqueante) hooks/vigia.py:617 · resolvido na volta 1 (filtro de fork em bin/forge_estado.py:82); o delta não toca o filtro.
- A2 (bloqueante) hooks/vigia.py:717 · resolvido na volta 1 (isenção com motivo na spec); o delta não toca o vigia.
- A3 (bloqueante) tests/mutantes/v0481-s1-status.json:57 · resolvido: o `de` de M7 e M8 leva o `return` da linha seguinte e fica único; S1 sem linha de v0481; suíte parte 4/5 verde no head.
- A4 (recomendado) bin/forge_estado.py:120 · resolvido: a gravação cala o OSError e tira o temporário; status e proximo seguem; testes de GravacaoDaLista cobrem diretório no destino, disco cheio, temporário que não sai e as duas chamadas.

## Detalhe
**A4.** O `except OSError` envolve só o `gravar_json` e o `chmod`; a limpeza apaga apenas `<lista>.<pid>.tmp`, o mesmo nome que o `gravar_json` (`hooks/_comum.py:2574`) cria, e `unlink` sobre link plantado remove o link, não o alvo. Sondas em processo (biblioteca padrão, na cópia, head `dd25e4a8`), todas sem exceção: diretório no destino (S2 da volta 1) deixa a pasta só com o diretório; diretório plantado no lugar do temporário fica onde estava, sem gravar nada; link plantado no temporário para um arquivo do sistema é trocado pelo arquivo real e o alvo fica intacto (o `O_NOFOLLOW` segue valendo). A pasta sem escrita não se prova como root; o teste com `PermissionError` simulado a cobre. Uma falha calada só deixa o `vigia` com a lista anterior, que ele já trata como vencida pelo `gravado_em`: não abre aviso falso nem cala bloqueio.

**A3.** `bin/forge-mutante --conferir --todas` na cópia: nenhuma linha de `v0481-*` (as três linhas restantes são de specs da develop, fora deste pedido). M50 a M52 (`v0481-f4-vigia-fluxo-7.json`) são do QA; a catraca do head está verde.

Testes afetados rodados na cópia: `tests.test_hook_vigia_f4`, `tests.test_vigia_parado` e `tests.test_forge_status_estado`, 92 testes, OK. CI do head `dd25e4a8` (run 45957852722): as cinco partes da suíte, passos, verificações longas, `python 3.14`, instalação, árvore já provada, teto de pulados e catraca verdes; `bateria` e `bateria (pareceres)` vermelhas só pela falta dos pareceres deste head.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta, sondas em processo, `forge-mutante --conferir --todas`, `gh pr checks`. Varredura de segredo e de dependência sem objeto: o delta não toca credencial, configuração nem dependência.
