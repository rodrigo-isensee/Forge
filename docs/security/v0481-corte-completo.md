---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-corte-completo
commit: 8e814a7337637b561c53fe9b66ba4fd54966b1ec
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E13.22, #887, forge-fechar --corte: marca pronta para a promoção; classe C), revalidação por delta

## Gatilhos
Gatilhos: controle do fluxo de merge e de release (`forge-fechar --corte`, R-FLUXO, R-MAIN), envio a ramo no origin, rótulo do dono (R-CONTRIB).

## Lido
Delta `git diff 036a78a1..8e814a73` (volta E13.19): `bin/forge-fechar:1556` (só o texto do `die` do V5), `docs/fechamento-integrador.md` (o limite do `--laco` e como refazer o corpo), `tests/test_fechar_corte.py` (`test_leitura_do_origin_que_falha_nao_anexa` e a asserção da mensagem nova), `tests/mutantes/v0481-corte-completo-3.json` (M17), `tests/test_reval_delta.py:124` (contagem 2 para 3) e os pareceres de review e QA. A rodada anterior (no git, sobre 036a78a1) já leu o resto do `bin/forge-fechar` do item; não a recopio.

## Achados anteriores
- A1 (bloqueante, corrigido): `tests/test_reval_delta.py:124` agora diz 3, igual às citações reais; `python3 -I tests/test_reval_delta.py` passa e a suíte parte 3/5 está verde no CI (abaixo).

## Detalhe (só aperta ou neutro, por escrito)
- **Contagem 2 para 3:** a guarda continua exigindo o número exato de citações de `README.md` no arquivo; a lista só passa a refletir a citação sintética já revisada na rodada anterior: neutro.
- **Teste e M17:** o ramo de falha `[ "$r" != erro ]` (bin/forge-fechar:1615) ganhou teste: ls-remote em erro sai em 0, sem aviso de anexo, ramo no origin igual, sem `pr edit` nem `pr create`. `bin/forge-mutante tests/mutantes/v0481-corte-completo-3.json`: M17 morreu. Aperta (o que já barrava ganhou prova).
- **Mensagem do V5:** só texto; aponta para `$tmp/nova-medida`, que continua existindo depois do `die` (o `fim` do EXIT não apaga o `mktemp -d` do anexo, modo 0700, que guarda só a medida, sem segredo). Não sugere `--force`, rótulo nem merge: neutro.
- **Documentação:** registra o limite (item e marca mesclados na mesma volta do `--laco` deixam o fragmento para a versão seguinte; nada passa sem parecer) e que o corpo se ajusta à mão: neutro.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI: o run do Revisar-sha (45554026272) foi cancelado pelos envios dos pareceres de QA e review (a parte 3/5 do Python 3.14 chegou a terminar verde); no run 45555102260, do head 7f4d4fa2 (o Revisar-sha mais só `docs/qa` e `docs/reviews`), a suíte parte 3/5 está verde nas duas versões do Python, com as demais partes verdes ou em andamento na leitura. A `bateria (pareceres)` vermelha é a falta deste parecer no head. Rodei `python3 -I tests/test_fechar_corte.py` (29 testes, OK), `python3 -I tests/test_reval_delta.py` (10 testes, OK) e o M17 (morreu). gitleaks, shellcheck, zizmor, actionlint e semgrep ausentes no PATH (lacuna; o delta não toca workflow nem segredo).
