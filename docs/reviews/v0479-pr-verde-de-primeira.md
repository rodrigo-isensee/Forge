---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pr-verde-de-primeira
commit: 221d50ac5ef9a04d290e7e79b11bfa0a6833cfa2
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E54.8, desenho do PR-VERDE-DE-PRIMEIRA)

Diff contra a base 5ccac0bf: `docs/propostas/v0479-pr-verde-de-primeira.md` (106 linhas) e `changelog.d/v0479-pr-verde-de-primeira.md`. Só texto, nenhum código, workflow ou hook; classe T. Suíte não rodada (só documento; o CI do PR a roda).

## Achados
- A1 (recomendado) docs/propostas/v0479-pr-verde-de-primeira.md:13 · `tests/catraca.py:1104` aponta a linha em branco antes de `rotulo_do_dono` (1105); idem `.githooks/pre-push:338` (a função está em 339, linha 15) e `tests/test_forge.py:7237` (o teste está em 7238, linha 16). Apontar a linha da definição.
- A2 (recomendado) docs/propostas/v0479-pr-verde-de-primeira.md:24 · A condição do dono de 20/11 13:51 sobre D1 (arquivo gravado só pelo dono ou pela ferramenta, nunca por agente, com teste de agente recusado e confirmação escrita da segurança) não está no texto do PV-A nem nos casos de abuso do A3; levar ao cartão do A3.

## Sondas

## Parecer
Aprovado. Faz o que a etapa pede (desenho do PR-VERDE com PV-A a PV-D, ordem do dono de 20/11 10:41) e cobre as quatro frentes da ordem. Referências conferidas na base: `rotulo_liberado` (`tests/catraca.py:1115`), `rotulo_vale_pelo_conteudo` e `protegidos_como_no_rotulo` (`:1209`, `:1195`), `primeira_rodada` (`bin/forge-placar:613`), comentário do índice (`scripts/indice-forge.py:8`), jobs `partes-doze` e `partes-quatorze` no CI, `scripts/pesos-do-ci.py` e os oráculos `tests.test_catraca`, `tests.test_testes_tocados` e `tests.test_selo_e_entrega` existentes; a ausência de `test_autorizacao_gravar` e `test_conformidade_autorizacao` está declarada na linha 103. Mecanismos novos trazem "Por que o existente não basta" com evidência (seção 3) e há critério de reversão medido (seção 6), como pede `R-DECISAO`. Corte com teto de 150 linhas por item (H1) e trilhas por arquivo explícitas. A alternativa recusada que afrouxaria o portão (catraca neutra) está recusada pelo `R-CONFORMIDADE`; B-b recusada pelo gatilho de `R-SEGURANCA`. Neutro (`R-NEUTRO`): comandos dos projetos vêm do `pronto.md` da stack. Ferramenta: `bin/forge-changelog conferir --base 5ccac0bf` deu "ok: 1 fragmento(s) novo(s)". Os dois achados são de texto e não devolvem (`R-REVIEW`).
