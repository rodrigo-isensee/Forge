---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-trava-critica
commit: aa0f55f8ae0829ad1e958c543e259d5ff6cb6b92
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E169.7, PR #853, VIGIA-PRAZO-TRAVA, revisão por delta)

Diff revisado nesta volta: `cf8b8f69..aa0f55f8`, sem o que veio da `develop`. Delta lido: `forge-check parecer delta`. Commit de autor: `160ab342` (E169.6), 3 arquivos, nenhuma linha de código de hook. O merge `aa0f55f8` traz a `develop` em `fde1e76b`. O review anterior (E169.3, head `cf8b8f69`) cobre o resto e segue valendo.

## Achados
- A1 (recomendado) hooks/agentes.py:1421 · `agentes` e `pesado` também recusam e rodam sem `regra_do_prazo`: o timeout de 10 s do Claude Code ainda os libera. A decisão fala em "toda trava que pode recusar"; vale um cartão para decidir se o vigia se estende a eles (de E169.3, mantido).
- A2 (recomendado) hooks/_comum.py:2863 · Sem o marcador e sem corpo pendente, a recusa diz "a chamada com ação crítica", e a linha não tem ação crítica. Um texto neutro ("a chamada") evita confundir quem lê o stderr (de E169.3, mantido).

## Parecer
Aprovado no head `aa0f55f8`.

- **Delta lido:** no domínio, o `forge-check parecer delta` lista `tests/test_hooks_volta_propriedades.py`, `tests/mutantes/heredoc-donos.json` e `docs/hooks-fixtures.md`. A ADR 0003 e `tests/test_hooks.py` também aparecem, mas o que mudou neles veio da `develop` (`fde1e76b`, hook `ordens`, PR #805). Contra a base atual (`git diff fde1e76b aa0f55f8`), o PR toca os 15 arquivos já revisados, que incluem esses 3.
- **O merge não mexe no código revisado:** as linhas `+/-` de `hooks/_comum.py` são idênticas em `0f4a7791..cf8b8f69` e em `fde1e76b..aa0f55f8`, conferidas com `diff`.
- **Esperado trocado em `test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem`** (`tests/test_hooks_volta_propriedades.py:224-227`): no caso "sem marcador", o teste esperava `(0, "")` e agora espera código 2 e o stderr `^<regra>: o hook não decidiu`. A troca segue a DECISÃO DO DONO de 2026-11-24 07:43 (`docs/pedidos/v0478.md:1009`): prazo vencido numa trava recusa, nunca libera. Não afrouxa nada:
  - a asserção ficou mais estrita: exige a recusa pela regra do próprio hook (R-CONFORMIDADE ou R-REVIEW);
  - o teto `< PRAZO_DO_CLAUDE_CODE_S` continua;
  - os casos "sem passo lento" (libera) e "com marcador" (recusa antes de 10 s) estão intactos.
  O nome antigo do teste fica porque `tests/mutantes/lote-unico-032-l31.json` o cita; a docstring diz isso.
- **D11 e D12** (`tests/mutantes/heredoc-donos.json`) foram realinhados à fonte: o trecho antigo `hook.marcado is False and not hook.corpos_pendentes` já não existe.
  - O novo D11 põe de volta a isenção pelo marcador no retorno antecipado (`_comum.py:2860`), justamente o afrouxamento que a decisão proíbe.
  - O D12 anula o ramo da mensagem dos corpos pendentes (`:2863`).
  - `bin/forge-mutante --ids D11,D12 tests/mutantes/heredoc-donos.json` (rev `aa0f55f8ae08`): D11 morreu em `:2860`, D12 morreu em `:2863`.
- **`docs/hooks-fixtures.md`:** contra a `develop`, mudam só a contagem (3515 → 3516), a linha `conformidade`, a linha `errointerno-*` (uma fixture passa de libera a recusa, com `VIGIA-PRAZO-TRAVA`) e a linha nova `vigia-*`. Tudo bate com as fixtures já revisadas.
- **Testes do arquivo tocado, no head:** `test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem` e `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa` passaram (2 OK, 19,6 s).
- **CI do PR #853 no head `aa0f55f8`** (run 45394038493):
  - verdes: as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `teto de pulados` e `árvore já provada na develop`;
  - vermelhos à espera dos pareceres deste head: `bateria`, `bateria (pareceres)` e `catraca`.
  A suíte não foi rodada de novo aqui (R-REVIEW).
- **Commit:** `test(hooks): ...`, em Conventional Commits em português, cita a etapa E169.6. A base entrou por merge, sem `--force`.
