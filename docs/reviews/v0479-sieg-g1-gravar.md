---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-sieg-g1-gravar
commit: d7c1a53b259e6f2ce980cbe05a2986eeed958be6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 E90.7 (SIEG-G1 G1.2a, `forge-check autorizacao gravar`, volta E90.6)

Revalidação por delta (Decisão 1 do dono, 23/11): `forge-check parecer delta` lido, intervalo `2a0e4620..d7c1a53b`; no domínio `bin/forge_autorizacao.py`, `changelog.d/v0479-sieg-g1-gravar.md`, `docs/adr/0018-autorizacao-do-dono-gravada.md`, `tests/mutantes/v0479-sieg-g1-gravar.json`, `tests/mutantes/v0479-sieg-g1-gravar-7.json` e `tests/test_autorizacao_gravar.py`.

## Achados
- A1 (recomendado) docs/adr/0018-autorizacao-do-dono-gravada.md:53 · Diz que a volta "fechou" o A4 da segurança, mas `HOME` e `CLAUDE_CODE_SESSION_ID` são do ambiente do chamador: transcrição escrita pelo agente em `$TMPDIR` com os dois ajustados grava `ativa` (S1). Diga que a origem só se prova no corte do hook; `HOME` pode sair de `pwd.getpwuid`
- A2 (recomendado) bin/forge_autorizacao.py:311 · Herdado do review anterior (era A2): `(?![\w.])` não aceita ponto final logo após o alvo, e "pode aplicar o rótulo no PR 5." nasce pendente. Falha fechada; alinhe com o `do_item`

## Sondas
- S1 · `HOME` e `CLAUDE_CODE_SESSION_ID=s9` do chamador, `<tmp>/h/.claude/projects/p/s9.jsonl` escrito à mão (origin human, hora atual), gravar pr:5 · espera: recusada (como diz a ADR) · obtido: rc 0, A-1 gravada · ativa

## Conferido
- **A1 anterior (bloqueante) fechado:** o classificador agora é positivo, `origin == {"kind": "human"}`, e recusa também `isCompactSummary` e `isVisibleInTranscriptOnly` (`bin/forge_autorizacao.py:292-293`). Nas transcrições reais desta máquina, a mensagem digitada pelo dono traz `origin {"kind":"human"}` (595 registros), e o resumo de compactação vem sem `origin` (29): o critério separa os dois. Se o Claude Code acrescentar um campo ao `origin`, a igualdade exata falha fechada.
- **Volta E90.6 da segurança:** a fala no futuro ou de mais de 48 h recusa (`:377`); o prazo local nasce `pendente-confirmacao` com "prazo local sem fuso nesta etapa" (`:328`), e data já passada nunca nasce ativa. `agora` foi injetado em `cmd_gravar` e em `concessao_lida` para o teste do relógio.
- **A3 e A4 anteriores:** a ADR registra a cópia do classificador em `hooks/vigia.py` como corrigida noutro item. A frase sobre a origem do registro ficou mais forte do que o código entrega (A1 acima).
- **Mutantes (guardas do diff):** `bin/forge-mutante tests/mutantes/v0479-sieg-g1-gravar-7.json` com M47 a M54 mortos, um por linha de guarda nova; M1, M4 e M5 foram realinhados às linhas novas.
- **Testes:** `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao` deu 43 testes, OK. O teste que roda subprocesso limpa o ambiente herdado e usa `-I`. Suíte inteira: no CI.
- **Tamanho (H1):** o delta soma cerca de 14 linhas de código em `bin/`, e o item segue dentro do teto.

## Parecer
Aprovado (`R-REVIEW`). O bloqueante do review anterior está corrigido, com teste do ramo de falha e mutante morto. A1 e A2 não bloqueiam e viram cartão depois do merge. O A1 tem a mesma gravidade que a segurança deu à via (A4 dela, recomendado). Ele não bloqueia porque nada consome concessão antes da G1.3, e o hook é o corte que prova a origem.
