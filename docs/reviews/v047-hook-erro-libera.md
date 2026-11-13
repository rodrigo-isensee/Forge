---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-hook-erro-libera
commit: 9e3f57c66510ceff571fd59e3153b145b8d58e6b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 · HOOK-ERRO-LIBERA (E3.16)

Head revisado 9e3f57c6 (merge da develop c5aa70e1 sobre a série de commits da E3.7 e E3.11). Classe C, instância que não fez a entrega.

## Achados
- A1 (recomendado) hooks/conformidade.py:730 · `os.path.expanduser` segue solto em conformidade.py:730 e :2452 e em parecer.py:473 e :829; não lança, mas a C1 pede função única e o teste só barra `.expanduser()` literal. Unificar em `expandir_home` na próxima passada.
- A2 (recomendado) hooks/_comum.py:2744 · `barrar_sem_versao` também usa `marcado`, agora ampliado: sem `.forge/versao`, a escrita que cita caminho da política ou tem alvo opaco passa a recusar (R-CONFORMIDADE). Coerente com a intenção, mas fora do texto das ADRs 0003 e 0009; dizer no corpo do PR.
- A3 (recomendado) hooks/_comum.py:2785 · a C5 exige no corpo do PR a medida das linhas de prazo vencido do `erros.log` da cópia principal que passariam a recusar; não há no branch. Levar ao PR, número medido.

## Sondas

## Parecer
Aprovado. Condições conferidas no código e nos testes:
- C1: `expandir_home` em `_comum.py:94` e uso nos 4 pontos de `Path(...).expanduser()` de `conformidade.py` (:881, :976, :2121, :2376); zero `.expanduser()` literal em `hooks/*.py`, com teste estrutural (A1 é o resíduo de `os.path`).
- C2 e C3: `termos_da_politica` monta os termos do JSON real (sem barra final, `~/` em quatro formas mais o home real, `*` como `[^/\s]*`); `ESCREVE_NA_LINHA` é a união pedida; política ilegível ou sem `caminhos` marca tudo; `ALVO_OPACO` cobre `$`, crase e `<(`. O teste gera `cp x <entrada>` de cada uma das 48 entradas.
- C4: `arquivo_marcado` resolve o caminho (link, `..`, `~`) contra a raiz da sessão ou a política; caminho vazio marca; coberto por teste e fixtures de Write/Edit.
- C5: `prazo_vencido` passa pelo mesmo `marcado`; `marcado` captura `Exception` e marca (falha fecha). Fixtures `errointerno-prazo-*`. Medida em A3.
- C6: `-s -E` nas 18 entradas do `hooks.json`, com teste estrutural e sonda E7 (`usercustomize` e `sitecustomize` com `os._exit(0)`; com a linha do hooks.json rc 2, sem as opções rc 0). A catraca ajustada ignora opções antes do script, e trocar o script ainda conta como remoção.
- C7: `conferir_brief` roda antes do estado, com `try` que recusa em qualquer exceção; a liberação de agente morto grava antes da recusa; `SystemExit` do `bloquear` não é engolido. Fixtures do `agentes` (estado corrompido, clone sem estado, selo, forma, hash).
- C8: ADR 0003 (item 4), ADR 0009 (seção 7), `docs/hooks.md` e docstring de `registrar_erro` atualizados no mesmo branch (E3.11: cada mudança em `_comum.py`, `agentes.py` e ADRs vem de C5, C7 ou C8).

Teto M14: 432 linhas de código e teste (`git diff --numstat --no-renames origin/develop...HEAD` nos caminhos que contam), acima das 150; uma classe só (falha fechada do hook por erro e prazo), com corpus próprio. O corpo do PR precisa de `teto: excedido, 432 linhas, <motivo>`.

Provas rodadas por mim: `tests/test_hook_erro_libera.py` com 11 testes, OK (35 s); `bin/forge-mutante` nas 5 specs (`v047-hook-erro-libera.json` e `-2` a `-5`): todos os mutantes morreram, nenhum sobrevivente (M3, M4, M15, M20 e M23 morrem por erro do teste declarado, não por asserção). Sem PR aberto, não há CI a citar; a suíte inteira fica para o CI do PR.
