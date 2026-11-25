---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-corte-completo
commit: 8e814a7337637b561c53fe9b66ba4fd54966b1ec
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E13.20, #887, forge-fechar --corte: marca pronta para a promoção; classe C), por delta

## Lido
Revalidação por `forge-check parecer delta docs/reviews/v0481-corte-completo.md`: intervalo `036a78a1..8e814a73`, no domínio `bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/mutantes/v0481-corte-completo-3.json`, `tests/test_fechar_corte.py` e `tests/test_reval_delta.py` (`revalida: sim`, o parecer anterior era reprovado). Li só esse delta; o restante do parecer de `036a78a1` segue valendo.

## Achados anteriores
- A1 (bloqueante): corrigido. `tests/test_reval_delta.py:124` conta 3 citações de README.md em `test_fechar_corte.py`; `python3 -I tests/test_reval_delta.py`: 10 testes, OK. No CI do head 8e814a73 (run 45554026272), `suíte (python 3.14, parte 3/5)` verde; a 3.12 parte 3/5 foi cancelada pelo push do parecer do QA (7577cf6f, só `docs/qa/`), e o CI do head final decide o merge.
- A2 (bloqueante): corrigido. `test_leitura_do_origin_que_falha_nao_anexa` põe o ls-remote do ramo em erro com fragmento novo e confere rc 0, a linha "já existe no origin (ou a leitura falhou)", sem aviso de anexo, ramo do origin intacto e nenhum `pr edit` nem `pr create`. M17 declarado em `tests/mutantes/v0481-corte-completo-3.json` (mesma troca da S1 anterior): `bin/forge-mutante --processos 1` dá `M17 · morreu · bin/forge-fechar:1615`.
- A3 (recomendado): resolvido. A mensagem de `bin/forge-fechar:1556` diz que o mesmo comando não refaz o corpo e aponta a medida na pasta temporária; a pasta sobrevive ao `die` (o `fim` não a apaga) e o teste do V5 confere o texto novo.
- A4 (recomendado): resolvido. O limite do `--laco` (item e marca mesclados na mesma volta deixam o fragmento para a versão seguinte) está no `docs/fechamento-integrador.md:107`.

## Ferramentas
- `python3 -I tests/test_fechar_corte.py`: 29 testes, OK.
- `bin/forge-mutante` na spec nova: M17 morreu. As specs anteriores (M1 a M16) não mudaram de trecho neste delta.
- `shellcheck` ausente no PATH: fica com o CI.

## Parecer
Aprovado no head 8e814a73. O delta corrige os dois bloqueantes e trata os dois recomendados sem mudar o comportamento já revisado: a única linha de código mudada é o texto da mensagem do `die`.
