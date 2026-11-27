---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: 04b508f60417897819537305b78a9e4db5258971
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E34.7, F4 do estudo de atrito, PR #931), volta 1

Revalidação por delta (H3) no `04b508f6`. Delta lido: `forge-check parecer delta docs/reviews/v0481-f4-vigia-fluxo.md`, intervalo `8d755e50..04b508f6`, 19 arquivos no domínio (`bin/forge-check`, `bin/forge_estado.py`, `hooks/vigia.py`, ADR 0003, `docs/hooks.md`, changelog, `tests/apoio_time_parado.py`, a fixture renomeada, as 7 specs `v0481-f4-vigia-fluxo*.json`, `tests/test_hook_vigia_f4.py`, `tests/test_hooks.py`, `tests/test_proximo.py`).

Achados da 1ª rodada (`8d755e50`):
- A1 resolvido: o `vigia` não chama mais o `gh` (sai o `subprocess`); lê `prs-abertos.json` em disco, gravado pelo `forge-check status` e pelo `proximo`. Emenda do item 7 da ADR 0003 com reversão, título do PR com `[afrouxa-regra: ADR 0003 item 7]` e o rótulo `afrouxa-regra` aplicado.
- A2 resolvido: formato fixo das três partes, até 3 PRs e 1 preso com ` e mais <M>`, teto de 280 com corte da última parte inteira (`hooks/vigia.py:712`); a regex do laço das fixtures sai de `tests/apoio_time_parado.py` e confere o teto.
- A3 resolvido: `forge-mutante --cobertura --base 2bdf1a2e` sai 0, a guarda apagada fica `isenta` com motivo (o M3 de `v0480-vigia-time-parado.json` cobre a linha nova).
- A4 resolvido: `docs/hooks.md:87` e o item 7 da ADR 0003 descrevem a condição com agente rodando, a lista em disco e o teto.
- A5 segue como cartão depois do merge; A6 perdeu o objeto (o hook não chama mais o `gh`).

Tamanho: `teto: excedido, 183 linhas` no PR, com motivo (o gravador da lista é condição do A1: sem ele o F4 sai sem efeito). Aceito.

## Achados
- A7 (bloqueante) bin/forge_estado.py:84 · `papel_do_pr` copia as linhas 63 e 66 de `grupo_do_pr` (aqui e na :97): M7 e M8 de tests/mutantes/v0481-s1-status.json casam 2 vezes e o CI do head fica vermelho (suíte 4/5, tests/test_forge_mutante.py:1564). Alinhe as duas specs no mesmo commit ou tire a duplicação
- A8 (bloqueante) bin/forge_estado.py:118 · a gravação da lista não apanha OSError: pasta de estado sem escrita (sandbox, disco cheio) derruba o `forge-check status`, cujo contrato é `nunca erro: rc 0` (só apanha NaoVerificavel), e o `proximo` depois da saída, contra o `falha não muda nada` da linha 123 (S1). Cale o OSError na gravação

## Sondas
- S1 · python3 -I sonda_grava.py <cópia> /root/.claude/plugins (`gravar_prs_abertos` com 1 PR, pasta existente e sem escrita no sandbox) · espera: nada sobe ao chamador (a lista não muda) · obtido: `OSError: [Errno 30] Read-only file system: '/root/.claude/plugins/prs-abertos.json.3.tmp'`

## Verificações
- CI do PR no `04b508f60417897819537305b78a9e4db5258971` (`gh pr checks 931`): suíte 1/5, 2/5, 3/5 e 5/5, verificações longas, passos, python 3.14, instalação, árvore já provada e `catraca` verdes; `suíte (python 3.12, parte 4/5)` vermelha pelo A7 (`bin/forge-mutante --conferir --todas` na cópia: `M7 · o trecho aparece 2 vezes em bin/forge_estado.py`, idem M8); `bateria` e `bateria (pareceres)` esperam os pareceres. Sem CI verde, não aprova.
- Testes afetados, à mão: `python3 -m unittest tests.test_hook_vigia_f4 tests.test_vigia_parado tests.test_proximo tests.test_forge_status_estado`, 112 testes OK em 31 s.
- Mutantes: `bin/forge-mutante` nas 7 specs `v0481-f4-vigia-fluxo*.json`, todos mortos, rc 0; `--cobertura --base 2bdf1a2e`, rc 0.
- Leitura: `ler_prs_abertos` usa a guarda do `ler_quadro`, limite de 64 KiB, janela de `gravado_em` (-60 s a 15 min) e lista positiva por item (número, head, papel); `papel_do_pr` deixa o fork fora pela dúvida (`isCrossRepository is not False`); o corte do teto nunca tira a única parte (cada parte isolada cabe em 280). O `proximo` renova só com a lista vencida, uma leitura do `gh_json`, que não levanta.

## Parecer
Reprovado. Os quatro bloqueantes da 1ª rodada estão resolvidos e a lógica nova está testada e com mutantes mortos, mas o CI do head está vermelho pela spec do S1 que a cópia das linhas quebrou (A7) e a gravação nova pode derrubar o `forge-check status` e o `proximo` com a pasta de estado sem escrita (A8). As duas correções são pequenas e locais; na volta, leio só o delta.
